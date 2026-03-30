@echo off
setlocal
chcp 65001 >nul
title 環境安裝設定 (Setup)

echo 歡迎使用文字語音轉換器安裝程式！
echo =========================================
echo [1/3] 檢查 Python 環境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python！請確認您的電腦已安裝 Python 3.10 或以上版本。
    echo 並且在安裝時有勾選 "Add Python to PATH" (加入環境變數)。
    echo 請安裝 Python 後再重新執行此檔案。
    pause
    exit /b
)

echo.
echo [2/3] 建立/檢查虛擬環境...
if not exist ".venv" (
    echo 正在建立虛擬環境...
    python -m venv .venv
    if errorlevel 1 (
        echo [錯誤] 虛擬環境建立失敗！
        pause
        exit /b
    )
) else (
    echo 虛擬環境 (.venv) 已存在，跳過建立。
)

echo.
echo [3/3] 安裝與更新必要套件...
echo 正在準備環境 (更新 pip)...
.venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1

echo 正在安裝必要套件與深度學習模型 (這可能需要一段時間，請耐心等候)...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo [錯誤] 套件安裝過程中發生錯誤，請檢查網路連線或儲存空間。
    pause
    exit /b
)

echo.
echo =========================================
echo 安裝完成！正在驗證 GPU 支援狀態...
.venv\Scripts\python.exe -c "import torch; print('CUDA (GPU) 是否可用:', torch.cuda.is_available()); print('偵測到的 GPU 數量:', torch.cuda.device_count())"

echo.
echo 恭喜！環境設定已全部完成。
echo 以後您只需要直接點擊 [ run_app.bat ] 即可啟動程式！
pause
