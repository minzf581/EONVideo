from __future__ import annotations

import feedparser
import httpx

from app.core.config import settings
from app.services.source_adapters.base import HotTopic, clean_text, infer_category, infer_keywords, make_hot_topic


class WechatArticleSourceAdapter:
    name = "wechat_article_source"

    async def fetch(self, client: httpx.AsyncClient) -> list[HotTopic]:
        topics: list[HotTopic] = []
        for source in settings.wechat_source_config:
            url = source.get("url")
            if not url:
                continue
            try:
                response = await client.get(str(url))
                response.raise_for_status()
                topics.extend(self.parse_source(source, response.text))
            except Exception:
                continue
        return topics

    def parse_source(self, source: dict[str, object], body: str) -> list[HotTopic]:
        if "<rss" in body or "<feed" in body:
            feed = feedparser.parse(body)
            return [
                make_hot_topic(
                    platform="wechat_article",
                    title=clean_text(getattr(entry, "title", "")),
                    url=str(getattr(entry, "link", source.get("url", ""))),
                    heat_score=max(80 - index, 35),
                    keywords=list(source.get("keywords", []) or []) or infer_keywords(getattr(entry, "title", "")),
                    category=str(source.get("category") or infer_category(getattr(entry, "title", ""))),
                    raw={"adapter": self.name, "source": source},
                )
                for index, entry in enumerate(feed.entries[:20])
            ]
        title = clean_text(__import__("re").search(r"<title[^>]*>([\s\S]*?)</title>", body, flags=2).group(1)) if __import__("re").search(r"<title[^>]*>([\s\S]*?)</title>", body, flags=2) else str(source.get("name", "公众号文章源"))
        return [
            make_hot_topic(
                platform="wechat_article",
                title=title,
                url=str(source.get("url", "")),
                heat_score=72,
                keywords=list(source.get("keywords", []) or []) or infer_keywords(title),
                category=str(source.get("category") or infer_category(title)),
                raw={"adapter": self.name, "source": source},
            )
        ]
