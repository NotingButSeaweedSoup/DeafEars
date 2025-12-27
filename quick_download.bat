@echo off
chcp 65001 >nul
title 快速下载基础模型

echo ===================================
echo    快速下载基础模型
echo ===================================
echo.
echo 将下载以下模型:
echo - tiny: 快速测试用 (~39 MB)
echo - base: 日常使用推荐 (~142 MB)
echo 总大小约: ~181 MB
echo.

REM 激活虚拟环境（如果存在）
if exist ".venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
)

python quick_download.py

echo.
echo 按任意键退出...
pause >nul