# 每日 AI 热点短视频生产系统

面向财经、AI、IPO、RWA、新加坡/香港资本市场、企业出海和家族办公室相关热点的短视频生产系统。

## 当前 MVP

- FastAPI 后端骨架
- PostgreSQL 数据模型草案
- React + Tailwind 审核后台
- 发布效果反馈模块
- 支持平台：微信视频号、抖音、小红书
- Remotion 竖屏财经短视频模板占位
- 真实 RSS 热点采集：Google News RSS、MAS RSS、HKEX RSS 等公开源

## 目录

```text
apps/
  api/        FastAPI 后端
  web/        React + Tailwind 前端
  remotion/   Remotion 视频模板
  remotion-worker/ Railway Remotion 渲染 Worker
db/           SQL 初始化脚本
docs/         产品与架构文档
```

## 本地启动

```bash
docker compose up -d postgres
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```bash
cd apps/web
npm install
npm run dev
```

```bash
cd apps/remotion
npm install
npm run preview
```

```bash
cd apps/remotion-worker
npm install
npm run build
npm run worker
```

## Railway 部署

### 后端 API 服务

Root Directory 设为：

```text
apps/api
```

Railpack 会读取 [apps/api/railpack.json](</Users/lewis_1/source code/EONVideo/apps/api/railpack.json>) 并使用以下启动命令：

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Railway 会自动注入 `$PORT`，不需要手动写死端口。

后端服务根路径 `/` 只用于确认 API 正常运行，真正的 React 审核后台需要部署前端服务。

### 前端 Web 服务

新增一个 Railway Service，Root Directory 设为：

```text
apps/web
```

构建命令：

```bash
npm run build
```

启动命令由 [apps/web/railpack.json](</Users/lewis_1/source code/EONVideo/apps/web/railpack.json>) 指定：

```bash
npm run start
```

前端服务需要配置环境变量，指向后端 API 服务：

```text
VITE_API_BASE=https://你的后端服务域名/api/v1
```

如果你只有一个 Railway 服务且 Root Directory 是 `apps/api`，打开域名看到的是 API 状态页，不会是 React 审核后台。

### Remotion Worker 服务

新增一个 Railway Service，Root Directory 设为：

```text
apps/remotion-worker
```

该服务不提供 HTTP 端口，只轮询 PostgreSQL 的 `render_jobs` 表。

必需环境变量：

```text
DATABASE_URL=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=
R2_PUBLIC_BASE_URL=
WORKER_CONCURRENCY=1
```

Worker 行为：

- 每 5 秒领取一条 `status='pending'` 的任务
- 使用 `for update skip locked` 防止重复领取
- 使用 Remotion 模板 `CapitalNews` 渲染 1080x1920 MP4
- 临时文件写入 `/tmp/{job_id}.mp4`
- 上传到 Cloudflare R2
- 成功后更新 `video_url` 和 `completed_at`
- 失败后写入 `error_message` 并递增 `retry_count`

`payload` 示例：

```json
{
  "title": "新加坡资本市场新信号",
  "subtitle": "中国企业出海融资，需要重新审视资本结构",
  "script": "这是一条财经短视频脚本。",
  "bullets": ["海外融资", "资本结构", "投资人沟通"],
  "brandName": "EONVideo Capital Brief",
  "cta": "关注账号，了解更多海外融资观察。",
  "durationSeconds": 60,
  "fps": 30
}
```

## 真实热点采集

点击“生成今日 10 个选题”时，后端会优先从公开 RSS 源抓取最新新闻，再按业务相关度生成审核选题。

当前内置方向：

- AI / 科技融资
- 新加坡资本市场
- 香港 IPO
- RWA / 资产代币化
- 新加坡家族办公室
- 中国企业出海
- 海外融资与全球化资本结构

如果公开 RSS 源暂时不可用，系统会回退到本地种子选题，避免线上页面空白。

后续接入 OpenAI 后，可以把 `apps/api/app/services/news_ingestion.py` 里的规则生成替换为模型生成。

## 关键页面

- `http://localhost:5173/review/topics`: 选题审核
- `http://localhost:5173/publications`: 发布反馈
- `http://localhost:5173/performance`: 内容表现分析
