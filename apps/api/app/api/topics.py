from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from typing import Optional

from app.schemas.topics import (
    GenerateDailyTopicsRequest,
    ReviewRequest,
    ScriptUpdateRequest,
    Topic,
    TopicStatus,
    TopicUpdateRequest,
    VideoDraftRequest,
    VideoDraftResponse,
)
from app.schemas.video_jobs import VideoJob, VideoJobCreateRequest, VideoJobUpdateRequest
from app.services import mock_store
from app.services.news_ingestion import generate_live_topics
from app.services.render_jobs import create_job, list_jobs, retry_job, update_job
from app.services.video_assets import generate_assets

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("", response_model=list[Topic])
def list_topics(status: Optional[TopicStatus] = Query(default=None)) -> list[Topic]:
    return mock_store.list_topics(status)


@router.post("/generate-daily", response_model=list[Topic])
async def generate_daily_topics(payload: GenerateDailyTopicsRequest) -> list[Topic]:
    try:
        live_topics = await generate_live_topics(payload.count)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "热点采集失败，后端不会使用 mock 选题兜底。"
                "请接入可用的抖音/视频号/公众号/小红书/热搜数据接口后重试。"
            ),
        ) from exc
    if not live_topics:
        raise HTTPException(
            status_code=503,
            detail=(
                "当前没有采集到可用于生成选题的真实热点，后端不会使用 mock 选题兜底。"
                "请提供可用热点接口或手动导入真实热点数据。"
            ),
        )
    mock_store.replace_topics(live_topics)
    return live_topics


@router.get("/{topic_id}", response_model=Topic)
def get_topic(topic_id: UUID) -> Topic:
    try:
        return mock_store.get_topic(topic_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc


@router.patch("/{topic_id}", response_model=Topic)
def update_topic(topic_id: UUID, payload: TopicUpdateRequest) -> Topic:
    try:
        return mock_store.update_topic(topic_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc


@router.patch("/{topic_id}/scripts", response_model=Topic)
def update_script(topic_id: UUID, payload: ScriptUpdateRequest) -> Topic:
    try:
        return mock_store.update_script(topic_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc


@router.post("/{topic_id}/approve", response_model=Topic)
def approve_topic(topic_id: UUID, payload: Optional[ReviewRequest] = None) -> Topic:
    try:
        return mock_store.set_topic_status(topic_id, "approved")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc


@router.post("/{topic_id}/reject", response_model=Topic)
def reject_topic(topic_id: UUID, payload: Optional[ReviewRequest] = None) -> Topic:
    try:
        return mock_store.set_topic_status(topic_id, "rejected")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc


@router.post("/{topic_id}/request-revision", response_model=Topic)
def request_revision(topic_id: UUID, payload: Optional[ReviewRequest] = None) -> Topic:
    try:
        return mock_store.set_topic_status(topic_id, "revision_requested")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc


@router.post("/{topic_id}/video-draft", response_model=VideoDraftResponse)
def generate_video_draft(topic_id: UUID, payload: VideoDraftRequest) -> VideoDraftResponse:
    try:
        topic = mock_store.get_topic(topic_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc
    if topic.status not in {"approved", "video_draft_generated"}:
        raise HTTPException(status_code=400, detail="Approve the topic before generating a video draft")
    assets = generate_assets(topic, payload.script_type, payload.template)
    updated = mock_store.set_topic_assets(topic_id, assets)
    return VideoDraftResponse(
        topic=updated,
        assets=assets,
        message="已生成视频草稿资产：Remotion JSON、SRT 字幕、封面文案、发布文案。MP4 云端渲染待接入 Remotion Worker。",
    )


@router.post("/{topic_id}/render-final", response_model=dict)
def render_final(topic_id: UUID) -> dict:
    try:
        topic = mock_store.set_topic_status(topic_id, "final_rendered")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc
    return {"topic_id": str(topic.id), "status": topic.status, "message": "Final MP4/SRT/cover render job queued"}


@router.get("/{topic_id}/video-jobs", response_model=list[VideoJob])
def list_video_jobs(topic_id: UUID) -> list[VideoJob]:
    try:
        mock_store.get_topic(topic_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc
    try:
        return list_jobs(topic_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Render job database unavailable: {exc}") from exc


@router.post("/{topic_id}/video-jobs", response_model=VideoJob)
def create_video_job(topic_id: UUID, payload: VideoJobCreateRequest) -> VideoJob:
    try:
        topic = mock_store.get_topic(topic_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc
    if topic.status not in {"approved", "video_draft_generated", "final_rendered"}:
        raise HTTPException(status_code=400, detail="Approve the topic before creating a video job")
    if payload.payload.topic_id != topic_id:
        raise HTTPException(status_code=400, detail="Payload topic_id does not match path topic_id")
    try:
        return create_job(payload.payload)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Unable to create render job: {exc}") from exc


@router.patch("/{topic_id}/video-jobs/{job_id}", response_model=VideoJob)
def update_video_job(topic_id: UUID, job_id: UUID, payload: VideoJobUpdateRequest) -> VideoJob:
    if payload.payload.topic_id != topic_id:
        raise HTTPException(status_code=400, detail="Payload topic_id does not match path topic_id")
    try:
        return update_job(job_id, topic_id, payload.payload)
    except KeyError as exc:
        raise HTTPException(status_code=409, detail="Only pending or failed jobs can be edited") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Unable to update render job: {exc}") from exc


@router.post("/{topic_id}/video-jobs/{job_id}/retry", response_model=VideoJob)
def retry_video_job(topic_id: UUID, job_id: UUID) -> VideoJob:
    try:
        return retry_job(job_id, topic_id)
    except KeyError as exc:
        raise HTTPException(status_code=409, detail="Only failed jobs can be retried") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Unable to retry render job: {exc}") from exc
