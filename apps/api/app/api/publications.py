from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.publications import (
    CreatePublicationRequest,
    PerformanceAnalysis,
    PerformanceSnapshot,
    PerformanceSnapshotCreate,
    Publication,
    PublicationChannel,
)
from app.services import mock_store

router = APIRouter(tags=["publications"])


@router.get("/publication-channels", response_model=list[PublicationChannel])
def list_channels() -> list[PublicationChannel]:
    return mock_store.CHANNELS


@router.get("/publications", response_model=list[Publication])
def list_publications() -> list[Publication]:
    return mock_store.PUBLICATIONS


@router.post("/topics/{topic_id}/publications", response_model=Publication)
def create_publication(topic_id: UUID, payload: CreatePublicationRequest) -> Publication:
    try:
        return mock_store.create_publication(
            topic_id=topic_id,
            channel_id=payload.channel_id,
            platform=payload.platform,
            published_url=payload.published_url,
            published_at=payload.published_at,
            notes=payload.notes,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Topic not found") from exc


@router.get("/publications/{publication_id}", response_model=Publication)
def get_publication(publication_id: UUID) -> Publication:
    try:
        return mock_store.get_publication(publication_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Publication not found") from exc


@router.post("/publications/{publication_id}/performance-snapshots", response_model=PerformanceSnapshot)
def create_performance_snapshot(publication_id: UUID, payload: PerformanceSnapshotCreate) -> PerformanceSnapshot:
    try:
        mock_store.get_publication(publication_id)
        return mock_store.create_snapshot(publication_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Publication not found") from exc


@router.get("/publications/{publication_id}/performance-snapshots", response_model=list[PerformanceSnapshot])
def list_performance_snapshots(publication_id: UUID) -> list[PerformanceSnapshot]:
    return [snapshot for snapshot in mock_store.SNAPSHOTS if snapshot.publication_id == publication_id]


@router.post("/publications/{publication_id}/analyze-performance", response_model=PerformanceAnalysis)
def analyze_performance(publication_id: UUID) -> PerformanceAnalysis:
    try:
        return mock_store.analyze_publication(publication_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Publication not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/performance/dashboard", response_model=dict)
def performance_dashboard() -> dict:
    return {
        "platforms": ["微信视频号", "抖音", "小红书"],
        "publication_count": len(mock_store.PUBLICATIONS),
        "snapshot_count": len(mock_store.SNAPSHOTS),
        "analysis_count": len(mock_store.ANALYSES),
        "top_topics": sorted(mock_store.ANALYSES, key=lambda item: item.performance_score, reverse=True)[:5],
    }


@router.get("/performance/learning-summary", response_model=dict)
def learning_summary() -> dict:
    summaries = [analysis.prompt_learning_summary for analysis in mock_store.ANALYSES]
    return {
        "active_rules": len(summaries),
        "summary": summaries
        or [
            "暂无发布表现数据。默认优先生成与海外融资、新加坡资本市场、家族办公室和企业出海直接相关的选题。"
        ],
    }
