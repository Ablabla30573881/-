import sys
import os

# Ensure the root directory and src directory are in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
# --- FFmpeg / TorchAudio Fix ---
import os
import sys

# Attempt to mount imageio-ffmpeg
try:
    import imageio_ffmpeg
    ffmpeg_path = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
    if ffmpeg_path not in os.environ["PATH"]:
        os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]
except ImportError:
    pass

# Patch torchaudio to avoid torchcodec crash
try:
    import torchaudio
    import soundfile as sf
    import torch
    
    def patched_load(filepath, **kwargs):
        # Use soundfile to load and convert to tensor to skip ffmpeg/torchcodec logic
        data, samplerate = sf.read(filepath)
        # Convert to [channels, frames]
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        else:
            data = data.T
        return torch.from_numpy(data.astype("float32")), samplerate

    # Force monkeypatch
    torchaudio.load = patched_load
    print("Applied torchaudio.load monkeypatch to skip torchcodec.")
except Exception as e:
    print(f"Warning: Could not patch torchaudio: {e}")

# --- End Fix ---

# Ensure the root directory and src directory are in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from src.ui.desktop_ui import DesktopUI as AppUI
except ImportError:
    # Try web UI if desktop is not ready
    from src.ui.web_ui import WebUI as AppUI
except ImportError:
    # Fallback if src is already in path
    from ui.web_ui import WebUI

if __name__ == "__main__":
    ui = AppUI()
    if hasattr(ui, "launch"):
        ui.launch()
    else:
        ui.mainloop()
