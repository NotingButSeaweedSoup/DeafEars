#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音转文本客户端GUI
提供图形界面与服务器交互，集成配置管理
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import threading
import time
import os
import json
from pathlib import Path
import json

class AudioToTextClient:
    def __init__(self, root):
        self.root = root
        self.root.title("语音转文本客户端")
        self.root.geometry("900x700")
        
        # 服务器配置
        self.server_url = "http://localhost:5000"
        
        # 加载配置
        self.config = self.load_config()
        
        # 创建界面
        self.create_widgets()
        
        # 检查服务器状态
        self.check_server_status()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "deepseek": {
                    "api_key": "",
                    "base_url": "https://api.deepseek.com/v1",
                    "model": "deepseek-chat",
                    "enabled": False
                },
                "ai_correction": {
                    "enabled": True,
                    "prompt_template": "请修正以下语音转录文本中的错误，包括标点符号、语法和用词，保持原意不变，只输出修正后的文本：\n\n{text}",
                    "max_tokens": 2000,
                    "temperature": 0.1
                }
            }
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
            return False
    
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 服务器状态
        status_frame = ttk.LabelFrame(main_frame, text="服务器状态", padding="5")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="检查中...", foreground="orange")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(status_frame, text="刷新状态", command=self.check_server_status).grid(row=0, column=1, padx=(10, 0))
        ttk.Button(status_frame, text="AI配置", command=self.open_ai_config).grid(row=0, column=2, padx=(10, 0))
        
        # 模型选择
        model_frame = ttk.LabelFrame(main_frame, text="模型设置", padding="5")
        model_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(model_frame, text="模型大小:").grid(row=0, column=0, sticky=tk.W)
        
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                  values=["tiny", "base", "small", "medium", "large"],
                                  state="readonly", width=10)
        model_combo.grid(row=0, column=1, padx=(5, 10), sticky=tk.W)
        
        ttk.Button(model_frame, text="加载模型", command=self.load_model).grid(row=0, column=2)
        
        # 语言选择
        ttk.Label(model_frame, text="语言:").grid(row=0, column=3, padx=(20, 5), sticky=tk.W)
        
        self.language_var = tk.StringVar(value="zh")
        language_combo = ttk.Combobox(model_frame, textvariable=self.language_var,
                                     values=[("zh", "中文"), ("en", "英文"), ("auto", "自动检测")],
                                     state="readonly", width=10)
        language_combo.grid(row=0, column=4, sticky=tk.W)
        
        # AI修正选项
        self.ai_correction_var = tk.BooleanVar(value=self.config["ai_correction"].get("enabled", True))
        ai_checkbox = ttk.Checkbutton(model_frame, text="AI辅助修正", 
                                     variable=self.ai_correction_var,
                                     command=self.on_ai_correction_changed)
        ai_checkbox.grid(row=0, column=5, padx=(20, 0), sticky=tk.W)
        
        # AI状态指示
        self.ai_status_label = ttk.Label(model_frame, text="", foreground="gray")
        self.ai_status_label.grid(row=0, column=6, padx=(10, 0), sticky=tk.W)
        
        # 功能选择
        function_frame = ttk.LabelFrame(main_frame, text="功能选择", padding="5")
        function_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 单文件转录
        single_frame = ttk.Frame(function_frame)
        single_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(single_frame, text="选择音频文件", command=self.select_audio_file).grid(row=0, column=0)
        self.file_label = ttk.Label(single_frame, text="未选择文件", foreground="gray")
        self.file_label.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        ttk.Button(single_frame, text="开始转录", command=self.transcribe_single_file).grid(row=0, column=2, padx=(10, 0))
        
        # 批量转录
        batch_frame = ttk.Frame(function_frame)
        batch_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(batch_frame, text="选择文件夹", command=self.select_folder).grid(row=0, column=0)
        self.folder_label = ttk.Label(batch_frame, text="未选择文件夹", foreground="gray")
        self.folder_label.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        ttk.Button(batch_frame, text="批量转录", command=self.batch_transcribe).grid(row=0, column=2, padx=(10, 0))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="转录结果", padding="5")
        result_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)  # AI修正结果区域可扩展
        main_frame.rowconfigure(4, weight=1)
        
        # AI修正结果（主要显示区域）
        ai_result_frame = ttk.LabelFrame(result_frame, text="AI修正结果", padding="5")
        ai_result_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        ai_result_frame.columnconfigure(0, weight=1)
        ai_result_frame.rowconfigure(0, weight=1)
        
        self.ai_result_text = scrolledtext.ScrolledText(ai_result_frame, height=8, wrap=tk.WORD)
        self.ai_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 简体转换结果
        simplified_result_frame = ttk.LabelFrame(result_frame, text="简体转换结果", padding="5")
        simplified_result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        simplified_result_frame.columnconfigure(0, weight=1)
        simplified_result_frame.rowconfigure(0, weight=1)
        
        self.simplified_result_text = scrolledtext.ScrolledText(simplified_result_frame, height=6, wrap=tk.WORD)
        self.simplified_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 原始转录结果（可折叠）
        self.original_frame_visible = tk.BooleanVar(value=False)
        
        # 折叠按钮框架
        toggle_frame = ttk.Frame(result_frame)
        toggle_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.toggle_button = ttk.Button(toggle_frame, text="▶ 显示原始转录", 
                                       command=self.toggle_original_frame)
        self.toggle_button.grid(row=0, column=0, sticky=tk.W)
        
        # 原始转录结果框架（默认隐藏）
        self.original_result_frame = ttk.LabelFrame(result_frame, text="原始转录结果（繁体）", padding="5")
        
        original_frame_inner = ttk.Frame(self.original_result_frame)
        original_frame_inner.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        original_frame_inner.columnconfigure(0, weight=1)
        original_frame_inner.rowconfigure(0, weight=1)
        self.original_result_frame.columnconfigure(0, weight=1)
        self.original_result_frame.rowconfigure(0, weight=1)
        
        self.original_result_text = scrolledtext.ScrolledText(original_frame_inner, height=4, wrap=tk.WORD)
        self.original_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="清空结果", command=self.clear_results).grid(row=0, column=0)
        ttk.Button(button_frame, text="保存AI结果", command=self.save_ai_results).grid(row=0, column=1, padx=(10, 0))
        ttk.Button(button_frame, text="保存简体结果", command=self.save_simplified_results).grid(row=0, column=2, padx=(10, 0))
        ttk.Button(button_frame, text="复制AI结果", command=self.copy_ai_results).grid(row=0, column=3, padx=(10, 0))
        
        # 初始化变量
        self.selected_file = None
        self.selected_folder = None
        
        # 初始化AI状态和布局
        self.update_ai_status()
        
        # 根据AI配置状态调整界面
        self.update_result_layout()
    
    def toggle_original_frame(self):
        """切换原始转录结果的显示/隐藏"""
        if self.original_frame_visible.get():
            # 隐藏
            self.original_result_frame.grid_remove()
            self.toggle_button.config(text="▶ 显示原始转录")
            self.original_frame_visible.set(False)
        else:
            # 显示
            self.original_result_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
            self.toggle_button.config(text="▼ 隐藏原始转录")
            self.original_frame_visible.set(True)
    
    def update_result_layout(self):
        """根据AI配置状态更新结果显示布局"""
        # 检查组件是否已创建
        if not hasattr(self, 'ai_result_text') or not hasattr(self, 'simplified_result_text'):
            return
        
        # 检查AI是否可用
        api_configured = (self.config["deepseek"].get("enabled", False) and 
                         self.config["deepseek"].get("api_key") and 
                         self.config["deepseek"]["api_key"] != "your_deepseek_api_key_here")
        
        ai_enabled = api_configured and self.ai_correction_var.get()
        
        ai_result_frame = self.ai_result_text.master
        
        if ai_enabled:
            # 显示AI修正结果框
            ai_result_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
            # 调整简体结果框高度和位置
            self.simplified_result_text.config(height=4)
            simplified_frame = self.simplified_result_text.master
            simplified_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        else:
            # 隐藏AI修正结果框
            ai_result_frame.grid_remove()
            # 简体结果作为主要显示区域
            self.simplified_result_text.config(height=10)
            simplified_frame = self.simplified_result_text.master
            simplified_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
    
    def check_server_status(self):
        """检查服务器状态"""
        def check():
            try:
                response = requests.get(f"{self.server_url}/api/status", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    if data["model_loaded"]:
                        status_text = f"✓ 服务器运行中 (模型: {data['model_size']})"
                        color = "green"
                    else:
                        status_text = "⚠ 服务器运行中 (模型未加载)"
                        color = "orange"
                else:
                    status_text = "✗ 服务器响应异常"
                    color = "red"
            except requests.exceptions.RequestException:
                status_text = "✗ 无法连接服务器"
                color = "red"
            
            # 更新UI
            self.root.after(0, lambda: self.update_status(status_text, color))
        
        threading.Thread(target=check, daemon=True).start()
    
    def update_status(self, text, color):
        """更新状态显示"""
        self.status_label.config(text=text, foreground=color)
    
    def load_model(self):
        """加载模型"""
        model_size = self.model_var.get()
        
        def load():
            try:
                self.root.after(0, lambda: self.progress.start())
                
                response = requests.post(f"{self.server_url}/api/load_model", 
                                       json={"model_size": model_size}, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success":
                        self.root.after(0, lambda: messagebox.showinfo("成功", f"模型 {model_size} 加载成功"))
                        self.root.after(0, self.check_server_status)
                    else:
                        self.root.after(0, lambda: messagebox.showerror("错误", data["message"]))
                else:
                    self.root.after(0, lambda: messagebox.showerror("错误", "服务器请求失败"))
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"网络错误: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            finally:
                self.root.after(0, lambda: self.progress.stop())
        
        threading.Thread(target=load, daemon=True).start()
    
    def select_audio_file(self):
        """选择音频文件"""
        file_types = [
            ("音频文件", "*.wav *.mp3 *.m4a *.flac *.aac *.ogg *.wma"),
            ("所有文件", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=file_types
        )
        
        if filename:
            self.selected_file = filename
            self.file_label.config(text=os.path.basename(filename), foreground="black")
    
    def select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title="选择包含音频文件的文件夹")
        
        if folder:
            self.selected_folder = folder
            self.folder_label.config(text=os.path.basename(folder), foreground="black")
    
    def transcribe_single_file(self):
        """转录单个文件"""
        if not self.selected_file:
            messagebox.showwarning("警告", "请先选择音频文件")
            return
        
        def transcribe():
            try:
                self.root.after(0, lambda: self.progress.start())
                self.root.after(0, lambda: self.append_result(f"开始转录: {os.path.basename(self.selected_file)}\n"))
                
                # 发送转录请求
                data = {
                    "file_path": self.selected_file,
                    "language": self.language_var.get(),
                    "enable_ai_correction": self.ai_correction_var.get()
                }
                
                response = requests.post(f"{self.server_url}/api/transcribe_file", 
                                       json=data, timeout=300)  # 增加到5分钟
                
                if response.status_code == 200:
                    result = response.json()
                    if result["status"] == "success":
                        # 清空所有结果框
                        self.clear_results()
                        
                        # 显示结果信息
                        info_text = f"文件: {os.path.basename(self.selected_file)}\n"
                        info_text += f"检测语言: {result['language']}\n"
                        info_text += f"处理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        
                        # 显示AI修正状态
                        if result.get('ai_corrected', False):
                            info_text += "✓ AI辅助修正已应用\n"
                        
                        info_text += "-" * 40 + "\n\n"
                        
                        # 根据AI配置决定显示内容
                        ai_enabled = (self.config["deepseek"].get("enabled", False) and 
                                     self.config["deepseek"].get("api_key") and 
                                     self.ai_correction_var.get())
                        
                        if ai_enabled and result.get('ai_corrected', False):
                            # 显示AI修正结果
                            self.ai_result_text.insert(tk.END, info_text + result['text'])
                            
                            # 显示简体转换结果
                            if 'simplified_text' in result:
                                simplified_info = f"简体转换结果:\n{'-' * 20}\n"
                                self.simplified_result_text.insert(tk.END, simplified_info + result['simplified_text'])
                        else:
                            # 没有AI修正，简体结果作为主要显示
                            main_text = result.get('simplified_text', result['text'])
                            self.simplified_result_text.insert(tk.END, info_text + main_text)
                        
                        # 显示原始转录结果
                        if 'original_text' in result and result['original_text'] != result.get('simplified_text', result['text']):
                            original_info = f"原始转录结果（繁体）:\n{'-' * 20}\n"
                            self.original_result_text.insert(tk.END, original_info + result['original_text'])
                        
                        self.root.after(0, lambda: None)  # 刷新界面
                    else:
                        self.root.after(0, lambda: messagebox.showerror("错误", result["message"]))
                else:
                    self.root.after(0, lambda: messagebox.showerror("错误", "服务器请求失败"))
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"网络错误: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            finally:
                self.root.after(0, lambda: self.progress.stop())
        
        threading.Thread(target=transcribe, daemon=True).start()
    
    def batch_transcribe(self):
        """批量转录"""
        if not self.selected_folder:
            messagebox.showwarning("警告", "请先选择文件夹")
            return
        
        def transcribe():
            try:
                self.root.after(0, lambda: self.progress.start())
                self.root.after(0, lambda: self.append_result(f"开始批量转录: {self.selected_folder}\n"))
                
                # 发送批量转录请求
                data = {
                    "folder_path": self.selected_folder,
                    "language": self.language_var.get(),
                    "enable_ai_correction": self.ai_correction_var.get()
                }
                
                response = requests.post(f"{self.server_url}/api/batch_transcribe", 
                                       json=data, timeout=300)
                
                if response.status_code == 200:
                    result = response.json()
                    if result["status"] == "success":
                        # 清空所有结果框
                        self.clear_results()
                        
                        # 显示批量处理结果信息
                        info_text = f"批量转录完成!\n"
                        info_text += f"总文件数: {result['total_files']}\n"
                        info_text += f"成功转录: {result['successful']}\n"
                        info_text += f"处理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        info_text += "=" * 50 + "\n\n"
                        
                        # 根据AI配置决定显示方式
                        ai_enabled = (self.config["deepseek"].get("enabled", False) and 
                                     self.config["deepseek"].get("api_key") and 
                                     self.ai_correction_var.get())
                        
                        ai_results = []
                        simplified_results = []
                        original_results = []
                        
                        for item in result["results"]:
                            file_info = f"文件: {item['filename']}\n语言: {item['language']}\n"
                            
                            # AI修正结果
                            if ai_enabled and item.get('ai_corrected', False):
                                ai_text = file_info + f"✓ AI修正: {item['text']}\n" + "-" * 30 + "\n\n"
                                ai_results.append(ai_text)
                            
                            # 简体转换结果
                            simplified_text = item.get('simplified_text', item['text'])
                            simp_text = file_info + f"简体: {simplified_text}\n" + "-" * 30 + "\n\n"
                            simplified_results.append(simp_text)
                            
                            # 原始转录结果
                            if 'original_text' in item and item['original_text'] != simplified_text:
                                orig_text = file_info + f"原始: {item['original_text']}\n" + "-" * 30 + "\n\n"
                                original_results.append(orig_text)
                        
                        # 显示结果
                        if ai_results:
                            self.ai_result_text.insert(tk.END, info_text + "".join(ai_results))
                        
                        if simplified_results:
                            simp_info = info_text if not ai_results else ""
                            self.simplified_result_text.insert(tk.END, simp_info + "".join(simplified_results))
                        
                        if original_results:
                            self.original_result_text.insert(tk.END, "".join(original_results))
                        
                        self.root.after(0, lambda: None)  # 刷新界面
                    else:
                        self.root.after(0, lambda: messagebox.showerror("错误", result["message"]))
                else:
                    self.root.after(0, lambda: messagebox.showerror("错误", "服务器请求失败"))
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"网络错误: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            finally:
                self.root.after(0, lambda: self.progress.stop())
        
        threading.Thread(target=transcribe, daemon=True).start()
    
    def append_result(self, text):
        """向结果区域追加文本"""
        # 根据AI配置决定追加到哪个文本框
        ai_enabled = (self.config["deepseek"].get("enabled", False) and 
                     self.config["deepseek"].get("api_key") and 
                     self.ai_correction_var.get())
        
        if ai_enabled:
            # AI启用时，追加到AI结果框
            self.ai_result_text.insert(tk.END, text)
            self.ai_result_text.see(tk.END)
        else:
            # AI未启用时，追加到简体结果框
            self.simplified_result_text.insert(tk.END, text)
            self.simplified_result_text.see(tk.END)
    
    def clear_results(self):
        """清空所有结果"""
        self.ai_result_text.delete(1.0, tk.END)
        self.simplified_result_text.delete(1.0, tk.END)
        self.original_result_text.delete(1.0, tk.END)
    
    def save_ai_results(self):
        """保存AI修正结果"""
        content = self.ai_result_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有AI修正内容可保存")
            return
        
        filename = filedialog.asksaveasfilename(
            title="保存AI修正结果",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"AI修正结果已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def save_simplified_results(self):
        """保存简体转换结果"""
        content = self.simplified_result_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有简体转换内容可保存")
            return
        
        filename = filedialog.asksaveasfilename(
            title="保存简体转换结果",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"简体转换结果已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def copy_ai_results(self):
        """复制AI修正结果到剪贴板"""
        content = self.ai_result_text.get(1.0, tk.END).strip()
        if not content:
            # 如果没有AI结果，复制简体结果
            content = self.simplified_result_text.get(1.0, tk.END).strip()
        
        if not content:
            messagebox.showwarning("警告", "没有内容可复制")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("成功", "结果已复制到剪贴板")
    
    def update_ai_status(self):
        """更新AI状态显示"""
        if self.config["deepseek"].get("enabled", False) and self.config["deepseek"].get("api_key"):
            self.ai_status_label.config(text="✓ AI已配置", foreground="green")
        else:
            self.ai_status_label.config(text="⚠ AI未配置", foreground="orange")
        
        # 更新结果显示布局
        self.update_result_layout()
    
    def on_ai_correction_changed(self):
        """AI修正选项变化时的回调"""
        self.update_result_layout()
    
    def open_ai_config(self):
        """打开AI配置窗口"""
        config_window = tk.Toplevel(self.root)
        config_window.title("AI配置")
        config_window.geometry("600x500")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(config_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        config_window.columnconfigure(0, weight=1)
        config_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # DeepSeek API配置
        deepseek_frame = ttk.LabelFrame(main_frame, text="DeepSeek API配置", padding="10")
        deepseek_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        deepseek_frame.columnconfigure(1, weight=1)
        
        # API密钥
        ttk.Label(deepseek_frame, text="API密钥:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        api_key_var = tk.StringVar(value=self.config["deepseek"].get("api_key", ""))
        api_key_entry = ttk.Entry(deepseek_frame, textvariable=api_key_var, show="*", width=50)
        api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 显示/隐藏密钥
        show_key_var = tk.BooleanVar()
        show_key_cb = ttk.Checkbutton(deepseek_frame, text="显示", 
                                     variable=show_key_var, 
                                     command=lambda: api_key_entry.config(show="" if show_key_var.get() else "*"))
        show_key_cb.grid(row=0, column=2, padx=(5, 0), pady=(0, 5))
        
        # API地址
        ttk.Label(deepseek_frame, text="API地址:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        base_url_var = tk.StringVar(value=self.config["deepseek"].get("base_url", "https://api.deepseek.com/v1"))
        ttk.Entry(deepseek_frame, textvariable=base_url_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 模型
        ttk.Label(deepseek_frame, text="模型:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        model_var = tk.StringVar(value=self.config["deepseek"].get("model", "deepseek-chat"))
        ttk.Entry(deepseek_frame, textvariable=model_var, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 启用DeepSeek
        deepseek_enabled_var = tk.BooleanVar(value=self.config["deepseek"].get("enabled", False))
        ttk.Checkbutton(deepseek_frame, text="启用DeepSeek API", 
                       variable=deepseek_enabled_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # AI修正配置
        ai_frame = ttk.LabelFrame(main_frame, text="AI修正配置", padding="10")
        ai_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        ai_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 启用AI修正
        ai_enabled_var = tk.BooleanVar(value=self.config["ai_correction"].get("enabled", True))
        ttk.Checkbutton(ai_frame, text="启用AI辅助修正", 
                       variable=ai_enabled_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 提示词模板
        ttk.Label(ai_frame, text="提示词模板:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        
        prompt_text = tk.Text(ai_frame, height=6, wrap=tk.WORD)
        prompt_text.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        prompt_text.insert(1.0, self.config["ai_correction"].get("prompt_template", ""))
        
        # 滚动条
        prompt_scroll = ttk.Scrollbar(ai_frame, orient=tk.VERTICAL, command=prompt_text.yview)
        prompt_scroll.grid(row=1, column=2, sticky=(tk.N, tk.S), pady=(0, 5))
        prompt_text.config(yscrollcommand=prompt_scroll.set)
        
        # 参数设置
        params_frame = ttk.Frame(ai_frame)
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(params_frame, text="最大令牌数:").grid(row=0, column=0, sticky=tk.W)
        max_tokens_var = tk.StringVar(value=str(self.config["ai_correction"].get("max_tokens", 2000)))
        ttk.Entry(params_frame, textvariable=max_tokens_var, width=10).grid(row=0, column=1, padx=(5, 20))
        
        ttk.Label(params_frame, text="温度:").grid(row=0, column=2, sticky=tk.W)
        temperature_var = tk.StringVar(value=str(self.config["ai_correction"].get("temperature", 0.1)))
        ttk.Entry(params_frame, textvariable=temperature_var, width=10).grid(row=0, column=3, padx=(5, 0))
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        def test_connection():
            """测试API连接"""
            if not api_key_var.get():
                messagebox.showwarning("警告", "请先输入API密钥")
                return
            
            try:
                import httpx
                
                headers = {
                    "Authorization": f"Bearer {api_key_var.get()}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": model_var.get(),
                    "messages": [{"role": "user", "content": "测试连接"}],
                    "max_tokens": 10
                }
                
                with httpx.Client(timeout=10.0) as client:
                    response = client.post(f"{base_url_var.get()}/chat/completions", 
                                         headers=headers, json=data)
                    
                    if response.status_code == 200:
                        messagebox.showinfo("成功", "API连接测试成功！")
                    else:
                        messagebox.showerror("错误", f"API连接失败: {response.status_code}")
                        
            except Exception as e:
                messagebox.showerror("错误", f"连接测试失败: {e}")
        
        def save_config():
            """保存配置"""
            try:
                # 更新配置
                self.config["deepseek"]["api_key"] = api_key_var.get()
                self.config["deepseek"]["base_url"] = base_url_var.get()
                self.config["deepseek"]["model"] = model_var.get()
                self.config["deepseek"]["enabled"] = deepseek_enabled_var.get()
                
                self.config["ai_correction"]["enabled"] = ai_enabled_var.get()
                self.config["ai_correction"]["prompt_template"] = prompt_text.get(1.0, tk.END).strip()
                self.config["ai_correction"]["max_tokens"] = int(max_tokens_var.get())
                self.config["ai_correction"]["temperature"] = float(temperature_var.get())
                
                if self.save_config():
                    self.update_ai_status()  # 更新主界面AI状态
                    self.ai_correction_var.set(ai_enabled_var.get())  # 同步AI修正选项
                    messagebox.showinfo("成功", "配置保存成功！")
                    config_window.destroy()
                    
            except ValueError:
                messagebox.showerror("错误", "参数格式错误，请检查数值输入")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")
        
        ttk.Button(button_frame, text="测试连接", command=test_connection).grid(row=0, column=0)
        ttk.Button(button_frame, text="保存配置", command=save_config).grid(row=0, column=1, padx=(10, 0))
        ttk.Button(button_frame, text="取消", command=config_window.destroy).grid(row=0, column=2, padx=(10, 0))
        
        # 说明
        info_frame = ttk.LabelFrame(main_frame, text="说明", padding="10")
        info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        info_text = """1. 获取DeepSeek API密钥: https://platform.deepseek.com/
2. 提示词模板中的 {text} 会被替换为转录文本
3. 温度值越低，输出越稳定；越高，输出越有创意
4. 最大令牌数限制AI响应的长度"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)

def main():
    root = tk.Tk()
    app = AudioToTextClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()