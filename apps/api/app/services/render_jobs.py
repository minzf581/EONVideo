from __future__ import annotations

from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from app.core.config import settings
from app.schemas.video_jobs import VideoJob, VideoJobPayload


def database_url() -> str:
    return settings.database_url.replace("postgresql+psycopg://", "postgresql://")


def connect() -> psycopg.Connection:
    return psycopg.connect(database_url(), row_factory=dict_row)


def ensure_table() -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                create table if not exists render_jobs (
                  id uuid primary key default gen_random_uuid(),
                  status text not null default 'pending',
                  payload jsonb not null default '{}'::jsonb,
                  video_url text,
                  error_message text,
                  retry_count integer not null default 0,
                  created_at timestamp not null default now(),
                  updated_at timestamp not null default now(),
                  completed_at timestamp
                )
                """
            )
            cur.execute(
                """
                create index if not exists idx_render_jobs_pending
                  on render_jobs (created_at)
                  where status = 'pending'
                """
            )


def normalize_payload(raw_payload: dict[str, Any]) -> VideoJobPayload:
    payload = dict(raw_payload)
    if "brand_name" in payload and "brandName" not in payload:
        payload["brandName"] = payload.pop("brand_name")
    if "duration_seconds" in payload and "durationSeconds" not in payload:
        payload["durationSeconds"] = payload.pop("duration_seconds")
    if "target_platform" in payload and "targetPlatform" not in payload:
        payload["targetPlatform"] = payload.pop("target_platform")
    if "cover_title" in payload and "coverTitle" not in payload:
        payload["coverTitle"] = payload.pop("cover_title")
    if "script_type" in payload and "scriptType" not in payload:
        payload["scriptType"] = payload.pop("script_type")
    return VideoJobPayload.model_validate(payload)


def row_to_job(row: dict[str, Any]) -> VideoJob:
    return VideoJob(
        id=row["id"],
        status=row["status"],
        payload=normalize_payload(row["payload"]),
        video_url=row["video_url"],
        error_message=row["error_message"],
        retry_count=row["retry_count"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        completed_at=row["completed_at"],
    )


def list_jobs(topic_id: UUID | None = None) -> list[VideoJob]:
    ensure_table()
    with connect() as conn:
        with conn.cursor() as cur:
            if topic_id:
                cur.execute(
                    """
                    select *
                    from render_jobs
                    where payload->>'topic_id' = %s
                    order by created_at desc
                    """,
                    (str(topic_id),),
                )
            else:
                cur.execute(
                    """
                    select *
                    from render_jobs
                    where payload ? 'topic_id'
                    order by created_at desc
                    limit 200
                    """
                )
            return [row_to_job(row) for row in cur.fetchall()]


def create_job(payload: VideoJobPayload) -> VideoJob:
    ensure_table()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into render_jobs (status, payload)
                values ('pending', %s::jsonb)
                returning *
                """,
                (payload.model_dump_json(),),
            )
            return row_to_job(cur.fetchone())


def update_job(job_id: UUID, topic_id: UUID, payload: VideoJobPayload) -> VideoJob:
    ensure_table()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                update render_jobs
                set payload = %s::jsonb,
                    updated_at = now()
                where id = %s
                  and payload->>'topic_id' = %s
                  and status in ('pending', 'failed')
                returning *
                """,
                (payload.model_dump_json(), job_id, str(topic_id)),
            )
            row = cur.fetchone()
            if row is None:
                raise KeyError("render job not editable")
            return row_to_job(row)


def retry_job(job_id: UUID, topic_id: UUID) -> VideoJob:
    ensure_table()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                update render_jobs
                set status = 'pending',
                    error_message = null,
                    video_url = null,
                    completed_at = null,
                    updated_at = now()
                where id = %s
                  and payload->>'topic_id' = %s
                  and status = 'failed'
                returning *
                """,
                (job_id, str(topic_id)),
            )
            row = cur.fetchone()
            if row is None:
                raise KeyError("render job not retryable")
            return row_to_job(row)
