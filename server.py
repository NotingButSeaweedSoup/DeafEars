#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音转文本服务器端
提供REST API接口处理音频文件转录
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import os
import tempfile
import threading
import time
from pathlib import Path
import logging
import json
import httpx

# 导入音频转换工具
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# 导入繁简转换工具
try:
    import opencc
    OPENCC_AVAILABLE = True
    # 创建繁体转简体的转换器
    converter = opencc.OpenCC('t2s')  # Traditional to Simplified
except ImportError:
    OPENCC_AVAILABLE = False
    converter = None

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

class WhisperServer:
    def __init__(self):
        self.model = None
        self.model_size = "base"
        self.is_loading = False
        self.config = self.load_config()
        
    def load_config(self):
        """加载配置文件"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info("配置文件加载成功")
            return config
        except Exception as e:
            logger.warning(f"配置文件加载失败: {e}")
            return {
                "deepseek": {"enabled": False},
                "ai_correction": {"enabled": False}
            }
    
    def ai_correct_text(self, text):
        """使用DeepSeek AI修正文本"""
        if not self.config.get("ai_correction", {}).get("enabled", False):
            return text, False
        
        if not self.config.get("deepseek", {}).get("enabled", False):
            logger.warning("DeepSeek API未启用")
            return text, False
        
        api_key = self.config["deepseek"].get("api_key")
        if not api_key or api_key == "your_deepseek_api_key_here":
            logger.warning("DeepSeek API密钥未配置")
            return text, False
        
        try:
            logger.info("开始AI文本修正...")
            
            # 准备请求
            base_url = self.config["deepseek"].get("base_url", "https://api.deepseek.com/v1")
            model = self.config["deepseek"].get("model", "deepseek-chat")
            
            prompt_template = self.config["ai_correction"].get(
                "prompt_template", 
                "请修正以下语音转录文本中的错误，包括标点符号、语法和用词，保持原意不变，只输出修正后的文本：\n\n{text}"
            )
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt_template.format(text=text)
                    }
                ],
                "max_tokens": self.config["ai_correction"].get("max_tokens", 2000),
                "temperature": self.config["ai_correction"].get("temperature", 0.1)
            }
            
            # 发送请求，设置较短的超时时间
            with httpx.Client(timeout=60.0) as client:  # 减少到60秒
                response = client.post(f"{base_url}/chat/completions", 
                                     headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                corrected_text = result["choices"][0]["message"]["content"].strip()
                
                logger.info("AI文本修正完成")
                return corrected_text, True
                
        except httpx.TimeoutException:
            logger.error("AI文本修正超时，使用原始文本")
            return text, False
        except Exception as e:
            logger.error(f"AI文本修正失败: {e}")
            return text, False
        
    def load_model(self, model_size="base"):
        """加载Whisper模型"""
        if self.is_loading:
            return {"status": "error", "message": "模型正在加载中..."}
        
        if self.model and self.model_size == model_size:
            return {"status": "success", "message": f"模型 {model_size} 已加载"}
        
        self.is_loading = True
        try:
            logger.info(f"正在加载Whisper {model_size} 模型...")
            self.model = whisper.load_model(model_size)
            self.model_size = model_size
            logger.info("模型加载完成")
            return {"status": "success", "message": f"模型 {model_size} 加载成功"}
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            return {"status": "error", "message": f"模型加载失败: {str(e)}"}
        finally:
            self.is_loading = False
    
    def convert_to_simplified(self, text):
        """将繁体中文转换为简体中文"""
        if not OPENCC_AVAILABLE or not converter:
            return text
        
        try:
            return converter.convert(text)
        except Exception as e:
            logger.warning(f"繁简转换失败: {e}")
            return text
    
    def transcribe_audio(self, audio_file, language='zh', enable_ai_correction=True):
        """转录音频文件"""
        if not self.model:
            return {"status": "error", "message": "模型未加载"}
        
        try:
            logger.info(f"开始转录音频文件: {audio_file}")
            
            # 检查文件是否存在
            if not os.path.exists(audio_file):
                return {"status": "error", "message": f"文件不存在: {audio_file}"}
            
            # 检查文件大小
            file_size = os.path.getsize(audio_file)
            logger.info(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
            
            # 如果文件过大，给出警告
            if file_size > 100 * 1024 * 1024:  # 100MB
                logger.warning(f"文件较大 ({file_size / 1024 / 1024:.2f} MB)，转录可能需要较长时间")
            
            # 转录音频 - 让Whisper直接尝试处理
            transcribe_options = {
                "language": language if language and language != 'auto' else None,
                "fp16": False,  # 在CPU上禁用FP16
                "verbose": False,
                "beam_size": 1,  # 减少beam search以提高速度
                "best_of": 1,    # 减少候选数量以提高速度
                "temperature": 0.0  # 使用确定性输出
            }
            
            logger.info("开始Whisper转录...")
            start_time = time.time()
            
            # 直接尝试转录，Whisper内部会处理格式转换
            result = self.model.transcribe(audio_file, **transcribe_options)
            
            transcribe_time = time.time() - start_time
            logger.info(f"Whisper转录完成，耗时: {transcribe_time:.2f} 秒")
            
            # 提取结果
            text = result["text"].strip()
            detected_language = result.get("language", "未知")
            segments = result.get("segments", [])
            
            if not text:
                return {"status": "error", "message": "转录结果为空，可能是音频文件损坏或格式不支持"}
            
            # 如果是中文，转换为简体
            if detected_language == 'zh' or language == 'zh':
                logger.info("开始繁简转换...")
                simplified_text = self.convert_to_simplified(text)
                logger.info("繁简转换完成")
            else:
                simplified_text = text
            
            # AI修正文本
            corrected_text = simplified_text
            ai_corrected = False
            if enable_ai_correction and (detected_language == 'zh' or language == 'zh'):
                logger.info("开始AI文本修正...")
                ai_start_time = time.time()
                corrected_text, ai_corrected = self.ai_correct_text(simplified_text)
                ai_time = time.time() - ai_start_time
                logger.info(f"AI修正完成，耗时: {ai_time:.2f} 秒")
            
            total_time = time.time() - start_time
            logger.info(f"转录完成，总耗时: {total_time:.2f} 秒")
            
            return {
                "status": "success",
                "text": corrected_text,  # 最终修正后的文本
                "simplified_text": simplified_text,  # 简体转换后的文本
                "original_text": text,  # 原始转录文本
                "ai_corrected": ai_corrected,  # 是否进行了AI修正
                "language": detected_language,
                "segments": len(segments),
                "duration": sum(seg.get('end', 0) - seg.get('start', 0) for seg in segments),
                "processing_time": total_time,  # 添加处理时间信息
                "file_size_mb": file_size / 1024 / 1024  # 添加文件大小信息
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"转录失败: {error_msg}")
            
            # 提供更友好的错误信息和解决方案
            if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
                return {
                    "status": "error", 
                    "message": "需要安装FFmpeg来处理MP3文件。解决方案：\n1. 运行 python install_ffmpeg.py 自动安装\n2. 或手动安装FFmpeg\n3. 或将MP3文件转换为WAV格式"
                }
            elif "找不到指定的文件" in error_msg:
                return {
                    "status": "error", 
                    "message": "音频文件处理失败。建议：\n1. 安装FFmpeg处理MP3文件\n2. 或使用WAV格式的音频文件"
                }
            else:
                return {"status": "error", "message": f"转录失败: {error_msg}"}

# 创建全局服务器实例
whisper_server = WhisperServer()

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取服务器状态"""
    return jsonify({
        "status": "running",
        "model_loaded": whisper_server.model is not None,
        "model_size": whisper_server.model_size,
        "is_loading": whisper_server.is_loading
    })

