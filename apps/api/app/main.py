from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response

from app.api.publications import router as publications_router
from app.api.topics import router as topics_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics_router, prefix=settings.api_prefix)
app.include_router(publications_router, prefix=settings.api_prefix)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
    <!doctype html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>EONVideo API</title>
        <style>
          body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            background: #f7f8fa;
            color: #111827;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }
          main {
            width: min(720px, calc(100vw - 40px));
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            background: white;
            padding: 32px;
            box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
          }
          h1 { margin: 0; font-size: 28px; }
          p { color: #4b5563; line-height: 1.7; }
          a { color: #0f766e; font-weight: 700; text-decoration: none; }
          .links { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 24px; }
        </style>
      </head>
      <body>
        <main>
          <h1>EONVideo API is running</h1>
          <p>
            当前 Railway 服务是 FastAPI 后端。前端 React 审核后台需要作为独立 Railway
            服务部署，Root Directory 设置为 <strong>apps/web</strong>。
          </p>
          <div class="links">
            <a href="/docs">API Docs</a>
            <a href="/health">Health Check</a>
            <a href="/api/v1/topics">Topics API</a>
          </div>
        </main>
      </body>
    </html>
    """


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)
