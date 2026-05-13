from __future__ import annotations

from urllib.parse import quote

import httpx

from app.services.source_adapters.base import HotTopic, make_hot_topic


class WeiboHotsearchAdapter:
    name = "weibo_hotsearch"

    async def fetch(self, client: httpx.AsyncClient) -> list[HotTopic]:
        response = await client.get("https://weibo.com/ajax/side/hotSearch", headers={"Accept": "application/json"})
        response.raise_for_status()
        rows = response.json().get("data", {}).get("realtime", [])
        topics: list[HotTopic] = []
        for index, row in enumerate(rows[:50]):
            title = row.get("note") or row.get("word") or ""
            if not title:
                continue
            heat = row.get("num")
            heat_score = min(round(float(heat) / 10000), 100) if heat else max(98 - index * 2, 25)
            topics.append(
                make_hot_topic(
                    platform="weibo",
                    title=title,
                    url=f"https://s.weibo.com/weibo?q={quote(title)}",
                    heat_score=heat_score,
                    raw={"adapter": self.name, "rank": index + 1, **row},
                )
            )
        return topics
