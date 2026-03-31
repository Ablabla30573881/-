@echo off
title Setup Installer
chcp 65001 >nul

:: Check if Python is installed
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found on your system!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo IMPORTANT: Be sure to check "Add python.exe to PATH" in the installer.
    echo.
    pause
    exit /b 1
)

:: Check if FFmpeg is installed
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo.
    echo [INFO] FFmpeg not found on your system! Attempting to auto-install via winget...
    winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to automatically install FFmpeg.
        echo Please try installing it manually via PowerShell: winget install -e --id Gyan.FFmpeg
        pause
        exit /b 1
    ) else (
        echo.
        echo [SUCCESS] FFmpeg has been installed automatically!
        echo IMPORTANT: After setup finishes, you might need to close and restart this terminal for PATH to update.
        echo.
    )
)

:: Run the python setup script
echo.
echo Starting the installer, please wait...
echo.
python "%~dp0setup_env.py"

echo.
pause
exit /b 0
