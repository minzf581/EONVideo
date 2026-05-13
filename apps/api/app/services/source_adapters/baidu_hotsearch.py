from __future__ import annotations

from urllib.parse import quote

import httpx

from app.services.source_adapters.base import HotTopic, clean_text, make_hot_topic


class BaiduHotsearchAdapter:
    name = "baidu_hotsearch"

    async def fetch(self, client: httpx.AsyncClient) -> list[HotTopic]:
        response = await client.get("https://top.baidu.com/board?tab=realtime")
        response.raise_for_status()
        titles = [
            clean_text(match)
            for match in __import__("re").findall(
                r'<div[^>]+class="[^"]*c-single-text-ellipsis[^"]*"[^>]*>([\s\S]*?)</div>',
                response.text,
            )
        ]
        return [
            make_hot_topic(
                platform="baidu",
                title=title,
                url=f"https://www.baidu.com/s?wd={quote(title)}",
                heat_score=max(100 - index * 2, 30),
                raw={"adapter": self.name, "rank": index + 1},
            )
            for index, title in enumerate(titles[:50])
            if title
        ]
