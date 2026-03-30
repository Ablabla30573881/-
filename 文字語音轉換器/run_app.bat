@echo off
setlocal
chcp 65001 >nul
title 文字語音轉換器 (Text-to-Speech Converter)

if not exist ".venv\Scripts\python.exe" (
    echo [系統提示] 找不到虛擬環境！
    echo 第一次使用前，請先雙擊執行 "setup.bat" 來進行環境設定與安裝必要套件。
    echo.
    pause
    exit /b
)

echo 正在啟動應用程式，請稍候...
echo -----------------------------------
.venv\Scripts\python.exe main.py
if errorlevel 1 (
    echo.
    echo [系統提示] 應用程式意外關閉或發生錯誤。
    pause
)
