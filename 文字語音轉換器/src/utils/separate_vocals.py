import os
import subprocess
import glob
import shutil

def separate_vocals():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    
    # Files to process
    files = glob.glob(os.path.join(raw_dir, "*.mp3")) + glob.glob(os.path.join(raw_dir, "*.wav"))
    
    for f in files:
        basename = os.path.basename(f)
        # Check if it's already processed or if it's the clean wav
        if "那裡不行" in basename:
            print(f"Skipping separation for {basename} (assumed clean)")
            shutil.copy(f, os.path.join(processed_dir, basename))
            continue
            
        print(f"Processing {basename} with Demucs...")
        # Use demucs to separate vocals
        # Note: requires demucs installed in the environment
        try:
            subprocess.run([
                "demucs", 
                "--two-stems", "vocals", 
                "-o", "tmp_demucs", 
                f
            ], check=True)
            
            # Find the vocal file and move it
            # Demucs output is usually in tmp_demucs/htdemucs/filename/vocals.wav
            filename_no_ext = os.path.splitext(basename)[0]
            vocal_path = glob.glob(f"tmp_demucs/**/{filename_no_ext}/vocals.wav", recursive=True)
            if vocal_path:
                target_path = os.path.join(processed_dir, f"{filename_no_ext}_vocals.wav")
                shutil.move(vocal_path[0], target_path)
                print(f"Successfully extracted vocals for {basename}")
            else:
                print(f"Could not find vocal output for {basename}")
        except Exception as e:
            print(f"Error processing {basename}: {e}")
            print("Fallback: Using original file (quality may be low)")
            shutil.copy(f, os.path.join(processed_dir, basename))

    # Cleanup tmp_demucs if it exists
    if os.path.exists("tmp_demucs"):
        shutil.rmtree("tmp_demucs")

if __name__ == "__main__":
    separate_vocals()
