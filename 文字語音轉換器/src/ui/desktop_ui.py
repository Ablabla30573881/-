import customtkinter as ctk
import os
import glob
import threading
import pygame
from src.core.tts_processor import TTSProcessor

# Initialize pygame mixer for audio playback
pygame.mixer.init()

def get_all_audio_files():
    raw_files = glob.glob("data/raw/*.wav") + glob.glob("data/raw/*.mp3")
    proc_files = glob.glob("data/processed/*.wav") + glob.glob("data/processed/*.mp3")
    mapping = {}
    for f in raw_files:
        mapping[f"[Raw] {os.path.basename(f)}"] = f
    for f in proc_files:
        mapping[f"[Processed] {os.path.basename(f)}"] = f
    return mapping

class DesktopUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # UI State
        self.processor = None
        self.audio_mapping = get_all_audio_files()
        self.output_path = None
        self.streamer = None

        # Create TabView
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.tabview.add("文字轉語音")
        self.tabview.add("及時變聲器")

        # --- Tab 1: TTS ---
        self.setup_tts_tab()

        # --- Tab 2: Changer ---
        self.setup_changer_tab()

    def setup_tts_tab(self):
        parent = self.tabview.tab("文字轉語音")
        parent.grid_columnconfigure(0, weight=1)
        
        # Main container
        self.main_frame = ctk.CTkFrame(parent)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.label_title = ctk.CTkLabel(self.main_frame, text="🎙️ AI 文字語音轉換器", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, pady=(0, 20))

        # Dropdown for reference audio
        self.label_ref = ctk.CTkLabel(self.main_frame, text="1. 選擇參考音檔:")
        self.label_ref.grid(row=1, column=0, sticky="w", padx=20)
        
        # Re-fetch mapping
        self.audio_mapping = get_all_audio_files()
        self.ref_dropdown = ctk.CTkComboBox(self.main_frame, values=list(self.audio_mapping.keys()), width=400)
        self.ref_dropdown.grid(row=2, column=0, pady=(5, 15), padx=20, sticky="ew")

        # Text input for generation
        self.label_gen = ctk.CTkLabel(self.main_frame, text="2. 輸入要轉換的文字:")
        self.label_gen.grid(row=3, column=0, sticky="w", padx=20)
        
        self.text_input = ctk.CTkTextbox(self.main_frame, height=100)
        self.text_input.grid(row=4, column=0, pady=(5, 15), padx=20, sticky="ew")
        self.text_input.insert("0.0", "你好，這是一個測試。")

        # Ref text input (optional)
        self.label_ref_text = ctk.CTkLabel(self.main_frame, text="3. 參考文字 (選填):")
        self.label_ref_text.grid(row=5, column=0, sticky="w", padx=20)
        
        self.ref_text_input = ctk.CTkEntry(self.main_frame, placeholder_text="不填則自動識別")
        self.ref_text_input.grid(row=6, column=0, pady=(5, 10), padx=20, sticky="ew")

        # Parameters Slider Frame
        self.param_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.param_frame.grid(row=7, column=0, pady=5, padx=20, sticky="ew")
        self.param_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.param_frame, text="情感起伏 (CFG):").grid(row=0, column=0, padx=(0,10))
        self.cfg_slider = ctk.CTkSlider(self.param_frame, from_=0.1, to=5.0, number_of_steps=49)
        self.cfg_slider.set(2.0)
        self.cfg_slider.grid(row=0, column=1, sticky="ew")
        
        ctk.CTkLabel(self.param_frame, text="細膩程度 (Steps):").grid(row=1, column=0, padx=(0,10))
        self.steps_slider = ctk.CTkSlider(self.param_frame, from_=16, to=128, number_of_steps=28)
        self.steps_slider.set(32)
        self.steps_slider.grid(row=1, column=1, sticky="ew")

        ctk.CTkLabel(self.param_frame, text="語速 (Speed):").grid(row=2, column=0, padx=(0,10))
        self.speed_slider = ctk.CTkSlider(self.param_frame, from_=0.5, to=2.0, number_of_steps=30)
        self.speed_slider.set(1.0)
        self.speed_slider.grid(row=2, column=1, sticky="ew")

        ctk.CTkLabel(self.param_frame, text="生動紋理 (Sway):").grid(row=3, column=0, padx=(0,10))
        self.sway_slider = ctk.CTkSlider(self.param_frame, from_=-0.2, to=0.5, number_of_steps=35)
        self.sway_slider.set(0.0)
        self.sway_slider.grid(row=3, column=1, sticky="ew")

        # Logic Tip
        tip_text = "💡 提示：在文字中加入 '...' 或 '！' 可以讓語氣更生動！"
        ctk.CTkLabel(self.main_frame, text=tip_text, text_color="cyan", font=ctk.CTkFont(size=12)).grid(row=8, column=0, pady=2)

        # Buttons
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.grid(row=9, column=0, pady=5)

        self.generate_btn = ctk.CTkButton(self.btn_frame, text="開始轉換", command=self.start_generation, width=120)
        self.generate_btn.grid(row=0, column=0, padx=10)

        self.play_btn = ctk.CTkButton(self.btn_frame, text="播放", command=self.play_audio, state="disabled", width=120)
        self.play_btn.grid(row=0, column=1, padx=10)

        self.status_label = ctk.CTkLabel(self.main_frame, text="狀態: 就緒", text_color="gray")
        self.status_label.grid(row=10, column=0, pady=5)

        self.log_area = ctk.CTkTextbox(self.main_frame, height=60, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_area.grid(row=11, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.log_area.configure(state="disabled")

    def setup_changer_tab(self):
        parent = self.tabview.tab("及時變聲器")
        parent.grid_columnconfigure(0, weight=1)
        
        self.changer_frame = ctk.CTkFrame(parent)
        self.changer_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.changer_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.changer_frame, text="🔁 及時語音轉換 (變聲器)", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)

        # Device selection with safety check
        try:
            from src.utils.audio_streamer import AudioStreamer
            if self.streamer is None:
                self.streamer = AudioStreamer()
            inputs = self.streamer.list_input_devices()
            outputs = self.streamer.list_output_devices()
            has_pyaudio = True
        except Exception as e:
            self.log(f"變聲器啟動失敗 (缺少 pyaudio): {e}")
            inputs = ["請先執行 setup.bat 安裝依賴"]
            outputs = ["請先執行 setup.bat 安裝依賴"]
            has_pyaudio = False

        ctk.CTkLabel(self.changer_frame, text="輸入裝置:").grid(row=1, column=0, sticky="w", padx=20)
        self.input_select = ctk.CTkComboBox(self.changer_frame, values=inputs, width=400)
        self.input_select.grid(row=2, column=0, pady=5, padx=20, sticky="ew")

        ctk.CTkLabel(self.changer_frame, text="輸出音色 (參考音檔):").grid(row=3, column=0, sticky="w", padx=20)
        self.changer_ref_dropdown = ctk.CTkComboBox(self.changer_frame, values=list(self.audio_mapping.keys()), width=400)
        self.changer_ref_dropdown.grid(row=4, column=0, pady=5, padx=20, sticky="ew")

        # Changer params
        self.changer_cfg_label = ctk.CTkLabel(self.changer_frame, text="情感倍率 (CFG=2.0)")
        self.changer_cfg_label.grid(row=5, column=0, pady=(5,0))
        self.changer_cfg_slider = ctk.CTkSlider(self.changer_frame, from_=1.0, to=4.0, command=lambda v: self.changer_cfg_label.configure(text=f"情感倍率 (CFG={v:.1f})"))
        self.changer_cfg_slider.set(2.0)
        self.changer_cfg_slider.grid(row=6, column=0, padx=20, sticky="ew")

        self.start_changer_btn = ctk.CTkButton(self.changer_frame, text="啟動變聲器", command=self.toggle_changer, fg_color="green")
        self.start_changer_btn.grid(row=7, column=0, pady=20)

        self.changer_status = ctk.CTkLabel(self.changer_frame, text="狀態: 停止", text_color="gray")
        self.changer_status.grid(row=6, column=0)
        
        self.is_changer_running = False

    def toggle_changer(self):
        if not self.is_changer_running:
            self.start_changer()
        else:
            self.stop_changer()

    def start_changer(self):
        ref_display = self.changer_ref_dropdown.get()
        if not ref_display:
            return
        
        self.is_changer_running = True
        self.start_changer_btn.configure(text="停止變聲器", fg_color="red")
        self.changer_status.configure(text="狀態: 執行中 (監聽麥克風...)", text_color="green")
        
        # Start a recording thread that processes chunks
        # This is a simplified version: record 5s, transcribe, then TTS
        self.log("啟動變聲器監聽...")
        threading.Thread(target=self.changer_loop, args=(ref_display,)).start()

    def changer_loop(self, ref_display):
        import time
        import soundfile as sf
        import tempfile
        import numpy as np
        
        chunk_duration = 3  # Seconds per chunk
        self.log(f"及時變聲器已啟動，每 {chunk_duration} 秒進行一次轉換...")
        
        while self.is_changer_running:
            try:
                # 1. Capture audio from mic (Pseudo-streaming using short recordings)
                self.changer_status.configure(text=f"狀態: 正在錄音 ({chunk_duration}s)...")
                
                # We reuse the streamer if we can, or just use a simple recording
                import sounddevice as sd
                fs = 16000
                # Get selected device index from combobox
                try:
                    dev_idx = int(self.input_select.get().split(":")[0])
                except:
                    dev_idx = None
                
                recording = sd.rec(int(chunk_duration * fs), samplerate=fs, channels=1, device=dev_idx)
                sd.wait()
                
                if not self.is_changer_running: break
                
                self.changer_status.configure(text="狀態: 正在識別與轉換...")
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    temp_in = tf.name
                sf.write(temp_in, recording, fs)
                
                # 2. Transcribe and Generate
                ref_path = self.audio_mapping[ref_display]
                engine = self.lazy_load_engine()
                
                # Recognize text from mic
                input_text = engine.transcribe(temp_in)
                if len(input_text.strip()) < 1:
                    continue
                
                self.log(f"識別到: {input_text}")
                
                # Convert to target voice
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    temp_out = tf.name
                
                engine.generate(
                    ref_audio=ref_path,
                    gen_text=input_text,
                    output_path=temp_out,
                    nfe_step=16, # Fixed lower steps for real-time speed
                    cfg_strength=float(self.changer_cfg_slider.get())
                )
                
                # 3. Play back
                self.changer_status.configure(text="狀態: 播放中...")
                pygame.mixer.music.load(temp_out)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    if not self.is_changer_running: break
                    time.sleep(0.1)
                
                # Cleanup
                os.unlink(temp_in)
                os.unlink(temp_out)
                
            except Exception as e:
                self.log(f"變聲循環錯誤: {e}")
                time.sleep(1)

    def stop_changer(self):
        self.is_changer_running = False
        self.start_changer_btn.configure(text="啟動變聲器", fg_color="green")
        self.changer_status.configure(text="狀態: 停止", text_color="gray")

    def log(self, text):
        self.log_area.configure(state="normal")
        self.log_area.insert("end", f"> {text}\n")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")

    def lazy_load_engine(self):
        if self.processor is None:
            self.status_label.configure(text="狀態: 正在載入模型 (初次執行較久)...", text_color="orange")
            self.log("正在初始化 F5-TTS 引擎...")
            self.processor = TTSProcessor()
            self.log("初始化完成。")
        return self.processor

    def start_generation(self):
        ref_display = self.ref_dropdown.get()
        if not ref_display:
            self.log("錯誤: 請先選擇參考音檔。")
            return

        self.generate_btn.configure(state="disabled")
        self.status_label.configure(text="狀態: 正在轉換中...", text_color="orange")
        
        # Run in thread to keep UI responsive
        thread = threading.Thread(target=self.run_generation, args=(ref_display,))
        thread.start()

    def run_generation(self, ref_display):
        try:
            # Prevent file lock by unloading music
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except:
                pass
                
            gen_text = self.text_input.get("0.0", "end").strip()
            ref_text = self.ref_text_input.get().strip()
            ref_path = self.audio_mapping[ref_display]
            
            engine = self.lazy_load_engine()
            
            self.log(f"使用音檔: {ref_display}")
            # Use a simpler output name or timestamp to avoid cache/lock issues
            import time
            timestamp = int(time.time())
            output_name = f"result_{timestamp}.wav"
            
            self.output_path, detected_text = engine.generate(
                ref_audio=ref_path,
                gen_text=gen_text,
                ref_text=ref_text if ref_text else None,
                output_path=output_name,
                nfe_step=int(self.steps_slider.get()),
                cfg_strength=float(self.cfg_slider.get()),
                speed=float(self.speed_slider.get()),
                sway_sampling_coef=float(self.sway_slider.get())
            )
            
            self.log(f"轉換成功！參考文字 identificación: {detected_text}")
            self.status_label.configure(text="狀態: 轉換完成！", text_color="green")
            self.play_btn.configure(state="normal")
            
        except Exception as e:
            self.log(f"轉換失敗: {e}")
            self.status_label.configure(text="狀態: 錯誤", text_color="red")
        finally:
            self.generate_btn.configure(state="normal")

    def play_audio(self):
        if self.output_path and os.path.exists(self.output_path):
            pygame.mixer.music.load(self.output_path)
            pygame.mixer.music.play()
            self.log("正在播放...")
        else:
            self.log("找不到生成的音檔。")

if __name__ == "__main__":
    app = DesktopUI()
    app.mainloop()
