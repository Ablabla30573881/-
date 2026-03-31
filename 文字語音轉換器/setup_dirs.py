import os
import shutil

def setup():
    dirs = [
        "data/raw",
        "data/processed",
        "src/core",
        "src/ui",
        "src/utils",
        "models"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    # Move audio files from root to data/raw
    for f in os.listdir("."):
        if f.endswith((".wav", ".mp3", ".m4a", ".flac")):
            target = os.path.join("data/raw", f)
            if not os.path.exists(target):
                shutil.move(f, target)
                print(f"Moved {f} to data/raw")

if __name__ == "__main__":
    setup()