@app.route('/api/load_model', methods=['POST'])
def load_model():
    """加载模型"""
    data = request.get_json()
    model_size = data.get('model_size', 'base')
    
    if whisper_server.is_loading:
        return jsonify({"status": "error", "message": "模型正在加载中..."})
    
    # 直接在当前线程中加载模型，而不是后台线程
    result = whisper_server.load_model(model_size)
    return jsonify(result)

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    """转录音频文件"""
    if 'audio' not in request.files:
        return jsonify({"status": "error", "message": "未找到音频文件"})
    
    audio_file = request.files['audio']
    language = request.form.get('language', 'zh')
    enable_ai_correction = request.form.get('enable_ai_correction', 'true').lower() == 'true'
    
    if audio_file.filename == '':
        return jsonify({"status": "error", "message": "未选择文件"})
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as tmp_file:
        audio_file.save(tmp_file.name)
        
        try:
            # 转录音频
            result = whisper_server.transcribe_audio(tmp_file.name, language, enable_ai_correction)
            return jsonify(result)
        finally:
            # 删除临时文件
            try:
                os.unlink(tmp_file.name)
            except:
                pass

@app.route('/api/transcribe_file', methods=['POST'])
def transcribe_file():
    """转录本地文件"""
    data = request.get_json()
    file_path = data.get('file_path')
    language = data.get('language', 'zh')
    enable_ai_correction = data.get('enable_ai_correction', True)
    
    if not file_path:
        return jsonify({"status": "error", "message": "未提供文件路径"})
    
    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": f"文件不存在: {file_path}"})
    
    result = whisper_server.transcribe_audio(file_path, language, enable_ai_correction)
    return jsonify(result)

@app.route('/api/batch_transcribe', methods=['POST'])
def batch_transcribe():
    """批量转录文件夹"""
    data = request.get_json()
    folder_path = data.get('folder_path')
    language = data.get('language', 'zh')
    enable_ai_correction = data.get('enable_ai_correction', True)
    
    if not folder_path:
        return jsonify({"status": "error", "message": "未提供文件夹路径"})
    
    if not os.path.exists(folder_path):
        return jsonify({"status": "error", "message": f"文件夹不存在: {folder_path}"})
    
    # 支持的音频格式
    audio_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.aac', '.ogg', '.wma'}
    
    # 查找音频文件
    audio_files = []
    for file_path in Path(folder_path).rglob('*'):
        if file_path.suffix.lower() in audio_extensions:
            audio_files.append(str(file_path))
    
    if not audio_files:
        return jsonify({"status": "error", "message": "未找到音频文件"})
    
    results = []
    for audio_file in audio_files:
        result = whisper_server.transcribe_audio(audio_file, language, enable_ai_correction)
        if result["status"] == "success":
            results.append({
                "file": audio_file,
                "filename": os.path.basename(audio_file),
                "text": result["text"],
                "simplified_text": result.get("simplified_text", ""),
                "original_text": result.get("original_text", ""),
                "ai_corrected": result.get("ai_corrected", False),
                "language": result["language"]
            })
    
    return jsonify({
        "status": "success",
        "total_files": len(audio_files),
        "successful": len(results),
        "results": results
    })

def main():
    print("=== 语音转文本服务器 ===")
    print("正在启动服务器...")
    
    # 默认加载base模型
    print("加载默认模型...")
    whisper_server.load_model("base")
    
    print("服务器启动成功!")
    print("API地址: http://localhost:5000")
    print("状态检查: http://localhost:5000/api/status")
    print("按 Ctrl+C 停止服务器")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()