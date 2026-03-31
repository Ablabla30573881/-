import gradio as gr
import os
import glob
from src.core.tts_processor import TTSProcessor

def get_all_audio_files():
    # Look in both directories
    raw_files = glob.glob("data/raw/*.wav") + glob.glob("data/raw/*.mp3")
    proc_files = glob.glob("data/processed/*.wav") + glob.glob("data/processed/*.mp3")
    
    # Return mapping of display name to full path
    mapping = {}
    for f in raw_files:
        mapping[f"[Raw] {os.path.basename(f)}"] = f
    for f in proc_files:
        mapping[f"[Processed] {os.path.basename(f)}"] = f
    return mapping

class WebUI:
    def __init__(self):
        self.processor = None
        self.processed_dir = "data/processed"
        
    def lazy_load_engine(self):
        if self.processor is None:
            self.processor = TTSProcessor()
        return self.processor

    def predict(self, ref_display_name, gen_text, ref_text):
        audio_mapping = get_all_audio_files()
        if not ref_display_name or ref_display_name not in audio_mapping:
            return None, "請選擇參考音檔", ""
        
        ref_path = audio_mapping[ref_display_name]
        engine = self.lazy_load_engine()
        
        output_name = "output_speech.wav"
        output_path, detected_text = engine.generate(
            ref_audio=ref_path,
            gen_text=gen_text,
            ref_text=ref_text if ref_text.strip() else None,
            output_path=output_name
        )
        
        return output_path, f"成功生成！參考文字：{detected_text}", detected_text

    def refresh_list(self):
        mapping = get_all_audio_files()
        return gr.Dropdown(choices=list(mapping.keys()))

    def launch(self):
        mapping = get_all_audio_files()
        with gr.Blocks(title="AI 文字語音轉換器") as demo:
            gr.Markdown("# 🎙️ AI 文字語音轉換器 (F5-TTS)")
            gr.Markdown("這是一個從零開始建立的語音克隆系統。您可以直接選擇 `data/raw` 中的音檔。")
            
            with gr.Row():
                with gr.Column():
                    ref_audio_list = gr.Dropdown(
                        label="選擇參考音檔", 
                        choices=list(mapping.keys())
                    )
                    refresh_btn = gr.Button("重新整理清單")
                    
                    gen_text = gr.Textbox(
                        label="要轉換的文字", 
                        placeholder="請輸入您想讓 AI 說的話...",
                        lines=5
                    )
                    
                    ref_text_input = gr.Textbox(
                        label="參考音檔的內容 (不填則自動轉錄)", 
                        placeholder="選填，手動輸入可提高品質"
                    )
                    
                    submit_btn = gr.Button("開始轉換", variant="primary")
                    
                with gr.Column():
                    output_audio = gr.Audio(label="輸出的語音")
                    info_text = gr.Textbox(label="狀態訊息", interactive=False)
                    detected_ref_text = gr.Textbox(label="自動識別的參考文字", interactive=False)

            # Events
            submit_btn.click(
                fn=self.predict,
                inputs=[ref_audio_list, gen_text, ref_text_input],
                outputs=[output_audio, info_text, detected_ref_text]
            )
            
            refresh_btn.click(
                fn=self.refresh_list,
                inputs=[],
                outputs=[ref_audio_list]
            )
            
        demo.launch(inbrowser=True, server_port=7861)

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("data/processed", exist_ok=True)
    ui = WebUI()
    ui.launch()
