@echo off
chcp 65001 >nul
title FFmpeg检查工具

echo ===================================
echo    FFmpeg检查工具
echo ===================================
echo.

REM 激活虚拟环境（如果存在）
if exist ".venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
)

echo 启动FFmpeg检查工具...
echo.

python check_ffmpeg.py

echo.
echo 按任意键退出...
pause >nul