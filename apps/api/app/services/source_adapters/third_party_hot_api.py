from __future__ import annotations

from datetime import datetime

import httpx

from app.core.config import settings
from app.services.source_adapters.base import HotTopic, make_hot_topic


class ThirdPartyHotApiAdapter:
    name = "third_party_hot_api"

    async def fetch(self, client: httpx.AsyncClient) -> list[HotTopic]:
        if not settings.hot_api_base_url:
            return []
        headers = {"Accept": "application/json"}
        if settings.hot_api_key:
            headers["Authorization"] = f"Bearer {settings.hot_api_key}"
            headers["X-API-Key"] = settings.hot_api_key
        response = await client.get(settings.hot_api_base_url, headers=headers)
        response.raise_for_status()
        payload = response.json()
        rows = extract_rows(payload)
        topics: list[HotTopic] = []
        for index, row in enumerate(rows[:100]):
            title = str(row.get("title") or row.get("name") or row.get("word") or "")
            if not title:
                continue
            topics.append(
                make_hot_topic(
                    platform=str(row.get("platform") or "third_party_hot_api"),
                    title=title,
                    url=str(row.get("url") or ""),
                    heat_score=row.get("heat_score") or row.get("hot") or max(92 - index, 20),
                    published_at=parse_iso_datetime(row.get("published_at")),
                    keywords=list(row.get("keywords", []) or []),
                    category=str(row.get("category") or "") or None,
                    raw={"adapter": self.name, **row},
                )
            )
        return topics


def extract_rows(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("data", "items", "list", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
    return []


def parse_iso_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
