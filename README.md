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

