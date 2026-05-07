# 聊天案例 → 文档生成器

> 从聊天截图、PDF 文档、纯文本中自动识别技术排障案例，生成结构化 Word + PDF 文档。

## ✨ 功能特性

- **多格式输入**：聊天截图（JPG/PNG）、PDF 文档、纯文本（TXT/MD/LOG）
- **智能 OCR**：使用 RapidOCR 识别中文聊天截图，准确率高
- **PDF 自动判断**：文本型 PDF 直接提取，扫描型 PDF 自动切换 OCR
- **AI 框例提取**：接入 DeepSeek 等 LLM，自动提取故障描述、排查步骤、根因、方案
- **双格式导出**：一键下载 Word (.docx) 和 PDF 文档
- **深色主题 UI**：拖拽上传，实时预览，一键下载
- **Docker 一键部署**：`docker compose up -d` 即可运行

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/chat-case-to-doc.git
cd chat-case-to-doc
```

### 2. 配置 LLM API

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

支持任何兼容 OpenAI 格式的 API（DeepSeek、OpenAI、通义千问等）：

```env
LLM_API_KEY=sk-your-api-key
LLM_API_BASE=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

### 3. Docker 部署

```bash
docker compose up -d
```

访问 `http://localhost:5000` 即可使用。

### 4. 本地开发（不用 Docker）

```bash
pip install -r requirements.txt
export LLM_API_KEY=sk-your-api-key
export LLM_API_BASE=https://api.deepseek.com
python -m app.main
```

## 📖 使用方法

1. 打开 Web 界面
2. 上传文件（支持多选、拖拽）：
   - **截图**：群聊排障对话截图，按发送顺序排列
   - **PDF**：已有的排障文档或聊天记录导出
   - **文本**：复制粘贴的聊天记录
3. 点击「开始识别」
4. 等待处理（OCR → AI 分析 → 文档生成）
5. 预览结果，下载 Word 或 PDF

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
│   ├── ocr.py           # OCR 处理（截图/扫描PDF）
│   ├── pdf_parser.py    # PDF 文本提取
│   ├── llm.py           # LLM 案例提取
│   ├── docx_export.py   # Word 文档生成
│   ├── pdf_export.py    # PDF 文档生成
│   └── templates/
│       └── index.html   # Web 界面
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## ⚙️ 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LLM_API_KEY` | - | LLM API 密钥（必填） |
| `LLM_API_BASE` | `https://api.deepseek.com` | API 地址 |
| `LLM_MODEL` | `deepseek-chat` | 模型名称 |

### 端口

默认 `5000`，可在 `docker-compose.yml` 中修改：

```yaml
ports:
  - "8080:5000"  # 改为 8080
```

## 🔧 常见问题

### PDF 中文显示方块

Docker 镜像已内置 `fonts-noto-cjk` 字体，一般不会出现此问题。如果仍有问题：

```bash
# 进入容器检查字体
docker exec chat-case-to-doc fc-list :lang=zh
```

### OCR 识别不准

- 确保截图清晰，分辨率不低于 720p
- 聊天截图建议包含完整对话，不要截断
- 图片按发送顺序排列（系统按文件修改时间排序）

### LLM 返回格式异常

DeepSeek 等模型偶尔会返回非 JSON 格式。系统已内置降级处理，会将原始文本作为描述输出。

## 📄 License

MIT
