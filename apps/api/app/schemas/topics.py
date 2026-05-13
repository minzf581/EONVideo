from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


TopicStatus = Literal[
    "draft",
    "pending_review",
    "approved",
    "rejected",
    "revision_requested",
    "video_draft_generated",
    "final_rendered",
    "published",
    "metrics_pending",
    "metrics_collected",
    "performance_analyzed",
]


class TopicScript(BaseModel):
    script_type: Literal["30s", "60s", "douyin", "wechat_channels", "xiaohongshu"]
    full_script: str
    estimated_duration_seconds: int


class VideoAsset(BaseModel):
    asset_type: Literal["mp4", "srt", "cover", "publish_copy", "remotion_json"]
    file_name: str
    download_url: str
    render_status: Literal["pending", "completed", "failed"] = "completed"


class Topic(BaseModel):
    id: UUID
    production_date: date
    status: TopicStatus
    category: str
    score: float = Field(ge=0, le=100)
    risk_score: float = Field(ge=0, le=100)
    topic_emotion: str = "机会"
    china_boss_relevance_score: float = Field(default=0, ge=0, le=100)
    enterprise_globalization_score: float = Field(default=0, ge=0, le=100)
    overseas_capital_score: float = Field(default=0, ge=0, le=100)
    wechat_channels_potential_score: float = Field(default=0, ge=0, le=100)
    douyin_potential_score: float = Field(default=0, ge=0, le=100)
    comment_controversy_score: float = Field(default=0, ge=0, le=100)
    collection_value_score: float = Field(default=0, ge=0, le=100)
    international_news_score: float = Field(default=0, ge=0, le=100)
    topic_title: str
    hot_source: str = ""
    why_short_video: str = ""
    recommended_script_angle: str = ""
    hot_summary: str
    target_client: str
    user_pain_point: str
    business_entry_point: str
    cover_title: str
    risk_notice: str
    publish_copy: str
    tags: list[str]
    scripts: list[TopicScript]
    created_at: datetime
    assets: list[VideoAsset] = []


class GenerateDailyTopicsRequest(BaseModel):
    production_date: date
    count: int = Field(default=20, ge=1, le=20)
    categories: list[str] = []
    style: str = "china_boss_global_capital_advisor"
    use_performance_learning: bool = True


class ReviewRequest(BaseModel):
    comment: Optional[str] = None


class TopicUpdateRequest(BaseModel):
    topic_title: Optional[str] = None
    target_client: Optional[str] = None
    user_pain_point: Optional[str] = None
    business_entry_point: Optional[str] = None
    cover_title: Optional[str] = None
    risk_notice: Optional[str] = None
    publish_copy: Optional[str] = None


class ScriptUpdateRequest(BaseModel):
    script_type: Literal["30s", "60s", "douyin", "wechat_channels", "xiaohongshu"]
    full_script: str


class VideoDraftRequest(BaseModel):
    script_type: Literal["30s", "60s", "douyin", "wechat_channels", "xiaohongshu"] = "60s"
    template: str = "finance_advisory_dark"


class VideoDraftResponse(BaseModel):
    topic: Topic
    assets: list[VideoAsset]
    message: str
