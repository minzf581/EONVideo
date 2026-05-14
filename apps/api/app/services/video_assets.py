from __future__ import annotations

from json import dumps
from re import sub
from urllib.parse import quote

from app.schemas.topics import Topic, TopicScript, VideoAsset


def slugify(value: str) -> str:
    slug = sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", value).strip("-")
    return slug[:48] or "topic"


def pick_script(topic: Topic, script_type: str) -> TopicScript:
    for script in topic.scripts:
        if script.script_type == script_type:
            return script
    return topic.scripts[-1]


def build_srt(script: TopicScript) -> str:
    sentences = [part.strip() for part in sub(r"[。！？!?]", "。\n", script.full_script).splitlines() if part.strip()]
    chunks = sentences[:8] or [script.full_script]
    seconds_per_chunk = max(3, round(script.estimated_duration_seconds / max(len(chunks), 1)))
    lines = []
    current = 0
    for index, sentence in enumerate(chunks, start=1):
        start = current
        end = min(script.estimated_duration_seconds, current + seconds_per_chunk)
        current = end
        lines.extend(
            [
                str(index),
                f"{format_srt_time(start)} --> {format_srt_time(end)}",
                sentence,
                "",
            ]
        )
    return "\n".join(lines)


def format_srt_time(total_seconds: int) -> str:
    minutes, seconds = divmod(max(total_seconds, 0), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},000"


def build_remotion_payload(topic: Topic, script: TopicScript, template: str) -> dict[str, object]:
    return {
        "template": template,
        "composition": "CapitalNews",
        "resolution": "1080x1920",
        "topic_id": str(topic.id),
        "title": topic.topic_title,
        "subtitle": topic.topic_title,
        "script_type": script.script_type,
        "script": script.full_script,
        "voiceoverUrl": None,
        "bgmUrl": None,
        "bullets": [topic.target_client, topic.user_pain_point, topic.business_entry_point],
        "brandName": "EONVideo Capital Brief",
        "cta": "关注账号，了解更多海外融资与新加坡资本市场观察。",
        "durationSeconds": script.estimated_duration_seconds,
        "fps": 30,
        "style": "douyin_finance_ip",
        "targetPlatform": "douyin",
        "coverTitle": topic.cover_title,
        "riskNotice": topic.risk_notice,
    }


def make_data_asset(asset_type: str, file_name: str, content: str, mime_type: str) -> VideoAsset:
    return VideoAsset(
        asset_type=asset_type,
        file_name=file_name,
        download_url=f"data:{mime_type};charset=utf-8,{quote(content)}",
        render_status="completed",
    )


def generate_assets(topic: Topic, script_type: str, template: str) -> list[VideoAsset]:
    script = pick_script(topic, script_type)
    slug = slugify(topic.cover_title)
    remotion_payload = build_remotion_payload(topic, script, template)
    return [
        make_data_asset(
            "remotion_json",
            f"{slug}-remotion.json",
            dumps(remotion_payload, ensure_ascii=False, indent=2),
            "application/json",
        ),
        make_data_asset("srt", f"{slug}.srt", build_srt(script), "text/plain"),
        make_data_asset("publish_copy", f"{slug}-publish-copy.txt", topic.publish_copy, "text/plain"),
        make_data_asset(
            "cover",
            f"{slug}-cover.txt",
            f"封面标题：{topic.cover_title}\n副标题：{topic.topic_title}",
            "text/plain",
        ),
        VideoAsset(
            asset_type="mp4",
            file_name=f"{slug}-draft.mp4",
            download_url="about:blank",
            render_status="pending",
        ),
    ]
