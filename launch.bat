@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title 从容猛攻助手

:: ──────────────────────────────────────────
::  从容猛攻助手 — 一键启动器
:: ──────────────────────────────────────────

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo.
echo   ╔══════════════════════════════════╗
echo   ║     🎮 从容猛攻助手             ║
echo   ║     CongRong MengGong ZhuShou   ║
echo   ╚══════════════════════════════════╝
echo.

:: ── 1. 检查 Python ──────────────────────
echo   [1/3] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ 未找到 Python！
    echo   请先安装 Python 3.11+：https://www.python.org/downloads/
    echo   安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo   ✅ Python %PYVER%

:: ── 2. 检查/创建虚拟环境 ────────────────
echo.
echo   [2/3] 准备虚拟环境...

if not exist ".venv\Scripts\python.exe" (
    echo   正在创建虚拟环境...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo   ❌ 创建虚拟环境失败！
        pause
        exit /b 1
    )
    echo   ✅ 虚拟环境已创建
) else (
    echo   ✅ 虚拟环境已就绪
)

:: ── 3. 安装依赖 ─────────────────────────
echo.
echo   [3/3] 检查依赖...

set "NEED_INSTALL=0"
.venv\Scripts\python.exe -c "import uiautomation" 2>nul || set "NEED_INSTALL=1"
.venv\Scripts\python.exe -c "import nicegui" 2>nul || set "NEED_INSTALL=1"
.venv\Scripts\python.exe -c "import mss" 2>nul || set "NEED_INSTALL=1"

if "!NEED_INSTALL!"=="1" (
    echo   正在安装依赖（首次运行需要 1-2 分钟）...
    .venv\Scripts\python.exe -m pip install -r requirements.txt -q
    if %errorlevel% neq 0 (
        echo   ❌ 依赖安装失败！请检查网络连接后重试。
        pause
        exit /b 1
    )
    echo   ✅ 依赖安装完成
) else (
    echo   ✅ 依赖已就绪
)

:: ── 启动 ────────────────────────────────
echo.
echo   ═══════════════════════════════════
echo     🟢 正在启动...
echo     如果微信未打开，启动后请先登录微信
echo     然后在本工具中点击「开始监听」
echo   ═══════════════════════════════════
echo.

.venv\Scripts\python.exe -m src.main

if %errorlevel% neq 0 (
    echo.
    echo   ❌ 程序异常退出（错误码: %errorlevel%）
    echo   请查看上方日志排查问题
    pause
)
