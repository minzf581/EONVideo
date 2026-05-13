from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.video_jobs import VideoJob
from app.services.render_jobs import list_jobs

router = APIRouter(prefix="/video-jobs", tags=["video-jobs"])


@router.get("", response_model=list[VideoJob])
def list_video_jobs() -> list[VideoJob]:
    try:
        return list_jobs()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Render job database unavailable: {exc}") from exc
