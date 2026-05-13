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
from app.services.source_adapters import (
    BaiduHotsearchAdapter,
    FinanceNewsAdapter,
    ManualSeedSourceAdapter,
    ThirdPartyHotApiAdapter,
    WechatArticleSourceAdapter,
    WeiboHotsearchAdapter,
)
from app.services.source_adapters.base import HotTopic, dedupe_topics, is_relevant


USER_AGENT = "EONVideoBot/1.0 (+https://github.com/minzf581/EONVideo)"


@dataclass(frozen=True)
class NewsSource:
    name: str
    url: str
    category: str
    region: str
    platform: str
    priority_weight: float


@dataclass(frozen=True)
class NewsItem:
    title: str
    url: str
    source: str
    category: str
    region: str
    platform: str
    priority_weight: float
    published_at: datetime | None
    summary: str


RSS_SOURCES = [
    NewsSource(
        name="抖音热点 - 中国老板资本关键词",
        url="https://news.google.com/rss/search?q=%E6%8A%96%E9%9F%B3%20AI%20IPO%20%E6%96%B0%E5%8A%A0%E5%9D%A1%20%E4%BC%81%E4%B8%9A%E5%87%BA%E6%B5%B7%20when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        category="ai_capital",
        region="china",
        platform="douyin",
        priority_weight=0.40,
    ),
    NewsSource(
        name="抖音财经趋势 - 新加坡与海外融资",
        url="https://news.google.com/rss/search?q=%E6%8A%96%E9%9F%B3%20%E6%96%B0%E5%8A%A0%E5%9D%A1%20%E6%B5%B7%E5%A4%96%E8%9E%8D%E8%B5%84%20%E5%AE%B6%E6%97%8F%E5%8A%9E%E5%85%AC%E5%AE%A4%20when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        category="singapore_capital_market",
        region="china",
        platform="douyin",
        priority_weight=0.40,
    ),
    NewsSource(
        name="微信公众号财经 - IPO与出海",
        url="https://news.google.com/rss/search?q=%E8%B4%A2%E6%96%B0%2036kr%20%E8%99%8E%E5%97%85%20%E6%8A%95%E4%B8%AD%20IPO%E6%97%A9%E7%9F%A5%E9%81%93%20%E4%BC%81%E4%B8%9A%E5%87%BA%E6%B5%B7%20when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        category="hongkong_ipo",
        region="china",
        platform="wechat_channels",
        priority_weight=0.25,
    ),
    NewsSource(
        name="微信公众号财经 - 华尔街见闻/财联社/第一财经",
        url="https://news.google.com/rss/search?q=%E5%8D%8E%E5%B0%94%E8%A1%97%E8%A7%81%E9%97%BB%20%E8%B4%A2%E8%81%94%E7%A4%BE%20%E7%AC%AC%E4%B8%80%E8%B4%A2%E7%BB%8F%20%E6%B5%B7%E5%A4%96%E8%B5%84%E4%BA%A7%E9%85%8D%E7%BD%AE%20when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        category="family_office",
        region="china",
        platform="wechat_channels",
        priority_weight=0.25,
    ),
    NewsSource(
        name="小红书商业趋势 - 海外资产与身份焦虑",
        url="https://news.google.com/rss/search?q=%E5%B0%8F%E7%BA%A2%E4%B9%A6%20%E6%96%B0%E5%8A%A0%E5%9D%A1%20family%20office%20%E6%B5%B7%E5%A4%96%E8%B5%84%E4%BA%A7%20%E9%A6%99%E6%B8%AFIPO%20when:7d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        category="family_office",
        region="china",
        platform="xiaohongshu",
        priority_weight=0.20,
    ),
    NewsSource(
        name="小红书商业趋势 - 企业出海",
        url="https://news.google.com/rss/search?q=%E5%B0%8F%E7%BA%A2%E4%B9%A6%20%E4%BC%81%E4%B8%9A%E5%87%BA%E6%B5%B7%20%E5%85%A8%E7%90%83%E8%B5%84%E4%BA%A7%E9%85%8D%E7%BD%AE%20%E9%A6%99%E6%B8%AFIPO%20when:7d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        category="enterprise_globalization",
        region="china",
        platform="xiaohongshu",
        priority_weight=0.20,
    ),
    NewsSource(
        name="百度/微博/雪球 - 辅助财经热搜",
        url="https://news.google.com/rss/search?q=%E7%99%BE%E5%BA%A6%E7%83%AD%E6%90%9C%20%E5%BE%AE%E5%8D%9A%E8%B4%A2%E7%BB%8F%20%E9%9B%AA%E7%90%83%20%E7%BE%8E%E8%82%A1%20%E6%B8%AF%E8%82%A1%20%E6%AF%94%E7%89%B9%E5%B8%81%20when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        category="rwa",
        region="china",
        platform="china_search_social",
        priority_weight=0.10,
    ),
    NewsSource(
        name="国际媒体辅助 - 资本视角校准",
        url="https://news.google.com/rss/search?q=Bloomberg%20Reuters%20CNBC%20WSJ%20Financial%20Times%20China%20companies%20Singapore%20IPO%20when:2d&hl=zh-CN&gl=SG&ceid=SG:zh-Hans",
        category="enterprise_globalization",
        region="global",
        platform="international_media",
        priority_weight=0.05,
    ),
]

