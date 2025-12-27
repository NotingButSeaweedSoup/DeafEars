#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键启动脚本
自动启动服务器和客户端
"""

import subprocess
import sys
import time
import threading
import os
import requests
from pathlib import Path

class AppLauncher:
    def __init__(self):
        self.server_process = None
        self.client_process = None
        self.server_url = "http://localhost:5000"
        
        # 设置FFmpeg路径
        self.setup_ffmpeg()
    
    def setup_ffmpeg(self):
        """设置FFmpeg路径"""
        # 获取当前脚本目录
        current_dir = Path(__file__).parent
        ffmpeg_path = current_dir / "ffmpeg" / "ffmpeg-master-latest-win64-gpl" / "bin"
        
        if ffmpeg_path.exists() and (ffmpeg_path / "ffmpeg.exe").exists():
            # 将FFmpeg路径添加到环境变量
            current_path = os.environ.get("PATH", "")
            ffmpeg_str = str(ffmpeg_path)
            
            if ffmpeg_str not in current_path:
                os.environ["PATH"] = f"{ffmpeg_str};{current_path}"
                print(f"✓ 设置FFmpeg路径: {ffmpeg_path}")
            else:
                print("✓ FFmpeg路径已设置")
        else:
            print("⚠ 未找到FFmpeg，MP3文件可能无法处理")
            print("  提示: 运行 python install_ffmpeg.py 安装FFmpeg")
    
    def check_server_running(self):
        """检查服务器是否运行"""
        try:
            response = requests.get(f"{self.server_url}/api/status", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_server(self):
        """启动服务器"""
        print("正在启动服务器...")
        
        try:
            # 启动服务器进程
            self.server_process = subprocess.Popen([
                sys.executable, "server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # 等待服务器启动
            max_wait = 30  # 最多等待30秒
            for i in range(max_wait):
                if self.check_server_running():
                    print("✓ 服务器启动成功")
                    return True
                time.sleep(1)
                print(f"等待服务器启动... ({i+1}/{max_wait})")
            
            print("✗ 服务器启动超时")
            return False
            
        except Exception as e:
            print(f"✗ 服务器启动失败: {e}")
            return False
    
    def start_client(self):
        """启动客户端"""
        print("正在启动客户端...")
        
        try:
            # 启动客户端进程
            self.client_process = subprocess.Popen([
                sys.executable, "client.py"
            ])
            
            print("✓ 客户端启动成功")
            return True
            
        except Exception as e:
            print(f"✗ 客户端启动失败: {e}")
            return False
    
    def stop_processes(self):
        """停止所有进程"""
        print("\n正在关闭应用...")
        
        if self.client_process:
            try:
                self.client_process.terminate()
                self.client_process.wait(timeout=5)
                print("✓ 客户端已关闭")
            except:
                self.client_process.kill()
                print("✓ 客户端已强制关闭")
        
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("✓ 服务器已关闭")
            except:
                self.server_process.kill()
                print("✓ 服务器已强制关闭")
    
    def run(self):
        """运行应用"""
        print("=== 你尔多🐉吗语音转文本系统启动器 ===\n")
        
        try:
            # 检查必要文件
            required_files = ["server.py", "client.py"]
            for file in required_files:
                if not os.path.exists(file):
                    print(f"✗ 缺少必要文件: {file}")
                    return
            
            # 检查服务器是否已经运行
            if self.check_server_running():
                print("✓ 检测到服务器已在运行")
                server_started = True
            else:
                server_started = self.start_server()
            
            if not server_started:
                print("服务器启动失败，无法继续")
                return
            
            # 启动客户端
            client_started = self.start_client()
            
            if not client_started:
                print("客户端启动失败")
                if self.server_process:
                    self.stop_processes()
                return
            
            print("\n=== 系统运行中 ===")
            print("服务器地址: http://localhost:5000")
            print("客户端GUI已启动")
            print("按 Ctrl+C 或关闭客户端窗口来停止系统\n")
            
            # 等待客户端进程结束
            if self.client_process:
                self.client_process.wait()
            
        except KeyboardInterrupt:
            print("\n收到停止信号...")
        except Exception as e:
            print(f"运行时错误: {e}")
        finally:
            self.stop_processes()
            print("系统已关闭")

def check_dependencies():
    """检查依赖"""
    print("检查依赖包...")
    
    required_packages = {
        'whisper': 'openai-whisper',
        'flask': 'flask',
        'requests': 'requests',
        'opencc': 'opencc-python-reimplemented',
        'tkinter': None  # 通常随Python安装
    }
    
    missing_packages = []
    
    for package, install_name in required_packages.items():
        try:
            if package == 'whisper':
                import whisper
            elif package == 'flask':
                import flask
            elif package == 'requests':
                import requests
            elif package == 'opencc':
                import opencc
            elif package == 'tkinter':
                import tkinter
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            if install_name:
                missing_packages.append(install_name)
    
    if missing_packages:
        print(f"\n缺少依赖包，请运行:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✓ 所有依赖包已安装\n")
    return True

def main():
    # 检查依赖
    if not check_dependencies():
        input("按回车键退出...")
        return
    
    # 启动应用
    launcher = AppLauncher()
    launcher.run()

if __name__ == "__main__":
    main()