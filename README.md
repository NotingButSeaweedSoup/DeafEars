# DeafEars

DeafEars（中文：你尔多🐉吗）是一个基于客户端-服务器架构的语音转文本系统，使用OpenAI Whisper进行音频转录，支持繁简转换。

## 系统架构

- **服务器端 (server.py)**: 提供REST API，处理音频转录任务
- **客户端 (client.py)**: 图形界面，与服务器交互
- **启动器 (start.py)**: 一键启动服务器和客户端
- **FFmpeg**: 本地集成，使用相对路径

## 功能特点

- 🎯 **C/S架构**: 服务器处理计算密集任务，客户端提供友好界面
- 🎵 **多格式支持**: WAV, MP3, M4A, FLAC, AAC, OGG, WMA
- 🌐 **多语言识别**: 中文、英文、自动检测
- 🔄 **繁简转换**: 自动将繁体中文转换为简体中文
- 🤖 **AI辅助修正**: 使用DeepSeek AI优化转录结果
- 📁 **批量处理**: 支持文件夹批量转录
- 💾 **结果管理**: 保存、复制、清空转录结果
- 🔄 **实时状态**: 显示服务器和模型状态
- 📦 **便携部署**: 使用相对路径，易于移植
- ⚙️ **配置管理**: 图形化配置DeepSeek API

## 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
```

### 2. 一键启动

**方法一: 使用批处理文件 (推荐)**
```bash
start.bat
```

**方法二: 使用Python脚本**
```bash
python start.py
```

**方法三: 手动启动**
```bash
# 终端1: 启动服务器
python server.py

# 终端2: 启动客户端
python client.py
```

## 使用说明

### 客户端界面

1. **服务器状态**: 显示服务器连接状态和模型加载情况
2. **模型设置**: 选择Whisper模型大小和识别语言
3. **单文件转录**: 选择单个音频文件进行转录
4. **批量转录**: 选择文件夹进行批量处理
5. **结果显示**: 查看转录结果，支持保存和复制
6. **繁简转换**: 自动显示简体和繁体对比

### 模型选择

| 模型 | 大小 | 速度 | 准确度 | 推荐用途 |
|------|------|------|--------|----------|
| tiny | ~39MB | 最快 | 较低 | 快速测试 |
| base | ~74MB | 快 | 平衡 | 日常使用 |
| small | ~244MB | 中等 | 较好 | 高质量需求 |
| medium | ~769MB | 慢 | 高 | 专业用途 |
| large | ~1550MB | 最慢 | 最高 | 最高质量 |

## AI辅助修正

系统集成了DeepSeek AI来优化转录结果，可以修正语法错误、标点符号和用词不当等问题。

### 配置DeepSeek API

1. **获取API密钥**: 访问 [DeepSeek平台](https://platform.deepseek.com/) 注册并获取API密钥
2. **打开AI配置**: 在客户端点击"AI配置"按钮
3. **输入API密钥**: 填入获取的API密钥
4. **启用功能**: 勾选"启用DeepSeek API"和"启用AI辅助修正"
5. **保存配置**: 点击"保存配置"

### 修正效果示例

**原始转录:**
```
你有什麼事沒聽清楚了換個方式再說一遍吧
```

**繁简转换:**
```
你有什么事没听清楚了换个方式再说一遍吧
```

**AI修正后:**
```
你有什么事没听清楚了，换个方式再说一遍吧。
```

### 配置选项

- **提示词模板**: 自定义AI修正的指令
- **最大令牌数**: 限制AI响应长度
- **温度**: 控制输出的随机性（0-1，越低越稳定）

## API接口

服务器提供以下REST API接口：

- `GET /api/status` - 获取服务器状态
- `POST /api/load_model` - 加载指定模型
- `POST /api/transcribe` - 上传文件转录
- `POST /api/transcribe_file` - 转录本地文件
- `POST /api/batch_transcribe` - 批量转录文件夹

## 文件结构

```
├── server.py                    # 服务器端
├── client.py                    # 客户端GUI
├── config_manager.py           # 配置管理器
├── start.py                     # Python启动脚本
├── start.bat                    # Windows批处理启动器
├── config.json                  # 配置文件
├── requirements.txt             # 依赖包列表
├── install_ffmpeg.py           # FFmpeg安装助手
├── ffmpeg/                     # FFmpeg本地安装
│   └── ffmpeg-master-latest-win64-gpl/
│       └── bin/
│           ├── ffmpeg.exe
│           ├── ffplay.exe
│           └── ffprobe.exe
└── README.md                   # 说明文档
```

## 故障排除

### 1. 依赖安装问题

```bash
# 更新pip
python -m pip install --upgrade pip

# 逐个安装
pip install openai-whisper
pip install flask flask-cors
pip install requests
pip install opencc-python-reimplemented
```

### 2. FFmpeg问题

```bash
# 自动安装FFmpeg
python install_ffmpeg.py

# 测试FFmpeg
python test_ffmpeg.py
```

### 3. 服务器启动失败

- 检查端口5000是否被占用
- 确保防火墙允许本地连接
- 查看服务器日志输出

### 4. 模型下载慢

- 首次使用会下载模型文件
- 可以手动下载到 `~/.cache/whisper/`
- 使用较小的模型进行测试

### 5. 繁简转换问题

```bash
# 测试繁简转换
python test_conversion.py
```

## 高级用法

### 自定义服务器地址

修改 `client.py` 中的 `server_url` 变量：

```python
self.server_url = "http://your-server:5000"
```

### 测试功能

系统提供完整的GUI界面进行测试：

1. **启动系统**: 运行 `start.bat` 或 `python start.py`
2. **配置AI**: 点击"配置管理"设置DeepSeek API（可选）
3. **选择文件**: 在GUI中选择MP3或其他音频文件
4. **开始转录**: 勾选"AI辅助修正"，点击转录按钮
5. **查看结果**: 对比原始转录、繁简转换和AI修正结果
6. **批量处理**: 选择文件夹进行批量转录

### 配置管理

```bash
# 单独运行配置管理器
python config_manager.py
```

## 系统要求

- Python 3.8+
- Windows/Linux/macOS
- 至少2GB内存 (推荐4GB+)
- 网络连接 (首次下载模型)

## 许可证

本项目仅供学习和研究使用。