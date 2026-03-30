@echo off
setlocal
chcp 65001 >nul

echo [1/3] Checking/Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
)

echo [2/3] Installing/Updating GPU Dependencies (CUDA 12.1)...
echo This will force a reinstall to ensure CUDA support.
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo [3/3] Verify GPU installation...
.venv\Scripts\python.exe -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('Device count:', torch.cuda.device_count())"

echo.
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Installation failed. Please check your internet connection.
) else (
    echo Setup completed successfully! Now you can run run_app.bat
)
pause
