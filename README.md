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
- **Docker 一键部署**：`docker compose up -d` 即可运行

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/youxiao240388/chat-case-to-doc.git
cd chat-case-to-doc
```

### 2. Docker 部署

```bash
docker compose up -d
```

### 3. 配置模型

首次访问 `http://localhost:2657` 会自动跳转到设置页面。

填入你的 API 配置（支持 DeepSeek / OpenAI / 通义千问等兼容 OpenAI 格式的 API）：

- **API 密钥**：你的 API Key
- **API 地址**：如 `https://api.deepseek.com`
- **模型名称**：如 `deepseek-chat`

视觉模型配置可选，留空则复用主模型配置。

### 4. 开始使用

配置完成后，回到首页即可上传文件生成案例文档。

## 📖 使用方法

1. 打开 Web 界面 `http://localhost:2657`
2. 点击右上角 ⚙️ 可随时修改模型配置
3. 上传文件（支持多选、拖拽）：
   - **截图**：群聊排障对话截图，按发送顺序排列
   - **PDF**：已有的排障文档或聊天记录导出
   - **文本**：复制粘贴的聊天记录
4. 选择 OCR 模式（仅截图时显示）：
   - **离线模式**：RapidOCR 本地识别
   - **视觉模型**：AI 模型识别
5. 点击「开始识别」
6. 预览结果，下载 Word 或 PDF

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

### 核心组件

| 组件 | 技术 | 说明 |
|------|------|------|
| Web 框架 | Flask | 轻量、易部署 |
| OCR | rapidocr-onnxruntime | 离线中文 OCR，无需 tesseract |
| PDF 解析 | pymupdf | 文本型 PDF 直接提取 |
| AI 提取 | OpenAI-compatible API | 兼容 DeepSeek/OpenAI/通义等 |
| Word 导出 | python-docx | 结构化 Word 文档 |
| PDF 导出 | weasyprint | HTML → PDF，支持中文 |

## 📁 项目结构

```
chat-case-to-doc/
├── app/
│   ├── main.py          # Flask 主应用
│   ├── settings.py      # 配置管理
│   ├── ocr.py           # OCR 处理（截图/扫描PDF）
│   ├── pdf_parser.py    # PDF 文本提取
│   ├── llm.py           # LLM 案例提取
│   ├── docx_export.py   # Word 文档生成
│   ├── pdf_export.py    # PDF 文档生成
│   └── templates/
│       ├── index.html   # 主界面
│       └── settings.html # 设置界面
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## ⚙️ 配置说明

### 端口

默认 `2657`，可在 `docker-compose.yml` 中修改：

```yaml
ports:
  - "8080:5000"  # 改为 8080
```

### 模型配置

所有模型配置通过 Web 界面管理，持久化存储在 `output/settings.json`。

支持的 API：
- DeepSeek：`https://api.deepseek.com`
- OpenAI：`https://api.openai.com`
- 通义千问：`https://dashscope.aliyuncs.com/compatible-mode/v1`
- 其他兼容 OpenAI 格式的 API

## 🔧 常见问题

### PDF 中文显示方块

Docker 镜像已内置 `fonts-noto-cjk` 字体，一般不会出现此问题。

### OCR 识别不准

- 确保截图清晰，分辨率不低于 720p
- 聊天截图建议包含完整对话，不要截断
- 图片按发送顺序排列（系统按文件修改时间排序）

### LLM 返回格式异常

系统已内置降级处理，会将原始文本作为描述输出。

## 📄 License

MIT
