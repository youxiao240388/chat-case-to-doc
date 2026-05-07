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
- **一键部署**：复制 YAML 即可运行，镜像已预装所有依赖

## 🚀 一键部署

### 群晖 NAS / Docker

直接复制下面的 YAML 到 Container Manager：

```yaml
version: '3.8'
services:
  chat-case-to-doc:
    image: ghcr.io/youxiao240388/chat-case-to-doc:latest
    container_name: chat-case-to-doc
    ports:
      - "2657:5000"
    volumes:
      - chat-case-data:/app/output
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped

volumes:
  chat-case-data:
```

**就这么简单！** 镜像已预装所有依赖，秒启动。

### 访问

启动后访问 `http://你的IP:2657`

首次访问会自动跳转到设置页面，填入你的 LLM API 配置。

## 📖 使用方法

1. 打开 Web 界面 `http://localhost:2657`
2. 点击右上角 ⚙️ 配置模型（DeepSeek / OpenAI 等）
3. 上传文件（截图/PDF/文本）
4. 选择 OCR 模式（截图时显示）
5. 点击「开始识别」
6. 下载 Word 或 PDF

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
├── app/                    # 应用代码
│   ├── main.py             # Flask 主应用
│   ├── settings.py         # 配置管理
│   ├── ocr.py              # 双模式 OCR
│   ├── pdf_parser.py       # PDF 解析
│   ├── llm.py              # LLM 案例提取
│   ├── docx_export.py      # Word 导出
│   ├── pdf_export.py       # PDF 导出
│   └── templates/
├── .github/workflows/      # GitHub Actions 自动构建
├── Dockerfile              # 镜像构建文件
├── docker-compose.yml      # 一键部署配置
└── README.md
```

## 🔧 常见问题

### Q: 端口被占用？

A: 修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8080:5000"  # 改为你想要的端口
```

### Q: 如何更新？

A: 拉取最新镜像后重建：
```bash
docker compose pull
docker compose up -d
```
数据不会丢失（存储在 Volume 中）。

### Q: 如何备份？

A: 备份 Docker Volume：
```bash
docker run --rm -v chat-case-data:/data -v $(pwd):/backup alpine tar czf /backup/chat-case-backup.tar.gz -C /data .
```

### Q: OCR 识别不准？

A: 
- 确保截图清晰（≥720p）
- 图片按时间顺序排列
- 尝试切换「视觉模型」模式

## 📄 License

MIT
