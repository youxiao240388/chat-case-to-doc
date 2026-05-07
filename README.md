     1|# 聊天案例 → 文档生成器
     2|
     3|> 从聊天截图、PDF 文档、纯文本中自动识别技术排障案例，生成结构化 Word + PDF 文档。
     4|
     5|## ✨ 功能特性
     6|
     7|- **多格式输入**：聊天截图（JPG/PNG）、PDF 文档、纯文本（TXT/MD/LOG）
     8|- **双模式 OCR**：
     9|  - 📴 **离线模式**：RapidOCR 本地识别，无需网络，速度快
    10|  - 🤖 **视觉模型**：AI 模型识别，准确率更高，支持复杂排版
    11|- **PDF 自动判断**：文本型 PDF 直接提取，扫描型 PDF 自动切换 OCR
    12|- **AI 案例提取**：接入 DeepSeek 等 LLM，自动提取故障描述、排查步骤、根因、方案
    13|- **双格式导出**：一键下载 Word (.docx) 和 PDF 文档
    14|- **Web 配置**：模型配置在 Web 界面完成，无需修改配置文件
    15|- **深色主题 UI**：拖拽上传，实时预览，一键下载
    16|- **一键部署**：复制 YAML 即可运行，无需手动操作
    17|
    18|## 🚀 一键部署
    19|
    20|### 群晖 NAS / Docker
    21|
    22|直接复制下面的 YAML 到 Container Manager：
    23|
    24|```yaml
    25|services:
    26|  chat-case-to-doc:
    27|    image: python:3.11-slim
    28|    container_name: chat-case-to-doc
    29|    ports:
    30|      - "2657:5000"
    31|    volumes:
    32|      - chat-case-data:/app/output
    33|    environment:
    34|      - TZ=Asia/Shanghai
    35|    entrypoint: ["/bin/bash", "-c"]
    36|    command:
    37|      - |
    38|        set -e
    39|        echo "=== 安装系统依赖 ==="
    40|        apt-get update -qq
    41|        apt-get install -y -qq --no-install-recommends libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2 fonts-noto-cjk curl git > /dev/null
    42|        echo "=== 下载项目代码 ==="
    43|        cd /app
    44|        git clone --depth 1 https://github.com/youxiao240388/chat-case-to-doc.git /tmp/chat-case-to-doc
    45|        cp -r /tmp/chat-case-to-doc/app/* ./app/
    46|        rm -rf /tmp/chat-case-to-doc
    47|        echo "=== 安装 Python 依赖 ==="
    48|        pip install -q flask gunicorn rapidocr-onnxruntime pymupdf python-docx weasyprint openai python-dotenv werkzeug
    49|        echo "=== 创建目录 ==="
    50|        mkdir -p /app/output/uploads /app/output/results
    51|        echo "=== 启动服务 ==="
    52|        exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app.main:app
    53|    restart: unless-stopped
    54|
    55|volumes:
    56|  chat-case-data:
    57|```
    58|
    59|**首次启动**：约 3-5 分钟（下载依赖），后续秒启动。
    60|
    61|### 访问
    62|
    63|启动后访问 `http://你的IP:2657`，首次会自动跳转到设置页面配置 LLM API。
    64|
    65|## 📖 使用方法
    66|
    67|1. 打开 Web 界面 `http://localhost:2657`
    68|2. 点击右上角 ⚙️ 可随时修改模型配置
    69|3. 上传文件（支持多选、拖拽）：
    70|   - **截图**：群聊排障对话截图，按发送顺序排列
    71|   - **PDF**：已有的排障文档或聊天记录导出
    72|   - **文本**：复制粘贴的聊天记录
    73|4. 选择 OCR 模式（仅截图时显示）
    74|5. 点击「开始识别」
    75|6. 预览结果，下载 Word 或 PDF
    76|
    77|## ⚙️ 配置说明
    78|
    79|所有模型配置通过 Web 界面管理（右上角 ⚙️），持久化存储在 Docker Volume 中。
    80|
    81|支持的 API：
    82|- DeepSeek：`https://api.deepseek.com`
    83|- OpenAI：`https://api.openai.com`
    84|- 通义千问：`https://dashscope.aliyuncs.com/compatible-mode/v1`
    85|- 其他兼容 OpenAI 格式的 API
    86|
    87|## 🏗️ 技术架构
    88|
    89|```
    90|┌─────────────┐     ┌──────────────┐     ┌─────────────┐
    91|│  Web 上传    │────▶│  内容提取     │────▶│  AI 分析     │
    92|│  Flask UI    │     │  OCR/PDF/文本 │     │  LLM 提取    │
    93|└─────────────┘     └──────────────┘     └──────┬──────┘
    94|                                                │
    95|                                         ┌──────▼──────┐
    96|                                         │  文档生成    │
    97|                                         │  Word + PDF  │
    98|                                         └─────────────┘
    99|```
   100|
   101|## 📁 项目结构
   102|
   103|```
   104|chat-case-to-doc/
   105|├── app/
   106|│   ├── main.py          # Flask 主应用
   107|│   ├── settings.py      # 配置管理
   108|│   ├── ocr.py           # OCR 处理
   109|│   ├── pdf_parser.py    # PDF 文本提取
   110|│   ├── llm.py           # LLM 案例提取
   111|│   ├── docx_export.py   # Word 文档生成
   112|│   ├── pdf_export.py    # PDF 文档生成
   113|│   └── templates/
   114|│       ├── index.html   # 主界面
   115|│       └── settings.html # 设置界面
   116|├── Dockerfile           # 本地构建用
   117|├── docker-compose.yml   # 一键部署
   118|└── README.md
   119|```
   120|
   121|## 🔧 常见问题
   122|
   123|### 首次启动慢
   124|
   125|首次需要下载 Python 依赖，约 3-5 分钟。后续重启秒启动。
   126|
   127|### 端口冲突
   128|
   129|如果 2657 端口被占用，修改 YAML 中的端口映射：
   130|```yaml
   131|ports:
   132|  - "8080:5000"  # 改为你想要的端口
   133|```
   134|
   135|### 数据持久化
   136|
   137|配置和生成的文档都存储在 Docker Volume `chat-case-data` 中，容器重建不会丢失。
   138|
   139|## 📄 License
   140|
   141|MIT
   142|