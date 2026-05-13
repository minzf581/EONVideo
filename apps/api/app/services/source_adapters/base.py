from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import unescape
from re import sub
from typing import Any, Protocol

import httpx


USER_AGENT = "EONVideoBot/1.0 (+https://github.com/minzf581/EONVideo)"

TOPIC_KEYWORDS = [
    "融资",
    "IPO",
    "上市",
    "红筹",
    "H股",
    "新加坡",
    "RWA",
    "家族办公室",
    "企业出海",
    "海外融资",
    "跨境资本",
    "并购",
    "定向增发",
    "上市公司",
    "企业家",
    "现金流",
    "供应链金融",
    "海外资产",
]

CATEGORY_KEYWORDS = {
    "hongkong_ipo": ["IPO", "上市", "H股", "红筹", "递表", "港股"],
    "family_office": ["家族办公室", "家办", "海外资产", "资产配置"],
    "rwa": ["RWA", "真实世界资产", "代币化", "数字资产"],
    "enterprise_globalization": ["企业出海", "出海", "全球化"],
    "singapore_capital_market": ["新加坡", "海外融资", "区域总部"],
    "corporate_finance": ["融资", "并购", "定向增发", "现金流", "供应链金融", "企业家"],
}


@dataclass(frozen=True)
class HotTopic:
    platform: str
    title: str
    url: str
    heat_score: float
    published_at: datetime | None
    keywords: list[str]
    category: str
    raw: dict[str, Any]


class SourceAdapter(Protocol):
    name: str

    async def fetch(self, client: httpx.AsyncClient) -> list[HotTopic]:
        ...


def clean_text(value: str | None) -> str:
    text = unescape(value or "")
    text = sub(r"<script[\s\S]*?</script>", "", text, flags=2)
    text = sub(r"<style[\s\S]*?</style>", "", text, flags=2)
    text = sub(r"<[^>]+>", " ", text)
    text = sub(r"\s+", " ", text)
    return text.strip()


def infer_keywords(text: str) -> list[str]:
    lowered = text.lower()
    return [keyword for keyword in TOPIC_KEYWORDS if keyword.lower() in lowered]


def infer_category(text: str) -> str:
    lowered = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return category
    return "corporate_finance"


def is_relevant(topic: HotTopic) -> bool:
    text = f"{topic.title} {' '.join(topic.keywords)} {topic.category}".lower()
    return any(keyword.lower() in text for keyword in TOPIC_KEYWORDS)


def normalize_heat(value: float | int | None, default: float = 50) -> float:
    if value is None:
        return default
    return max(0, min(float(value), 100))


def dedupe_topics(topics: list[HotTopic]) -> list[HotTopic]:
    seen: set[str] = set()
    deduped: list[HotTopic] = []
    for topic in topics:
        key = topic.title.lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(topic)
    return deduped


def make_hot_topic(
    *,
    platform: str,
    title: str,
    url: str = "",
    heat_score: float | int | None = None,
    published_at: datetime | None = None,
    keywords: list[str] | None = None,
    category: str | None = None,
    raw: dict[str, Any] | None = None,
) -> HotTopic:
    clean_title = clean_text(title)
    inferred_keywords = keywords or infer_keywords(clean_title)
    return HotTopic(
        platform=platform,
        title=clean_title,
        url=url,
        heat_score=normalize_heat(heat_score),
        published_at=published_at,
        keywords=inferred_keywords,
        category=category or infer_category(f"{clean_title} {' '.join(inferred_keywords)}"),
        raw=raw or {},
    )
