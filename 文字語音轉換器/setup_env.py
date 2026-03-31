import sys
import os
import subprocess

def run_cmd(cmd_list, step_name):
    print(f"  執行指令: {step_name} ...")
    try:
        # 使用 stdout=None 繼承原本的 CMD 終端，這樣才能顯示即時進度條
        result = subprocess.run(cmd_list)
        if result.returncode != 0:
            print(f"\n[嚴重錯誤] {step_name} 執行失敗！")
            print("請檢查上方的錯誤訊息。這通常是因為缺少 C++ Build Tools 或是網路連線不穩。")
            sys.exit(1)
    except Exception as e:
        print(f"\n[系統錯誤] 無法啟動 {step_name}: {e}")
        sys.exit(1)

def main():
    # 強制將 Windows 終端機切換至 UTF-8 以正確顯示中文
    os.system("chcp 65001 >nul")
    
    print("===================================================")
    print("      文字語音轉換器 (Text-to-Speech) - 自動化安裝程式")
    print("===================================================")
    print("本程式將引導您自動完成安裝配置，讓程式可以在這台電腦上順利執行。")
    print("過程可能會需要下載依賴套件 (數 GB)，請耐心等待並確保網路連線正常。\n")

    # 1. 檢查 Python 版本
    print("[1/6] 檢查 Python 系統環境...")
    print(f"  找到 Python 版本: {sys.version.split(' ')[0]}")
    print()

    # 2. 建立或檢查虛擬環境
    print("[2/6] 檢查/建立獨立的虛擬環境 (.venv)...")
    venv_dir = ".venv"
    # Windows 環境下的 python 路徑
    venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    
    if not os.path.exists(venv_python):
        print("  開始建立全新的虛擬環境 (這可能需要幾秒鐘)...")
        run_cmd([sys.executable, "-m", "venv", venv_dir], "建立虛擬環境")
    else:
        print("  虛擬環境已存在，將繼續使用。")
    print()

    # 3. 更新 pip 與核心工具
    print("[3/6] 更新 pip 核心套件安裝工具...")
    run_cmd([venv_python, "-m", "pip", "install", "--upgrade", "pip"], "更新 pip")
    print()

    # 4. 偵測硬體並安裝對應的 PyTorch 版本
    print("[4/6] 偵測系統硬體以判斷適合的 PyTorch 加速版本...")
    has_nvidia = False
    try:
        # 測試是否能呼叫 nvidia-smi，這代表已安裝 NVIDIA 驅動程式且具有支援的顯示卡
        test_nv = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if test_nv.returncode == 0:
            has_nvidia = True
    except Exception:
        pass

    if has_nvidia:
        print("  ✅ 偵測到 NVIDIA 顯示卡！準備安裝 GPU (CUDA 12.1) 加速版 PyTorch...")
        print("  (下載 PyTorch 檔案超過 2GB，可能會花費超過 5 分鐘，請保持網路通暢並勿關閉視窗)")
        run_cmd([venv_python, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu121"], "安裝 PyTorch (GPU版)")
    else:
        print("  ⚠ 未偵測到 NVIDIA 顯示卡或相關驅動，將為您安裝「純 CPU 版本」的 PyTorch。")
        print("  (注意：沒有 GPU 加速，語音轉換速度將會較慢)")
        run_cmd([venv_python, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"], "安裝 PyTorch (CPU版)")
    print()

    # 5. 安裝需求套件
    print("[5/6] 開始下載並安裝其他相依模組...")
    run_cmd([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], "安裝需求套件")
    print()

    # 執行初次資料夾建立
    print("  初始化工作資料夾結構...")
    if os.path.exists("setup_dirs.py"):
        run_cmd([venv_python, "setup_dirs.py"], "初始化資料夾")
    print()

    # 6. 驗證 GPU
    print("[6/6] 驗證系統硬體與 CUDA 加速狀態...")
    check_gpu_code = """
import torch
print('\\n--- 系統檢測報告 ---')
print(f'PyTorch 版本: {torch.__version__}')
print(f'CUDA 是否啟用: {"是 (✅ 支援 GPU 加速)" if torch.cuda.is_available() else "否 (⚠ 僅支援純 CPU 運算，速度將大幅減緩)"}')
print(f'偵測到的顯示卡數量: {torch.cuda.device_count()}')
print('--------------------')
"""
    subprocess.run([venv_python, "-c", check_gpu_code])
    
    print("\n===================================================")
    print("  恭喜！所有環境設定已經成功完成。")
    print("  ✅ 您的環境已經準備好。")
    print("  ▶ 以後只要直接執行「run_app.bat」即可啟動轉換器。")
    print("===================================================")

if __name__ == "__main__":
    try:
        # 切換工作目錄到安裝檔所在的位置
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        main()
    except KeyboardInterrupt:
        print("\n\n[中斷] 安裝程序已被使用者手動取消。")
        sys.exit(1)
    except Exception as e:
        print(f"\n[錯誤] 發生不可預期的異常: {e}")
        sys.exit(1)