CHINA_BOSS_KEYWORDS = {
    "老板": 22,
    "企业家": 22,
    "创始人": 20,
    "董事长": 18,
    "cfo": 18,
    "融资": 22,
    "ipo": 22,
    "上市": 20,
    "新加坡": 24,
    "singapore": 24,
    "家族办公室": 24,
    "family office": 24,
    "企业出海": 24,
    "出海": 20,
    "海外融资": 24,
    "海外资产": 20,
    "全球资产配置": 20,
    "香港ipo": 22,
    "香港": 16,
    "rwa": 18,
    "中美关系": 18,
    "美股": 14,
    "港股": 14,
    "比特币": 12,
    "全球化": 22,
    "资本结构": 22,
    "估值": 16,
    "投资人": 18,
}

LOW_PRIORITY_KEYWORDS = {
    "openai功能": -18,
    "ai工具": -14,
    "科技公司财报": -16,
    "vc动态": -12,
    "互联网八卦": -20,
    "tool review": -16,
}

SOURCE_PRIORITY_WEIGHT = {
    "baidu": 0.10,
    "weibo": 0.10,
    "finance_news": 0.25,
    "wechat_article": 0.25,
    "third_party_hot_api": 0.40,
    "douyin": 0.40,
    "xiaohongshu": 0.20,
    "manual_seed": 0.08,
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
    scores = score_dimensions(item)
    score = (
        scores["china_boss_relevance_score"] * 0.28
        + scores["enterprise_globalization_score"] * 0.18
        + scores["overseas_capital_score"] * 0.18
        + scores["wechat_channels_potential_score"] * 0.10
        + scores["douyin_potential_score"] * 0.09
        + scores["comment_controversy_score"] * 0.06
        + scores["collection_value_score"] * 0.06
        + scores["international_news_score"] * 0.05
        - scores["risk_score"] * 0.18
    )
    for keyword, weight in LOW_PRIORITY_KEYWORDS.items():
        if keyword in text:
            score += weight
    return min(max(score, 0), 96.0)


def keyword_score(text: str, keywords: dict[str, int], base: float = 0) -> float:
    score = base
    for keyword, weight in keywords.items():
        if keyword in text:
            score += weight
    return min(score, 100.0)


def score_dimensions(item: NewsItem) -> dict[str, float]:
    text = f"{item.title} {item.summary}".lower()
    source_boost = item.priority_weight * 100
    china_boss = keyword_score(text, CHINA_BOSS_KEYWORDS, 28 + source_boost * 0.32)
    enterprise_globalization = keyword_score(
        text,
        {"企业出海": 30, "出海": 22, "全球化": 26, "海外": 18, "供应链": 12, "区域总部": 16, "东南亚": 14},
        22 + source_boost * 0.18,
    )
    overseas_capital = keyword_score(
        text,
        {"ipo": 24, "上市": 20, "融资": 24, "新加坡": 22, "香港": 18, "家族办公室": 20, "rwa": 18, "基金": 12, "投资人": 16},
        24 + source_boost * 0.2,
    )
    wechat_potential = keyword_score(text, {"深度": 12, "趋势": 16, "变化": 12, "企业家": 18, "资本逻辑": 18}, 24 + (24 if item.platform == "wechat_channels" else 0))
    douyin_potential = keyword_score(text, {"热搜": 16, "很多老板": 18, "焦虑": 16, "机会": 14, "变化": 12, "暴涨": 8}, 26 + (28 if item.platform == "douyin" else 0))
    controversy = keyword_score(text, {"中美关系": 20, "比特币": 18, "rwa": 16, "监管": 16, "估值": 12, "风险": 12}, 18)
    collection = keyword_score(text, {"怎么": 10, "路径": 16, "结构": 16, "准备": 14, "清单": 18, "避坑": 16, "框架": 18}, 30)
    international = 72 if item.platform == "international_media" else keyword_score(text, {"bloomberg": 14, "reuters": 14, "wsj": 12, "financial times": 12}, 18)
    risk = keyword_score(text, {"比特币": 18, "rwa": 16, "绕监管": 40, "移民": 12, "荐股": 30, "暴富": 24, "财富自由": 28}, 18)
    if item.published_at:
        age_hours = (datetime.now(timezone.utc) - item.published_at.astimezone(timezone.utc)).total_seconds() / 3600
        if age_hours <= 24:
            china_boss = min(china_boss + 8, 100)
            douyin_potential = min(douyin_potential + 8, 100)
        elif age_hours <= 72:
            china_boss = min(china_boss + 4, 100)
    return {
        "china_boss_relevance_score": round(china_boss, 1),
        "enterprise_globalization_score": round(enterprise_globalization, 1),
        "overseas_capital_score": round(overseas_capital, 1),
        "wechat_channels_potential_score": round(wechat_potential, 1),
        "douyin_potential_score": round(douyin_potential, 1),
        "comment_controversy_score": round(controversy, 1),
        "collection_value_score": round(collection, 1),
        "international_news_score": round(international, 1),
        "risk_score": round(min(risk, 88), 1),
    }


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
                platform=source.platform,
                priority_weight=source.priority_weight,
                published_at=published,
                summary=summary,
            )
        )
    return items


