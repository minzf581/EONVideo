from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from re import sub
from typing import Awaitable
from uuid import uuid4

import asyncio
import feedparser
import httpx

from app.schemas.topics import Topic, TopicScript


USER_AGENT = "EONVideoBot/1.0 (+https://github.com/minzf581/EONVideo)"


@dataclass(frozen=True)
class NewsSource:
    name: str
    url: str
    category: str
    region: str


@dataclass(frozen=True)
class NewsItem:
    title: str
    url: str
    source: str
    category: str
    region: str
    published_at: datetime | None
    summary: str


RSS_SOURCES = [
    NewsSource(
        name="Google News - AI Capital",
        url="https://news.google.com/rss/search?q=AI%20financing%20IPO%20Singapore%20Hong%20Kong%20when:2d&hl=zh-CN&gl=SG&ceid=SG:zh-Hans",
        category="ai_capital",
        region="global",
    ),
    NewsSource(
        name="Google News - Singapore Capital Market",
        url="https://news.google.com/rss/search?q=Singapore%20capital%20market%20IPO%20fundraising%20when:2d&hl=zh-CN&gl=SG&ceid=SG:zh-Hans",
        category="singapore_capital_market",
        region="singapore",
    ),
    NewsSource(
        name="Google News - Hong Kong IPO",
        url="https://news.google.com/rss/search?q=Hong%20Kong%20IPO%20China%20companies%20when:2d&hl=zh-CN&gl=HK&ceid=HK:zh-Hans",
        category="hongkong_ipo",
        region="hongkong",
    ),
    NewsSource(
        name="Google News - Family Office Singapore",
        url="https://news.google.com/rss/search?q=Singapore%20family%20office%20wealth%20management%20when:7d&hl=zh-CN&gl=SG&ceid=SG:zh-Hans",
        category="family_office",
        region="singapore",
    ),
    NewsSource(
        name="Google News - RWA",
        url="https://news.google.com/rss/search?q=RWA%20tokenization%20real%20world%20assets%20finance%20when:7d&hl=zh-CN&gl=SG&ceid=SG:zh-Hans",
        category="rwa",
        region="global",
    ),
    NewsSource(
        name="Google News - China Globalization",
        url="https://news.google.com/rss/search?q=Chinese%20companies%20going%20global%20overseas%20fundraising%20when:7d&hl=zh-CN&gl=SG&ceid=SG:zh-Hans",
        category="enterprise_globalization",
        region="global",
    ),
    NewsSource(
        name="MAS News",
        url="https://www.mas.gov.sg/rss/news",
        category="singapore_capital_market",
        region="singapore",
    ),
    NewsSource(
        name="HKEX News",
        url="https://www.hkex.com.hk/News/News-Release/RSS-Feeds?sc_lang=en",
        category="hongkong_ipo",
        region="hongkong",
    ),
]

BUSINESS_KEYWORDS = {
    "singapore": 18,
    "new加坡": 18,
    "ipo": 16,
    "上市": 16,
    "融资": 18,
    "fundraising": 18,
    "capital": 14,
    "market": 8,
    "ai": 14,
    "artificial intelligence": 14,
    "family office": 18,
    "家族办公室": 18,
    "hong kong": 14,
    "香港": 14,
    "rwa": 12,
    "tokenization": 12,
    "出海": 16,
    "overseas": 12,
    "china": 10,
    "中国": 10,
}


def clean_text(value: str | None) -> str:
    text = unescape(value or "")
    text = sub(r"<[^>]+>", "", text)
    text = sub(r"\s+", " ", text)
    return text.strip()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (TypeError, ValueError):
        return None


def score_item(item: NewsItem) -> float:
    text = f"{item.title} {item.summary}".lower()
    score = 42.0
    for keyword, weight in BUSINESS_KEYWORDS.items():
        if keyword in text:
            score += weight
    if item.published_at:
        age_hours = (datetime.now(timezone.utc) - item.published_at.astimezone(timezone.utc)).total_seconds() / 3600
        if age_hours <= 24:
            score += 12
        elif age_hours <= 72:
            score += 6
    return min(score, 96.0)


async def fetch_rss_source(client: httpx.AsyncClient, source: NewsSource) -> list[NewsItem]:
    response = await client.get(source.url, headers={"User-Agent": USER_AGENT}, follow_redirects=True)
    response.raise_for_status()
    feed = feedparser.parse(response.text)
    items: list[NewsItem] = []
    for entry in feed.entries[:12]:
        title = clean_text(getattr(entry, "title", ""))
        url = str(getattr(entry, "link", ""))
        if not title or not url:
            continue
        summary = clean_text(getattr(entry, "summary", ""))
        published = parse_datetime(getattr(entry, "published", None) or getattr(entry, "updated", None))
        items.append(
            NewsItem(
                title=title,
                url=url,
                source=source.name,
                category=source.category,
                region=source.region,
                published_at=published,
                summary=summary,
            )
        )
    return items


