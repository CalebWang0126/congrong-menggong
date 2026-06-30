@echo off
setlocal enabledelayedexpansion
title 从容猛攻助手

:: Switch to UTF-8 for Chinese character display (safe to skip if unsupported)
chcp 65001 >nul 2>&1

:: ──────────────────────────────────────────
::  从容猛攻助手 — 一键启动器
:: ──────────────────────────────────────────

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo.
echo   +====================================+
echo   |     从容猛攻助手                   |
echo   |     CongRong MengGong ZhuShou      |
echo   +====================================+
echo.

:: ── 1. Check Python ──────────────────────
echo   [1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [FAIL] Python not found!
    echo   Please install Python 3.11+ from https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during install
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo   [OK] Python %PYVER%

:: ── 2. Check/Create venv ─────────────────
echo.
echo   [2/3] Preparing virtual environment...

if not exist ".venv\Scripts\python.exe" (
    echo   Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo   [FAIL] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo   [OK] Virtual environment created
) else (
    echo   [OK] Virtual environment ready
)

:: ── 3. Install dependencies ──────────────
echo.
echo   [3/3] Checking dependencies...

set "NEED_INSTALL=0"
.venv\Scripts\python.exe -c "import uiautomation" 2>nul || set "NEED_INSTALL=1"
.venv\Scripts\python.exe -c "import nicegui" 2>nul || set "NEED_INSTALL=1"
.venv\Scripts\python.exe -c "import mss" 2>nul || set "NEED_INSTALL=1"
.venv\Scripts\python.exe -c "import webview" 2>nul || set "NEED_INSTALL=1"

if "!NEED_INSTALL!"=="1" (
    echo   Installing dependencies (first run takes 1-2 minutes)...
    .venv\Scripts\python.exe -m pip install -r requirements.txt -q
    if !errorlevel! neq 0 (
        echo   [FAIL] Dependency install failed! Check your network and retry.
        pause
        exit /b 1
    )
    echo   [OK] Dependencies installed
) else (
    echo   [OK] Dependencies ready
)

:: ── Launch ───────────────────────────────
echo.
echo   =====================================
echo     Starting...
echo     If WeChat is not open, launch WeChat
echo     and log in first, then click
echo     [Start Monitoring] in this tool
echo   =====================================
echo.

.venv\Scripts\python.exe -m src.main

if %errorlevel% neq 0 (
    echo.
    echo   [FAIL] Program exited abnormally (code: %errorlevel%)
    echo   Check the log output above for details
)
echo.
echo   Program exited.
pause
