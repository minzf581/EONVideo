from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


RenderJobStatus = Literal["pending", "processing", "completed", "failed"]


class VideoJobPayload(BaseModel):
    topic_id: UUID
    title: str
    subtitle: str = "国际资本市场观察"
    script: str
    bullets: list[str] = Field(default_factory=list)
    brandName: str = "EONVideo Capital Brief"
    cta: str = "关注账号，了解更多海外融资与新加坡资本市场观察。"
    durationSeconds: int = Field(default=60, ge=15, le=180)
    fps: int = Field(default=30, ge=24, le=60)
    template: str = "CapitalNews"
    style: str = "finance_advisory"
    targetPlatform: str = "douyin"
    coverTitle: str = ""
    scriptType: str = "60s"


class VideoJobCreateRequest(BaseModel):
    payload: VideoJobPayload


class VideoJobUpdateRequest(BaseModel):
    payload: VideoJobPayload


class VideoJob(BaseModel):
    id: UUID
    status: RenderJobStatus
    payload: VideoJobPayload
    video_url: str | None = None
    error_message: str | None = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