async def fetch_latest_news(limit: int = 40) -> list[NewsItem]:
    timeout = httpx.Timeout(12.0, connect=6.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [fetch_rss_source(client, source) for source in RSS_SOURCES]
        batches = await gather_with_failures(tasks)
    deduped: dict[str, NewsItem] = {}
    for item in [news for batch in batches for news in batch]:
        key = item.title.lower()
        if key not in deduped:
            deduped[key] = item
    return sorted(deduped.values(), key=score_item, reverse=True)[:limit]


async def gather_with_failures(tasks: list[Awaitable[list[NewsItem]]]) -> list[list[NewsItem]]:
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [result for result in results if isinstance(result, list)]


def infer_client(category: str) -> str:
    return {
        "ai_capital": "AI、SaaS、智能制造企业创始人和 CFO。",
        "singapore_capital_market": "计划海外融资、上市或设立新加坡区域总部的中国企业。",
        "hongkong_ipo": "计划 IPO、Pre-IPO 融资或比较上市地的企业家和 CFO。",
        "family_office": "企业家、高净值家庭、家族企业二代和家族办公室负责人。",
        "rwa": "探索 RWA、资产证券化、跨境融资或数字金融的企业。",
        "enterprise_globalization": "正在推进出海、海外融资或全球化架构调整的中国企业。",
    }.get(category, "关注海外融资、资本市场和全球化发展的企业决策者。")


def infer_business_entry(category: str) -> str:
    return {
        "ai_capital": "切入 AI 企业海外融资材料、投资人沟通和国际资本故事设计。",
        "singapore_capital_market": "切入新加坡资本市场对接、海外融资路径和全球化资本结构设计。",
        "hongkong_ipo": "切入香港 IPO 路径评估、上市前融资和资本结构梳理。",
        "family_office": "切入新加坡家族办公室设立评估、家族治理和海外投资机会对接。",
        "rwa": "切入 RWA 合规边界、跨境融资结构和海外投资人对接。",
        "enterprise_globalization": "切入中国企业出海的控股架构、融资路径和国际投资人沟通。",
    }.get(category, "切入海外融资、资本市场对接和全球化资本结构设计。")


def build_live_topic(item: NewsItem) -> Topic:
    score = score_item(item)
    target_client = infer_client(item.category)
    business_entry = infer_business_entry(item.category)
    pain_point = "看到了热点新闻，但不知道它会如何影响融资窗口、上市路径、海外架构和投资人判断。"
    source_line = f"来源：{item.source}；原文：{item.url}"
    topic_title = f"{item.title}，企业决策者应该看什么？"
    risk_notice = "以上内容基于公开新闻源整理，仅作市场观察和商业信息分享，不构成投资、法律或税务建议。"
    return Topic(
        id=uuid4(),
        production_date=date.today(),
        status="pending_review",
        category=item.category,
        score=score,
        risk_score=52 if item.category in {"rwa", "us_china"} else 34,
        topic_title=topic_title[:120],
        hot_summary=f"{item.title}。{item.summary[:180]} {source_line}",
        target_client=target_client,
        user_pain_point=pain_point,
        business_entry_point=business_entry,
        cover_title=make_cover_title(item),
        risk_notice=risk_notice,
        publish_copy=f"{item.title}\n\n这条新闻值得企业家和 CFO 关注的，不只是事件本身，而是它对融资路径、资本结构和海外投资人沟通的影响。\n\n{risk_notice}\n\n{source_line}",
        tags=make_tags(item),
        scripts=[
            TopicScript(
                script_type="30s",
                estimated_duration_seconds=30,
                full_script=f"今天这条新闻值得关注：{item.title}。对{target_client}来说，重点不是追热点，而是判断它会不会影响融资路径、上市地点、资本结构和投资人沟通。我的建议是，把新闻翻译成自己的企业决策问题，而不是只看标题。",
            ),
            TopicScript(
                script_type="60s",
                estimated_duration_seconds=60,
                full_script=f"今天看到一条值得企业家和 CFO 关注的新闻：{item.title}。公开信息来自{item.source}。这件事对{target_client}的启发是，海外资本市场的变化往往不会直接告诉你答案，但会改变投资人关注的问题。你需要判断：它是否影响你的融资窗口？是否影响上市地选择？是否需要提前调整控股架构和投资人故事？这也是我会切入的服务方向：{business_entry}。以上只是市场观察，不构成投资建议。",
            ),
        ],
        created_at=datetime.now(timezone.utc),
    )


def make_cover_title(item: NewsItem) -> str:
    if item.category == "singapore_capital_market":
        return "新加坡资本新信号"
    if item.category == "hongkong_ipo":
        return "香港 IPO 新动向"
    if item.category == "family_office":
        return "家办客户要关注"
    if item.category == "rwa":
        return "RWA 热点别只看融资"
    if item.category == "ai_capital":
        return "AI 融资故事怎么讲"
    return "企业出海新信号"


def make_tags(item: NewsItem) -> list[str]:
    base = {
        "ai_capital": ["AI", "海外融资", "资本故事"],
        "singapore_capital_market": ["新加坡", "资本市场", "企业出海"],
        "hongkong_ipo": ["香港IPO", "上市路径", "融资"],
        "family_office": ["家族办公室", "新加坡", "资产配置"],
        "rwa": ["RWA", "跨境融资", "合规"],
        "enterprise_globalization": ["企业出海", "全球化", "资本结构"],
    }.get(item.category, ["财经热点", "海外融资", "资本市场"])
    return base + [item.source]


async def generate_live_topics(count: int = 10) -> list[Topic]:
    news_items = await fetch_latest_news(limit=max(count * 2, 20))
    topics = [build_live_topic(item) for item in news_items[:count]]
    return topics
