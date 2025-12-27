# DeafEars - 语音转文本系统

基于OpenAI Whisper的语音转文本系统，支持繁简转换和AI辅助修正。

## ✨ 主要特点

- 🎵 **多格式支持**: WAV, MP3, M4A, FLAC, AAC, OGG, WMA
- 🌐 **多语言识别**: 中文、英文、自动检测
- 🔄 **繁简转换**: 自动将繁体中文转换为简体中文
- 🤖 **AI辅助修正**: 使用DeepSeek AI优化转录结果
- 📁 **批量处理**: 支持文件夹批量转录
- 🚀 **模型预下载**: 避免首次使用等待

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 安装FFmpeg（重要）
```bash
# 自动安装FFmpeg（推荐）
python install_ffmpeg.py

# 或手动下载安装
# 访问 https://ffmpeg.org/download.html
```
> ⚠️ **重要**: FFmpeg是处理MP3等音频格式的必需组件，不安装可能导致转录失败

### 3. 预下载模型（推荐）
```bash
# 快速下载基础模型（约181MB）
python quick_download.py

# 或使用完整下载工具
python download_models.py
```

### 4. 启动系统
```bash
# Windows用户
start.bat

# 或手动启动
python start.py
```

## 📖 使用说明

### 模型选择

| 模型 | 大小 | 速度 | 准确度 | 推荐用途 |
|------|------|------|--------|----------|
| tiny | ~39MB | 最快 | 较低 | 快速测试 |
| base | ~142MB | 快 | 平衡 | 日常使用 |
| small | ~466MB | 中等 | 较好 | 高质量需求 |
| medium | ~1.5GB | 慢 | 高 | 专业用途 |
| large | ~3.0GB | 最慢 | 最高 | 最高质量 |

### 音频建议

- **理想时长**: 5-10分钟
- **最大时长**: 15分钟
- **超过30分钟**: 建议分割处理
- **推荐格式**: WAV, MP3
- **注意**: MP3格式需要FFmpeg支持

## 🤖 AI辅助修正

### 配置DeepSeek API

1. 访问 [DeepSeek平台](https://platform.deepseek.com/) 获取API密钥
2. 在客户端点击"AI配置"按钮
3. 输入API密钥并启用功能
4. 保存配置

### 修正效果示例

**原始转录**: 你有什麼事沒聽清楚了換個方式再說一遍吧  
**AI修正后**: 你有什么事没听清楚了，换个方式再说一遍吧。

## 🛠️ 故障排除

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| 模型下载失败 | `python quick_download.py` |
| MP3文件无法处理 | `python install_ffmpeg.py` |
| 检查FFmpeg状态 | `python check_ffmpeg.py` |
| 转录超时 | 使用小模型，分割长音频 |
| 服务器无法启动 | 检查端口5000是否被占用 |
| AI修正失败 | 检查API密钥和网络连接 |

### 系统诊断
```bash
python diagnose.py
```

## �  文件结构

```
DeafEars/
├── server.py                    # 服务器端
├── client.py                    # 客户端GUI
├── start.py                     # 启动脚本
├── start.bat                    # Windows启动器
├── download_models.py           # 模型下载工具
├── quick_download.py            # 快速下载基础模型
├── diagnose.py                  # 系统诊断工具
├── install_ffmpeg.py           # FFmpeg安装助手
├── check_ffmpeg.py             # FFmpeg检查工具
├── config.json                  # 配置文件
├── requirements.txt             # 依赖包列表
├── README.md                   # 说明文档
└── ffmpeg/                     # FFmpeg本地安装
```

## 💻 系统要求

- Python 3.8+
- 内存: 2GB+ (推荐4GB+)
- 磁盘: 5GB可用空间
- 网络: 首次下载模型需要

## 📄 许可证

本项目仅供学习和研究使用。