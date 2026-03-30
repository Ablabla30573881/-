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

:: Run the python setup script
echo.
echo Starting the installer, please wait...
echo.
python "%~dp0setup_env.py"

echo.
pause
exit /b 0
