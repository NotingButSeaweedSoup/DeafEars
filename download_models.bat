@echo off
chcp 65001 >nul
title 模型下载工具

echo ===================================
echo    Whisper模型下载工具
echo ===================================
echo.

REM 激活虚拟环境（如果存在）
if exist ".venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
)

echo 启动模型下载工具...
echo.

python download_models.py

echo.
echo 按任意键退出...
pause >nul