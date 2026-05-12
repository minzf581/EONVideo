# 每日 AI 热点短视频生产系统

面向财经、AI、IPO、RWA、新加坡/香港资本市场、企业出海和家族办公室相关热点的短视频生产系统。

## 当前 MVP

- FastAPI 后端骨架
- PostgreSQL 数据模型草案
- React + Tailwind 审核后台
- 发布效果反馈模块
- 支持平台：微信视频号、抖音、小红书
- Remotion 竖屏财经短视频模板占位

## 目录

```text
apps/
  api/        FastAPI 后端
  web/        React + Tailwind 前端
  remotion/   Remotion 视频模板
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

## 关键页面

- `http://localhost:5173/review/topics`: 选题审核
- `http://localhost:5173/publications`: 发布反馈
- `http://localhost:5173/performance`: 内容表现分析
