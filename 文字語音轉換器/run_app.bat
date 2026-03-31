@echo off
title Text-to-Speech Application
chcp 65001 >nul

:: Switch to the directory where this script is located
cd /d "%~dp0"

echo ===================================================
echo   Starting the Text-to-Speech Application...
echo ===================================================
echo.

:: Check if the virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo It seems the application hasn't been set up yet.
    echo Please run "setup.bat" first to install everything.
    echo.
    pause
    exit /b 1
)

:: Run the main application
.venv\Scripts\python.exe main.py

:: Pause only if the application crashes (non-zero exit code)
if errorlevel 1 (
    echo.
    echo [ERROR] The application crashed or an error occurred.
    pause
    exit /b 1
)

:: Wait 3 seconds before closing gracefully if successful (optional)
timeout /t 3 >nul
exit /b 0
