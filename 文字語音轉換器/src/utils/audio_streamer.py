try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False

import numpy as np
import threading
import queue

class AudioStreamer:
    def __init__(self):
        if not HAS_PYAUDIO:
            raise ImportError("pyaudio is not installed. Please run setup.bat.")
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.chunk_size = 1024
        self.rate = 16000
        self.channels = 1
        self.format = pyaudio.paInt16

    def get_devices(self):
        if not HAS_PYAUDIO: return []
        devices = []
        for i in range(self.p.get_device_count()):
            try:
                info = self.p.get_device_info_by_index(i)
                devices.append({
                    "index": i,
                    "name": info["name"],
                    "maxInputChannels": info["maxInputChannels"],
                    "maxOutputChannels": info["maxOutputChannels"]
                })
            except:
                continue
        return devices

    def list_input_devices(self):
        return [f"{d['index']}: {d['name']}" for d in self.get_devices() if d["maxInputChannels"] > 0]

    def list_output_devices(self):
        return [f"{d['index']}: {d['name']}" for d in self.get_devices() if d["maxOutputChannels"] > 0]

    def start_recording(self, input_device_index, chunk_callback):
        if not HAS_PYAUDIO: return
        self.is_running = True
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=self.chunk_size
        )
        
        def record_loop():
            while self.is_running:
                try:
                    data = self.stream.read(self.chunk_size)
                    chunk_callback(data)
                except:
                    break
                
        self.thread = threading.Thread(target=record_loop)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None

    def __del__(self):
        if HAS_PYAUDIO:
            self.p.terminate()
