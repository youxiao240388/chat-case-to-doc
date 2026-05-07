# Docker 部署教程

## 一、群晖 NAS 部署（推荐）

### 1. 打开 Container Manager

群晖套件中心安装 **Container Manager**（DSM 7.2+）或 **Docker**（DSM 7.1 以下）。

### 2. 创建项目

1. 打开 Container Manager → 左侧选择「项目」
2. 点击「新建」
3. 项目名称填：`chat-case-to-doc`
4. 来源选择：「创建 docker-compose.yml」
5. 将下面的 YAML 粘贴到编辑器中

### 3. Docker Compose 配置

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

### 4. 启动

点击「下一步」→「完成」，等待容器启动（约 10-30 秒）。

### 5. 访问

浏览器打开 `http://群晖IP:2657`

首次访问会自动跳转到设置页面，填入你的 LLM API 配置：

| 配置项 | 示例值 | 说明 |
|--------|--------|------|
| API 密钥 | `sk-xxx` | DeepSeek / OpenAI 等 |
| API 地址 | `https://api.deepseek.com` | 兼容 OpenAI 格式 |
| 模型名称 | `deepseek-chat` | 支持视觉的模型 |

### 6. 使用

1. 上传截图/PDF/文本
2. 选择 OCR 模式（截图时显示）
3. 点击「开始识别」
4. 下载 Word/PDF 文档

---

## 二、普通 Docker 部署

### 前提条件

- Docker 20.10+
- Docker Compose v2

### 部署步骤

```bash
# 创建项目目录
mkdir -p /opt/chat-case-to-doc
cd /opt/chat-case-to-doc

# 创建 docker-compose.yml（内容同上）

# 启动
docker compose up -d

# 查看日志
docker compose logs -f
```

---

## 三、本地构建部署

如果需要自定义镜像：

```bash
# 克隆项目
git clone https://github.com/youxiao240388/chat-case-to-doc.git
cd chat-case-to-doc

# 构建镜像
docker build -t chat-case-to-doc .

# 启动
docker compose up -d
```

---

## 四、配置说明

### 端口修改

默认端口 `2657`，修改方法：

```yaml
ports:
  - "8080:5000"  # 改为 8080
```

### 数据持久化

- **配置文件**：Docker Volume `chat-case-data` 中的 `settings.json`
- **生成文档**：Docker Volume `chat-case-data` 中的 `results/` 目录

容器重建不会丢失数据。

### 资源占用

- 内存：约 200-500MB（取决于并发）
- CPU：空闲时接近 0，处理时根据文件大小
- 磁盘：镜像约 800MB，数据按使用量增长

---

## 五、常见问题

### Q: 端口被占用？

修改 `docker-compose.yml` 中的端口映射，如 `"8080:5000"`。

### Q: 如何更新？

```bash
docker compose pull
docker compose up -d
```
数据不会丢失（存储在 Volume 中）。

### Q: 如何备份？

```bash
docker run --rm -v chat-case-data:/data -v $(pwd):/backup alpine tar czf /backup/chat-case-backup.tar.gz -C /data .
```

### Q: OCR 识别不准？

- 确保截图清晰（≥720p）
- 图片按时间顺序排列
- 尝试切换「视觉模型」模式

### Q: PDF 中文乱码？

镜像已内置 `fonts-noto-cjk` 字体，一般不会出现此问题。

### Q: 容器启动失败？

常见原因：
- 网络问题导致镜像拉取失败（可尝试配置镜像源）
- 端口被占用（修改端口映射）
- 群晖内存不足（关闭其他容器释放内存）

查看日志排查：
```bash
docker logs chat-case-to-doc
```

---

## 六、支持的 API

| 服务商 | API 地址 | 模型示例 |
|--------|----------|----------|
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` |
| OpenAI | `https://api.openai.com` | `gpt-4o` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| 智谱 AI | `https://open.bigmodel.cn/api/paas/v4` | `glm-4` |

所有兼容 OpenAI 格式的 API 均可使用。
