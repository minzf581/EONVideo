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
    script_type: Literal["30s", "60s"]
    full_script: str
    estimated_duration_seconds: int


class Topic(BaseModel):
    id: UUID
    production_date: date
    status: TopicStatus
    category: str
    score: float = Field(ge=0, le=100)
    risk_score: float = Field(ge=0, le=100)
    topic_title: str
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


class GenerateDailyTopicsRequest(BaseModel):
    production_date: date
    count: int = Field(default=10, ge=1, le=20)
    categories: list[str] = []
    style: str = "finance_investment_banking_advisor"
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
