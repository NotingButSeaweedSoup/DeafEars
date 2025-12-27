@echo off
chcp 65001 >nul
title 你尔多🐉吗 - 语音转文本系统启动器

echo 正在启动你尔多🐉吗语音转文本系统...
echo.

REM 设置FFmpeg相对路径
set "FFMPEG_PATH=%~dp0ffmpeg\ffmpeg-master-latest-win64-gpl\bin"
if exist "%FFMPEG_PATH%\ffmpeg.exe" (
    echo ✓ 设置FFmpeg路径: %FFMPEG_PATH%
    set "PATH=%FFMPEG_PATH%;%PATH%"
) else (
    echo ================================================
    echo ⚠️  重要提醒: 未找到FFmpeg
    echo    FFmpeg是处理MP3等音频格式的必需组件
    echo    没有FFmpeg可能导致转录失败
    echo.
    echo    解决方案:
    echo    1. 运行: python install_ffmpeg.py
    echo    2. 或手动下载: https://ffmpeg.org/download.html
    echo ================================================
    echo.
    set /p choice="是否继续启动? (y/N): "
    if /i not "%choice%"=="y" (
        echo 启动已取消
        pause
        exit /b
    )
)

REM 激活虚拟环境（如果存在）
if exist ".venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
)

REM 运行启动脚本
python start.py

echo.
echo 按任意键退出...
pause >nul