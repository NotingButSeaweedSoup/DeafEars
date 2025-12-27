#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速下载常用模型
一键下载推荐的模型组合
"""

import whisper
import time
import sys

def download_essential_models():
    """下载基础必需模型"""
    essential_models = ["tiny", "base"]
    
    print("=== 快速下载基础模型 ===")
    print("将下载以下模型:")
    print("- tiny: 快速测试用 (~39 MB)")
    print("- base: 日常使用推荐 (~142 MB)")
    print("总大小约: ~181 MB\n")
    
    confirm = input("开始下载? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("下载已取消")
        return
    
    success_count = 0
    
    for model_name in essential_models:
        print(f"\n正在下载 {model_name} 模型...")
        try:
            start_time = time.time()
            model = whisper.load_model(model_name)
            end_time = time.time()
            
            print(f"✓ {model_name} 下载完成 (耗时: {end_time - start_time:.1f}秒)")
            success_count += 1
            
            # 释放内存
            del model
            
        except Exception as e:
            print(f"✗ {model_name} 下载失败: {e}")
    
    print(f"\n下载完成: {success_count}/{len(essential_models)} 个模型")
    
    if success_count == len(essential_models):
        print("✓ 所有基础模型下载成功！")
        print("现在可以启动语音转文本系统了")
    else:
        print("⚠ 部分模型下载失败，请检查网络连接")

def main():
    print("检查Whisper安装...")
    try:
        import whisper
        print("✓ Whisper已安装\n")
    except ImportError:
        print("✗ 请先安装Whisper:")
        print("pip install openai-whisper")
        input("按回车键退出...")
        return
    
    download_essential_models()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n下载被用户中断")
    except Exception as e:
        print(f"\n出现错误: {e}")
    
    input("\n按回车键退出...")