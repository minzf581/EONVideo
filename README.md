# 中国老板全球化资本趋势短视频系统

面向中国企业老板、准备融资企业、IPO 辅导机构、高净值家庭和国际资本顾问场景的短视频生产系统。系统不做“国际新闻翻译”，而是把国内短视频平台热点转译成企业全球化、海外融资、新加坡资本市场、香港 IPO、家族办公室、RWA 和全球资产配置相关的资本逻辑。

## 当前 MVP

- FastAPI 后端骨架
- PostgreSQL 数据模型草案
- React + Tailwind 审核后台
- 发布效果反馈模块
- 支持平台：微信视频号、抖音、小红书
- Remotion 竖屏财经短视频模板占位
- 热点采集优先级：抖音/视频号/公众号/小红书等中文平台方向优先，国际媒体仅作为辅助视角
- 新增中国老板相关度、企业全球化相关度、海外资本相关度、平台传播潜力等评分字段
- 自动生成抖音版、视频号版、小红书版脚本

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

## 热点采集与选题方向

点击“生成今日 10 个选题”时，后端会优先按“中国老板关注的国际资本与企业全球化”方向抓取和排序热点。当前 MVP 使用公开可访问入口模拟国内平台热点方向；后续接入抖音、视频号、小红书、公众号、雪球等数据接口时，沿用同一套字段和评分模型。

热点源权重：

- 抖音热点、抖音财经、趋势榜、搜索热词、热门评论关键词：40%
- 微信视频号财经/企业家内容、微信公众号财经文章：25%
- 小红书商业/海外资产/新加坡/家办/企业出海内容：20%
- 百度热搜、微博财经、雪球讨论：10%
- Bloomberg、Reuters、CNBC、WSJ、Financial Times：5%，仅用于国际视角校准

选题链路：

```text
热点 -> 中国老板痛点 -> 资本逻辑 -> 企业全球化影响 -> 海外融资/新加坡/家办/RWA 切入点
```

如果公开热点源暂时不可用，后端会直接返回错误，不再回退到本地种子选题。Prompt 方案见 [china_boss_global_capital.md](/Users/minzhenfa/sourceCode/EONVideo/apps/api/app/prompts/china_boss_global_capital.md)。

当前仍需要你提供或确认可用的数据接口：

- 抖音热点/财经热点/趋势榜/搜索热词/评论关键词接口
- 视频号热门财经/企业家内容接口，或公众号文章源
- 小红书商业/海外资产/企业出海内容接口
- 百度热搜、微博财经、雪球热门讨论接口

## 中文财经热点选题引擎

后端已在原有 `news_ingestion` 选题引擎中加入 Source Adapter 架构，位置：

```text
apps/api/app/services/source_adapters/
  baidu_hotsearch.py
  weibo_hotsearch.py
  finance_news.py
  wechat_article_source.py
  third_party_hot_api.py
  manual_seed_source.py
```

每条热点会统一转成：

```json
{
  "platform": "weibo",
  "title": "热点标题",
  "url": "https://example.com",
  "heat_score": 88,
  "published_at": "2026-05-13T10:00:00+08:00",
  "keywords": ["IPO", "融资"],
  "category": "hongkong_ipo",
  "raw": {}
}
```

环境变量：

```text
HOT_API_BASE_URL=
HOT_API_KEY=
WECHAT_SOURCE_CONFIG=[]
MANUAL_SEED_KEYWORDS=新加坡家族办公室,红筹架构IPO,企业出海海外融资
FINANCE_NEWS_RSS_URLS=
```

`WECHAT_SOURCE_CONFIG` 使用 JSON 数组，例如：

```json
[
  {
    "name": "IPO早知道",
    "url": "https://example.com/rss.xml",
    "category": "hongkong_ipo",
    "keywords": ["IPO", "上市", "融资"]
  }
]
```

## 关键页面

- `http://localhost:5173/review/topics`: 选题审核
- `http://localhost:5173/publications`: 发布反馈
- `http://localhost:5173/performance`: 内容表现分析
