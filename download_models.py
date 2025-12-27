#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper模型预下载工具
允许用户提前下载所需的模型，避免首次使用时的等待
"""

import whisper
import os
import sys
from pathlib import Path
import time

class ModelDownloader:
    def __init__(self):
        # Whisper模型信息
        self.models = {
            "tiny": {
                "size": "~39 MB",
                "description": "最小模型，速度最快，准确度较低",
                "languages": "多语言支持",
                "recommended": "快速测试"
            },
            "base": {
                "size": "~142 MB", 
                "description": "基础模型，速度和准确度平衡",
                "languages": "多语言支持",
                "recommended": "日常使用"
            },
            "small": {
                "size": "~466 MB",
                "description": "小型模型，准确度较好",
                "languages": "多语言支持", 
                "recommended": "高质量转录"
            },
            "medium": {
                "size": "~1.5 GB",
                "description": "中型模型，准确度很好",
                "languages": "多语言支持",
                "recommended": "专业使用"
            },
            "large": {
                "size": "~3.0 GB",
                "description": "大型模型，准确度最高",
                "languages": "多语言支持",
                "recommended": "最高质量"
            }
        }
        
        # 获取模型缓存目录
        self.cache_dir = self.get_cache_dir()
    
    def get_cache_dir(self):
        """获取Whisper模型缓存目录"""
        # Whisper默认缓存目录
        home = Path.home()
        cache_dir = home / ".cache" / "whisper"
        
        # Windows上可能在不同位置
        if os.name == 'nt':
            # 尝试几个可能的位置
            possible_dirs = [
                home / ".cache" / "whisper",
                Path(os.environ.get('LOCALAPPDATA', '')) / "whisper",
                Path(os.environ.get('APPDATA', '')) / "whisper"
            ]
            
            for dir_path in possible_dirs:
                if dir_path.exists():
                    cache_dir = dir_path
                    break
        
        return cache_dir
    
    def check_model_exists(self, model_name):
        """检查模型是否已下载"""
        try:
            # 尝试加载模型，如果存在则不会重新下载
            model_path = self.cache_dir / f"{model_name}.pt"
            return model_path.exists()
        except:
            return False
    
    def get_model_size_on_disk(self, model_name):
        """获取已下载模型的磁盘大小"""
        try:
            model_path = self.cache_dir / f"{model_name}.pt"
            if model_path.exists():
                size_bytes = model_path.stat().st_size
                return self.format_size(size_bytes)
            return "未下载"
        except:
            return "未知"
    
    def format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def show_models_info(self):
        """显示所有模型信息"""
        print("=== Whisper模型信息 ===\n")
        print(f"模型缓存目录: {self.cache_dir}\n")
        
        for model_name, info in self.models.items():
            exists = self.check_model_exists(model_name)
            disk_size = self.get_model_size_on_disk(model_name)
            status = "✓ 已下载" if exists else "✗ 未下载"
            
            print(f"【{model_name.upper()}】")
            print(f"  状态: {status}")
            print(f"  大小: {info['size']} (磁盘: {disk_size})")
            print(f"  描述: {info['description']}")
            print(f"  推荐: {info['recommended']}")
            print()
    
    def download_model(self, model_name):
        """下载指定模型"""
        if model_name not in self.models:
            print(f"错误: 未知模型 '{model_name}'")
            return False
        
        print(f"开始下载 {model_name} 模型...")
        print(f"预计大小: {self.models[model_name]['size']}")
        print("首次下载需要网络连接，请耐心等待...\n")
        
        try:
            start_time = time.time()
            
            # 使用whisper.load_model下载模型
            model = whisper.load_model(model_name)
            
            end_time = time.time()
            download_time = end_time - start_time
            
            print(f"✓ {model_name} 模型下载完成！")
            print(f"耗时: {download_time:.1f} 秒")
            
            # 显示模型信息
            actual_size = self.get_model_size_on_disk(model_name)
            print(f"实际大小: {actual_size}")
            
            # 释放内存
            del model
            
            return True
            
        except Exception as e:
            print(f"✗ {model_name} 模型下载失败: {e}")
            return False
    
    def download_multiple_models(self, model_names):
        """批量下载多个模型"""
        success_count = 0
        total_count = len(model_names)
        
        print(f"准备下载 {total_count} 个模型...\n")
        
        for i, model_name in enumerate(model_names, 1):
            print(f"[{i}/{total_count}] ", end="")
            
            if self.check_model_exists(model_name):
                print(f"{model_name} 模型已存在，跳过下载")
                success_count += 1
            else:
                if self.download_model(model_name):
                    success_count += 1
            
            print("-" * 50)
        
        print(f"\n下载完成: {success_count}/{total_count} 个模型")
        return success_count == total_count
    
    def interactive_download(self):
        """交互式下载"""
        while True:
            print("\n=== 模型下载菜单 ===")
            print("1. 查看所有模型状态")
            print("2. 下载单个模型")
            print("3. 下载推荐模型组合")
            print("4. 下载所有模型")
            print("5. 清理缓存")
            print("0. 退出")
            
            choice = input("\n请选择操作 (0-5): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.show_models_info()
            elif choice == "2":
                self.download_single_model()
            elif choice == "3":
                self.download_recommended_combo()
            elif choice == "4":
                self.download_all_models()
            elif choice == "5":
                self.clean_cache()
            else:
                print("无效选择，请重试")
    
    def download_single_model(self):
        """下载单个模型"""
        print("\n可用模型:")
        for i, (model_name, info) in enumerate(self.models.items(), 1):
            exists = "✓" if self.check_model_exists(model_name) else "✗"
            print(f"{i}. {model_name} ({info['size']}) {exists}")
        
        try:
            choice = int(input("\n请选择模型编号: ")) - 1
            model_names = list(self.models.keys())
            
            if 0 <= choice < len(model_names):
                model_name = model_names[choice]
                if self.check_model_exists(model_name):
                    print(f"{model_name} 模型已存在")
                else:
                    self.download_model(model_name)
            else:
                print("无效选择")
        except ValueError:
            print("请输入有效数字")
    
    def download_recommended_combo(self):
        """下载推荐模型组合"""
        print("\n推荐模型组合:")
        print("1. 轻量组合: tiny + base (适合日常使用)")
        print("2. 标准组合: base + small (平衡性能和质量)")
        print("3. 高质量组合: small + medium (专业使用)")
        
        choice = input("请选择组合 (1-3): ").strip()
        
        combos = {
            "1": ["tiny", "base"],
            "2": ["base", "small"], 
            "3": ["small", "medium"]
        }
        
        if choice in combos:
            models = combos[choice]
            print(f"\n将下载: {', '.join(models)}")
            confirm = input("确认下载? (y/N): ").strip().lower()
            
            if confirm == 'y':
                self.download_multiple_models(models)
        else:
            print("无效选择")
    
    def download_all_models(self):
        """下载所有模型"""
        total_size = "~5.1 GB"
        print(f"\n将下载所有模型，总大小约: {total_size}")
        print("这将需要较长时间和大量磁盘空间")
        
        confirm = input("确认下载所有模型? (y/N): ").strip().lower()
        
        if confirm == 'y':
            all_models = list(self.models.keys())
            self.download_multiple_models(all_models)
    
    def clean_cache(self):
        """清理模型缓存"""
        print(f"\n模型缓存目录: {self.cache_dir}")
        
        if not self.cache_dir.exists():
            print("缓存目录不存在")
            return
        
        # 列出缓存文件
        cache_files = list(self.cache_dir.glob("*.pt"))
        
        if not cache_files:
            print("没有找到缓存文件")
            return
        
        print("找到以下缓存文件:")
        total_size = 0
        for file_path in cache_files:
            size = file_path.stat().st_size
            total_size += size
            print(f"  {file_path.name} ({self.format_size(size)})")
        
        print(f"\n总大小: {self.format_size(total_size)}")
        
        confirm = input("确认删除所有缓存文件? (y/N): ").strip().lower()
        
        if confirm == 'y':
            try:
                for file_path in cache_files:
                    file_path.unlink()
                    print(f"已删除: {file_path.name}")
                print("✓ 缓存清理完成")
            except Exception as e:
                print(f"✗ 清理失败: {e}")

def main():
    print("=== Whisper模型下载工具 ===")
    print("此工具可以帮助您预先下载Whisper模型")
    print("避免首次使用时的等待时间\n")
    
    # 检查依赖
    try:
        import whisper
        print("✓ Whisper已安装")
    except ImportError:
        print("✗ 请先安装Whisper: pip install openai-whisper")
        input("按回车键退出...")
        return
    
    # 检查网络连接
    print("检查网络连接...")
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✓ 网络连接正常\n")
    except:
        print("⚠ 网络连接可能有问题，下载可能失败\n")
    
    # 启动下载器
    downloader = ModelDownloader()
    
    # 如果有命令行参数，直接下载指定模型
    if len(sys.argv) > 1:
        models_to_download = sys.argv[1:]
        print(f"命令行模式: 下载模型 {models_to_download}")
        downloader.download_multiple_models(models_to_download)
    else:
        # 交互模式
        downloader.interactive_download()
    
    print("\n感谢使用模型下载工具！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n下载被用户中断")
    except Exception as e:
        print(f"\n程序出现错误: {e}")
    
    input("按回车键退出...")