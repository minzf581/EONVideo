from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


Platform = Literal["wechat_channels", "douyin", "xiaohongshu"]


class PublicationChannel(BaseModel):
    id: UUID
    name: str
    platform: Platform
    account_name: str
    api_enabled: bool = False


class CreatePublicationRequest(BaseModel):
    channel_id: UUID
    asset_id: Optional[UUID] = None
    platform: Platform
    published_url: str
    published_at: datetime
    notes: Optional[str] = None


class Publication(BaseModel):
    id: UUID
    topic_id: UUID
    channel_id: UUID
    platform: Platform
    platform_name: str
    topic_title: str
    published_url: str
    published_at: datetime
    status: str
    notes: Optional[str] = None


class PerformanceSnapshotCreate(BaseModel):
    hours_since_publish: int = Field(ge=1)
    data_source: Literal["manual", "platform_api"] = "manual"
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    favorite_count: int = 0
    completion_rate: Optional[float] = None
    avg_watch_seconds: Optional[float] = None
    profile_visit_count: int = 0
    follower_gain: int = 0
    dm_count: int = 0
    lead_count: int = 0


class PerformanceSnapshot(PerformanceSnapshotCreate):
    id: UUID
    publication_id: UUID
    captured_at: datetime


class PerformanceAnalysis(BaseModel):
    id: UUID
    publication_id: UUID
    topic_id: UUID
    snapshot_id: UUID
    performance_score: float
    engagement_rate: float
    lead_rate: float
    performance_label: str
    winning_factors: list[str]
    weak_points: list[str]
    recommendation: str
    prompt_learning_summary: str
    created_at: datetime
