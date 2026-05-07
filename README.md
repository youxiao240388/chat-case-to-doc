# 聊天案例 → 文档生成器

> 从聊天截图、PDF 文档、纯文本中自动识别技术排障案例，生成结构化 Word + PDF 文档。

## ✨ 功能特性

- **多格式输入**：聊天截图（JPG/PNG）、PDF 文档、纯文本（TXT/MD/LOG）
- **双模式 OCR**：
  - 📴 **离线模式**：RapidOCR 本地识别，无需网络，速度快
  - 🤖 **视觉模型**：AI 模型识别，准确率更高，支持复杂排版
- **PDF 自动判断**：文本型 PDF 直接提取，扫描型 PDF 自动切换 OCR
- **AI 案例提取**：接入 DeepSeek 等 LLM，自动提取故障描述、排查步骤、根因、方案
- **双格式导出**：一键下载 Word (.docx) 和 PDF 文档
- **Web 配置**：模型配置在 Web 界面完成，无需修改配置文件
- **深色主题 UI**：拖拽上传，实时预览，一键下载
- **一键部署**：复制 YAML 即可运行，无需手动操作

## 🚀 一键部署

### 群晖 NAS / Docker

直接复制下面的 YAML 到 Container Manager：

```yaml
services:
  chat-case-to-doc:
    image: python:3.11-slim
    container_name: chat-case-to-doc
    ports:
      - "2657:5000"
    volumes:
      - chat-case-data:/app/output
    environment:
      - TZ=Asia/Shanghai
    command: >
      bash -c "
      echo '=== 安装系统依赖 ===' &&
      apt-get update -qq &&
      apt-get install -y -qq --no-install-recommends 
        libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 
        libffi-dev libcairo2 fonts-noto-cjk curl git > /dev/null &&
      echo '=== 下载项目代码 ===' &&
      cd /app &&
      git clone --depth 1 https://github.com/youxiao240388/chat-case-to-doc.git /tmp/chat-case-to-doc &&
      cp -r /tmp/chat-case-to-doc/app/* ./app/ &&
      rm -rf /tmp/chat-case-to-doc &&
      echo '=== 安装 Python 依赖 ===' &&
      pip install -q flask gunicorn rapidocr-onnxruntime pymupdf python-docx weasyprint openai python-dotenv werkzeug &&
      echo '=== 创建目录 ===' &&
      mkdir -p /app/output/uploads /app/output/results &&
      echo '=== 启动服务 ===' &&
      exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app.main:app
      "
    restart: unless-stopped

volumes:
  chat-case-data:
```

**首次启动**：约 3-5 分钟（下载依赖），后续秒启动。

### 访问

启动后访问 `http://你的IP:2657`，首次会自动跳转到设置页面配置 LLM API。

## 📖 使用方法

1. 打开 Web 界面 `http://localhost:2657`
2. 点击右上角 ⚙️ 可随时修改模型配置
3. 上传文件（支持多选、拖拽）：
   - **截图**：群聊排障对话截图，按发送顺序排列
   - **PDF**：已有的排障文档或聊天记录导出
   - **文本**：复制粘贴的聊天记录
4. 选择 OCR 模式（仅截图时显示）
5. 点击「开始识别」
6. 预览结果，下载 Word 或 PDF

## ⚙️ 配置说明

所有模型配置通过 Web 界面管理（右上角 ⚙️），持久化存储在 Docker Volume 中。

支持的 API：
- DeepSeek：`https://api.deepseek.com`
- OpenAI：`https://api.openai.com`
- 通义千问：`https://dashscope.aliyuncs.com/compatible-mode/v1`
- 其他兼容 OpenAI 格式的 API

## 🏗️ 技术架构

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Web 上传    │────▶│  内容提取     │────▶│  AI 分析     │
│  Flask UI    │     │  OCR/PDF/文本 │     │  LLM 提取    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                         ┌──────▼──────┐
                                         │  文档生成    │
                                         │  Word + PDF  │
                                         └─────────────┘
```

## 📁 项目结构

```
chat-case-to-doc/
├── app/
│   ├── main.py          # Flask 主应用
│   ├── settings.py      # 配置管理
│   ├── ocr.py           # OCR 处理
│   ├── pdf_parser.py    # PDF 文本提取
│   ├── llm.py           # LLM 案例提取
│   ├── docx_export.py   # Word 文档生成
│   ├── pdf_export.py    # PDF 文档生成
│   └── templates/
│       ├── index.html   # 主界面
│       └── settings.html # 设置界面
├── Dockerfile           # 本地构建用
├── docker-compose.yml   # 一键部署
└── README.md
```

## 🔧 常见问题

### 首次启动慢

首次需要下载 Python 依赖，约 3-5 分钟。后续重启秒启动。

### 端口冲突

如果 2657 端口被占用，修改 YAML 中的端口映射：
```yaml
ports:
  - "8080:5000"  # 改为你想要的端口
```

### 数据持久化

配置和生成的文档都存储在 Docker Volume `chat-case-data` 中，容器重建不会丢失。

## 📄 License

MIT
