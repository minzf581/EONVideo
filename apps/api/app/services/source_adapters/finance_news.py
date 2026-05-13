from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from app.core.config import settings
from app.services.source_adapters.base import HotTopic, clean_text, infer_category, infer_keywords, make_hot_topic


DEFAULT_RSS_URLS = [
    "https://news.google.com/rss/search?q=%E8%9E%8D%E8%B5%84%20IPO%20%E4%B8%8A%E5%B8%82%20%E4%BC%81%E4%B8%9A%E5%87%BA%E6%B5%B7%20when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    "https://news.google.com/rss/search?q=%E6%96%B0%E5%8A%A0%E5%9D%A1%20%E5%AE%B6%E6%97%8F%E5%8A%9E%E5%85%AC%E5%AE%A4%20%E6%B5%B7%E5%A4%96%E8%B5%84%E4%BA%A7%20when:7d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    "https://news.google.com/rss/search?q=RWA%20%E7%BA%A2%E7%AD%B9%20H%E8%82%A1%20%E8%B7%A8%E5%A2%83%E8%B5%84%E6%9C%AC%20when:7d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
]


class FinanceNewsAdapter:
    name = "finance_news"

    async def fetch(self, client: httpx.AsyncClient) -> list[HotTopic]:
        urls = settings.finance_news_rss_url_list or DEFAULT_RSS_URLS
        batches = []
        for url in urls:
            try:
                batches.extend(await self.fetch_rss(client, url))
            except Exception:
                continue
        return batches

    async def fetch_rss(self, client: httpx.AsyncClient, url: str) -> list[HotTopic]:
        response = await client.get(url)
        response.raise_for_status()
        feed = feedparser.parse(response.text)
        topics: list[HotTopic] = []
        for index, entry in enumerate(feed.entries[:20]):
            title = clean_text(getattr(entry, "title", ""))
            summary = clean_text(getattr(entry, "summary", ""))
            published_at = parse_datetime(getattr(entry, "published", None) or getattr(entry, "updated", None))
            text = f"{title} {summary}"
            topics.append(
                make_hot_topic(
                    platform="finance_news",
                    title=title,
                    url=str(getattr(entry, "link", "")),
                    heat_score=max(86 - index, 35),
                    published_at=published_at,
                    keywords=infer_keywords(text),
                    category=infer_category(text),
                    raw={"adapter": self.name, "source_url": url, "summary": summary},
                )
            )
        return topics


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
