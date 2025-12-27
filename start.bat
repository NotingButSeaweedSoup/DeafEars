@echo off
chcp 65001 >nul
title 你尔多🐉吗 - 语音转文本系统启动器

echo 正在启动你尔多🐉吗语音转文本系统...
echo.

REM 设置FFmpeg相对路径
set "FFMPEG_PATH=%~dp0ffmpeg\ffmpeg-master-latest-win64-gpl\bin"
if exist "%FFMPEG_PATH%\ffmpeg.exe" (
    echo 设置FFmpeg路径: %FFMPEG_PATH%
    set "PATH=%FFMPEG_PATH%;%PATH%"
) else (
    echo 警告: 未找到FFmpeg，MP3文件可能无法处理
    echo 提示: 运行 python install_ffmpeg.py 安装FFmpeg
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