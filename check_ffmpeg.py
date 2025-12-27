#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg检查工具
检查FFmpeg是否正确安装和配置
"""

import os
import subprocess
import sys
from pathlib import Path

def check_local_ffmpeg():
    """检查本地FFmpeg"""
    print("🔍 检查本地FFmpeg...")
    
    current_dir = Path(__file__).parent
    ffmpeg_path = current_dir / "ffmpeg" / "ffmpeg-master-latest-win64-gpl" / "bin"
    ffmpeg_exe = ffmpeg_path / "ffmpeg.exe"
    
    if ffmpeg_exe.exists():
        print(f"✅ 找到本地FFmpeg: {ffmpeg_exe}")
        
        # 测试FFmpeg版本
        try:
            result = subprocess.run([str(ffmpeg_exe), "-version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ FFmpeg版本: {version_line}")
                return True
            else:
                print("❌ FFmpeg无法正常运行")
                return False
        except Exception as e:
            print(f"❌ FFmpeg测试失败: {e}")
            return False
    else:
        print("❌ 未找到本地FFmpeg")
        return False

def check_system_ffmpeg():
    """检查系统FFmpeg"""
    print("\n🔍 检查系统FFmpeg...")
    
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ 系统FFmpeg: {version_line}")
            return True
        else:
            print("❌ 系统FFmpeg无法运行")
            return False
    except FileNotFoundError:
        print("❌ 系统中未安装FFmpeg")
        return False
    except Exception as e:
        print(f"❌ 系统FFmpeg测试失败: {e}")
        return False

def test_audio_conversion():
    """测试音频转换功能"""
    print("\n🎵 测试音频转换功能...")
    
    # 创建一个简单的测试音频文件
    test_command = [
        "ffmpeg", "-f", "lavfi", "-i", "sine=frequency=1000:duration=1",
        "-y", "test_audio.wav"
    ]
    
    try:
        result = subprocess.run(test_command, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and os.path.exists("test_audio.wav"):
            print("✅ 音频转换测试成功")
            
            # 清理测试文件
            try:
                os.remove("test_audio.wav")
            except:
                pass
            
            return True
        else:
            print("❌ 音频转换测试失败")
            return False
    except Exception as e:
        print(f"❌ 音频转换测试异常: {e}")
        return False

def show_installation_guide():
    """显示安装指南"""
    print("\n📋 FFmpeg安装指南:")
    print("=" * 40)
    
    print("方法1: 使用自动安装脚本 (推荐)")
    print("   python install_ffmpeg.py")
    
    print("\n方法2: 手动下载安装")
    print("   1. 访问: https://ffmpeg.org/download.html")
    print("   2. 下载适合您系统的版本")
    print("   3. 解压到项目的ffmpeg文件夹")
    
    print("\n方法3: 使用包管理器")
    print("   Windows: winget install ffmpeg")
    print("   macOS:   brew install ffmpeg")
    print("   Ubuntu:  sudo apt install ffmpeg")

def main():
    print("🔧 FFmpeg检查工具")
    print("=" * 30)
    
    local_ok = check_local_ffmpeg()
    system_ok = check_system_ffmpeg()
    
    if local_ok or system_ok:
        print(f"\n✅ FFmpeg状态: 正常")
        
        # 如果有可用的FFmpeg，测试音频转换
        if local_ok or system_ok:
            test_audio_conversion()
        
        print(f"\n🎯 建议:")
        if local_ok:
            print("   ✓ 本地FFmpeg已配置，可以正常使用")
        if system_ok:
            print("   ✓ 系统FFmpeg可用，作为备选方案")
        
    else:
        print(f"\n❌ FFmpeg状态: 未安装")
        print(f"\n⚠️  警告:")
        print("   - MP3、M4A等格式可能无法处理")
        print("   - 建议安装FFmpeg以获得完整功能")
        
        show_installation_guide()
        
        # 询问是否立即安装
        choice = input(f"\n是否立即运行自动安装? (y/N): ").strip().lower()
        if choice == 'y':
            try:
                subprocess.run([sys.executable, "install_ffmpeg.py"])
            except Exception as e:
                print(f"安装失败: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
    except Exception as e:
        print(f"\n检查工具出现错误: {e}")
    
    input("\n按回车键退出...")