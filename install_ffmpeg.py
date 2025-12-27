#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg安装助手
帮助用户安装FFmpeg
"""

import os
import sys
import subprocess
import requests
import zipfile
import tempfile
from pathlib import Path

def download_ffmpeg_windows():
    """下载Windows版本的FFmpeg"""
    print("正在下载FFmpeg for Windows...")
    
    # FFmpeg下载链接（使用GitHub releases）
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    try:
        # 下载文件
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            zip_path = tmp_file.name
        
        print("下载完成，正在解压...")
        
        # 解压到当前目录
        extract_path = Path("ffmpeg")
        extract_path.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # 查找ffmpeg.exe
        ffmpeg_exe = None
        for root, dirs, files in os.walk(extract_path):
            if "ffmpeg.exe" in files:
                ffmpeg_exe = Path(root) / "ffmpeg.exe"
                break
        
        if ffmpeg_exe:
            print(f"FFmpeg已安装到: {ffmpeg_exe}")
            
            # 将ffmpeg路径添加到环境变量
            current_path = os.environ.get("PATH", "")
            ffmpeg_dir = str(ffmpeg_exe.parent)
            
            if ffmpeg_dir not in current_path:
                os.environ["PATH"] = f"{ffmpeg_dir};{current_path}"
                print("已添加到当前会话的PATH环境变量")
            
            return str(ffmpeg_exe)
        else:
            print("解压后未找到ffmpeg.exe")
            return None
            
    except Exception as e:
        print(f"下载FFmpeg失败: {e}")
        return None
    finally:
        # 清理临时文件
        try:
            os.unlink(zip_path)
        except:
            pass

def check_ffmpeg():
    """检查FFmpeg是否可用"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def main():
    print("=== FFmpeg安装助手 ===\n")
    
    # 检查是否已安装
    if check_ffmpeg():
        print("✓ FFmpeg已安装并可用")
        return
    
    print("✗ 未检测到FFmpeg")
    
    if sys.platform == "win32":
        choice = input("是否自动下载安装FFmpeg? (y/n): ").strip().lower()
        if choice == 'y':
            ffmpeg_path = download_ffmpeg_windows()
            if ffmpeg_path:
                print("\n安装成功！")
                print("注意：重启程序后FFmpeg才会生效")
            else:
                print("\n自动安装失败")
                print_manual_instructions()
        else:
            print_manual_instructions()
    else:
        print_manual_instructions()

def print_manual_instructions():
    """打印手动安装说明"""
    print("\n手动安装FFmpeg:")
    
    if sys.platform == "win32":
        print("Windows:")
        print("1. 访问 https://ffmpeg.org/download.html")
        print("2. 下载Windows版本")
        print("3. 解压到任意目录")
        print("4. 将ffmpeg.exe所在目录添加到PATH环境变量")
        print("\n或者使用包管理器:")
        print("- Chocolatey: choco install ffmpeg")
        print("- Scoop: scoop install ffmpeg")
    elif sys.platform == "darwin":
        print("macOS:")
        print("- Homebrew: brew install ffmpeg")
        print("- MacPorts: sudo port install ffmpeg")
    else:
        print("Linux:")
        print("- Ubuntu/Debian: sudo apt install ffmpeg")
        print("- CentOS/RHEL: sudo yum install ffmpeg")
        print("- Arch: sudo pacman -S ffmpeg")

if __name__ == "__main__":
    main()