async def fetch_latest_news(limit: int = 40) -> list[NewsItem]:
    timeout = httpx.Timeout(12.0, connect=6.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        adapters = [
            ThirdPartyHotApiAdapter(),
            BaiduHotsearchAdapter(),
            WeiboHotsearchAdapter(),
            FinanceNewsAdapter(),
            WechatArticleSourceAdapter(),
            ManualSeedSourceAdapter(),
        ]
        tasks = [adapter.fetch(client) for adapter in adapters]
        hot_batches = await gather_hot_topic_failures(tasks)
    hot_topics = dedupe_topics([topic for batch in hot_batches for topic in batch])
    news_items = [hot_topic_to_news_item(topic) for topic in hot_topics if is_relevant(topic)]
    deduped: dict[str, NewsItem] = {}
    for item in news_items:
        key = item.title.lower()
        if key not in deduped:
            deduped[key] = item
    return sorted(deduped.values(), key=score_item, reverse=True)[:limit]


async def gather_with_failures(tasks: list[Awaitable[list[NewsItem]]]) -> list[list[NewsItem]]:
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [result for result in results if isinstance(result, list)]


async def gather_hot_topic_failures(tasks: list[Awaitable[list[HotTopic]]]) -> list[list[HotTopic]]:
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [result for result in results if isinstance(result, list)]


def hot_topic_to_news_item(topic: HotTopic) -> NewsItem:
    source_name = {
        "baidu": "百度热搜",
        "weibo": "微博热搜",
        "finance_news": "中文财经新闻",
        "wechat_article": "公众号文章源",
        "third_party_hot_api": "第三方热点 API",
        "manual_seed": "人工维护种子源",
    }.get(topic.platform, topic.platform)
    return NewsItem(
        title=topic.title,
        url=topic.url,
        source=source_name,
        category=topic.category,
        region="china",
        platform=topic.platform,
        priority_weight=SOURCE_PRIORITY_WEIGHT.get(topic.platform, 0.12),
        published_at=topic.published_at,
        summary=f"关键词：{'、'.join(topic.keywords) or '中文财经热点'}；热度分：{topic.heat_score}",
    )


def infer_client(category: str) -> str:
    return {
        "ai_capital": "AI、SaaS、智能制造企业创始人和 CFO。",
        "singapore_capital_market": "计划海外融资、上市或设立新加坡区域总部的中国企业。",
        "hongkong_ipo": "计划 IPO、Pre-IPO 融资或比较上市地的企业家和 CFO。",
        "family_office": "企业家、高净值家庭、家族企业二代和家族办公室负责人。",
        "rwa": "探索 RWA、资产证券化、跨境融资或数字金融的企业。",
        "enterprise_globalization": "正在推进出海、海外融资或全球化架构调整的中国企业。",
        "corporate_finance": "关注融资、现金流、并购、定增和供应链金融的企业老板与 CFO。",
    }.get(category, "关注海外融资、资本市场和全球化发展的企业决策者。")


def infer_business_entry(category: str) -> str:
    return {
        "ai_capital": "切入 AI 企业海外融资材料、投资人沟通和国际资本故事设计。",
        "singapore_capital_market": "切入新加坡资本市场对接、海外融资路径和全球化资本结构设计。",
        "hongkong_ipo": "切入香港 IPO 路径评估、上市前融资和资本结构梳理。",
        "family_office": "切入新加坡家族办公室设立评估、家族治理和海外投资机会对接。",
        "rwa": "切入 RWA 合规边界、跨境融资结构和海外投资人对接。",
        "enterprise_globalization": "切入中国企业出海的控股架构、融资路径和国际投资人沟通。",
        "corporate_finance": "切入融资方案、现金流管理、并购整合和资本结构优化。",
    }.get(category, "切入海外融资、资本市场对接和全球化资本结构设计。")


def why_short_video(item: NewsItem) -> str:
    return {
        "hongkong_ipo": "IPO、上市地和资本路径天然适合短视频拆解，能快速引发老板和 CFO 对窗口期的关注。",
        "singapore_capital_market": "新加坡、海外融资和区域总部话题能直接连接中国企业出海后的资本结构问题。",
        "family_office": "家族办公室和海外资产配置自带高净值人群关注点，适合用趋势洞察方式讲清楚框架。",
        "enterprise_globalization": "企业出海是老板正在面对的现实问题，适合从业务出海延伸到资本结构和海外融资。",
        "rwa": "RWA 有热度也有争议，适合用合规和融资结构角度做克制分析。",
        "corporate_finance": "融资、现金流、并购和供应链金融能直接触达企业经营者的现实压力。",
    }.get(item.category, "这个热点可以从中国老板痛点切入，把资讯转译成融资、上市或跨境资本决策。")


def recommended_script_angle(item: NewsItem) -> str:
    return f"不要讲成新闻播报，建议讲“{item.title}背后的资本逻辑”：先说老板为什么关心，再讲对融资、上市路径、现金流或全球化结构的影响。"


def infer_topic_emotion(item: NewsItem) -> str:
    text = f"{item.title} {item.summary}".lower()
    if any(keyword in text for keyword in ["风险", "监管", "中美关系", "地缘", "波动"]):
        return "风险"
    if any(keyword in text for keyword in ["身份", "家族办公室", "family office", "海外资产"]):
        return "资产安全"
    if any(keyword in text for keyword in ["ipo", "上市", "pre-ipo"]):
        return "IPO压力"
    if any(keyword in text for keyword in ["窗口", "机会", "回暖", "增长"]):
        return "机会"
    if any(keyword in text for keyword in ["趋势", "全球化", "出海"]):
        return "趋势"
    return "焦虑"


def platform_scripts(title: str, target_client: str, pain_point: str, business_entry: str) -> list[TopicScript]:
    return [
        TopicScript(
            script_type="30s",
            estimated_duration_seconds=30,
            full_script=f"最近很多老板都在看这个话题：{title}。真正值得关注的不是新闻本身，而是它会不会影响企业出海、融资节奏和资本结构。对{target_client}来说，{pain_point}。先把业务、股东结构和海外融资路径想清楚，再谈窗口。",
        ),
        TopicScript(
            script_type="60s",
            estimated_duration_seconds=60,
            full_script=f"最近很多老板开始重新评估一个问题：{title}。这件事背后，其实是资本逻辑在变。过去企业更关心哪里估值高，现在更关键的是：业务全球化、股东结构、上市地、海外投资人画像能不能互相匹配。对{target_client}来说，{pain_point}。这时要看的不是单一热点，而是企业全球化的第二阶段：用资本结构服务业务出海，用海外融资连接长期增长。可切入的方向是：{business_entry}。以上只是市场观察，不构成投资建议。",
        ),
        TopicScript(
            script_type="douyin",
            estimated_duration_seconds=45,
            full_script=f"很多老板没意识到，{title}，表面是热点，背后是融资窗口和资本结构的问题。企业出海不是注册一家公司就结束了，而是要提前想清楚新加坡、香港、海外融资和投资人故事怎么配。{pain_point}。这类问题越晚处理，融资时越被动。",
        ),
        TopicScript(
            script_type="wechat_channels",
            estimated_duration_seconds=60,
            full_script=f"最近老板圈讨论比较多的是：{title}。我更建议从资本逻辑看这件事。它提醒中国企业，全球化已经进入第二阶段，重点不只是卖产品到海外，而是同步建立资本结构、融资路径和国际投资人沟通体系。对{target_client}来说，核心问题是：{pain_point}。这背后可以延伸到{business_entry}。内容仅作市场观察。",
        ),
        TopicScript(
            script_type="xiaohongshu",
            estimated_duration_seconds=50,
            full_script=f"一个值得收藏的趋势观察：{title}。很多人只看到了热点，但对中国企业老板和高净值家庭来说，更重要的是资产安全、海外融资和全球资产配置的框架。{pain_point}。如果要判断自己是否适合新加坡、香港 IPO、家族办公室或海外融资路径，先看目标、结构和合规边界。",
        ),
    ]


def build_live_topic(item: NewsItem) -> Topic:
    score = score_item(item)
    dimensions = score_dimensions(item)
    target_client = infer_client(item.category)
    business_entry = infer_business_entry(item.category)
    pain_point = "看到了热点，但不知道它会如何影响融资窗口、上市路径、海外架构、家族资产安排和投资人判断。"
    source_line = f"来源：{item.source}；原文：{item.url}"
    topic_title = f"{item.title}，中国老板真正该看什么？"
    risk_notice = "以上内容基于公开热点源整理，仅作市场观察和商业信息分享，不构成投资、法律、税务、移民或证券建议。"
    source_summary = f"{item.source}｜{item.url or '无公开链接'}"
    return Topic(
        id=uuid4(),
        production_date=date.today(),
        status="pending_review",
        category=item.category,
        score=score,
        risk_score=dimensions["risk_score"],
        topic_emotion=infer_topic_emotion(item),
        china_boss_relevance_score=dimensions["china_boss_relevance_score"],
        enterprise_globalization_score=dimensions["enterprise_globalization_score"],
        overseas_capital_score=dimensions["overseas_capital_score"],
        wechat_channels_potential_score=dimensions["wechat_channels_potential_score"],
        douyin_potential_score=dimensions["douyin_potential_score"],
        comment_controversy_score=dimensions["comment_controversy_score"],
        collection_value_score=dimensions["collection_value_score"],
        international_news_score=dimensions["international_news_score"],
        topic_title=topic_title[:120],
        hot_source=source_summary,
        why_short_video=why_short_video(item),
        recommended_script_angle=recommended_script_angle(item),
        hot_summary=f"{item.title}。{item.summary[:180]} {source_line}",
        target_client=target_client,
        user_pain_point=pain_point,
        business_entry_point=business_entry,
        cover_title=make_cover_title(item),
        risk_notice=risk_notice,
        publish_copy=f"{item.title}\n\n这不是国际新闻翻译，而是给中国老板看的资本逻辑：它可能影响企业全球化、海外融资、香港/新加坡路径、家族办公室和全球资产配置判断。\n\n{risk_notice}\n\n{source_line}",
        tags=make_tags(item),
        scripts=platform_scripts(item.title, target_client, pain_point, business_entry),
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
        "corporate_finance": ["融资", "现金流", "资本结构"],
    }.get(item.category, ["财经热点", "海外融资", "资本市场"])
    return base + [item.source]


async def generate_live_topics(count: int = 10) -> list[Topic]:
    news_items = await fetch_latest_news(limit=max(count * 2, 20))
    topics = [build_live_topic(item) for item in news_items[:count]]
    return topics
