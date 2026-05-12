from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from app.schemas.publications import (
    PerformanceAnalysis,
    PerformanceSnapshot,
    PerformanceSnapshotCreate,
    Platform,
    Publication,
    PublicationChannel,
)
from app.schemas.topics import Topic, TopicScript, TopicStatus, TopicUpdateRequest


def now() -> datetime:
    return datetime.now(timezone.utc)


CHANNELS: list[PublicationChannel] = [
    PublicationChannel(id=uuid4(), name="微信视频号", platform="wechat_channels", account_name="默认账号"),
    PublicationChannel(id=uuid4(), name="抖音", platform="douyin", account_name="默认账号"),
    PublicationChannel(id=uuid4(), name="小红书", platform="xiaohongshu", account_name="默认账号"),
]


TOPICS: list[Topic] = [
    Topic(
        id=uuid4(),
        production_date=date.today(),
        status="pending_review",
        category="singapore_capital_market",
        score=88.5,
        risk_score=28,
        topic_title="新加坡资本市场窗口期来了，中国企业该怎么准备？",
        hot_summary="近期新加坡资本市场和跨境融资话题升温，适合切入中国企业海外融资路径选择。",
        target_client="计划海外融资、上市或搭建国际资本结构的中国企业创始人和 CFO。",
        user_pain_point="企业知道要出海融资，但不确定应该选择香港、新加坡还是美国，也不清楚前期结构如何设计。",
        business_entry_point="引导用户咨询海外融资路径、新加坡资本市场对接和全球化资本结构设计。",
        cover_title="新加坡融资窗口来了？",
        risk_notice="不构成投资建议，具体融资路径需结合企业情况判断。",
        publish_copy="新加坡资本市场正在被更多中国企业重新评估。你真正需要比较的，不只是上市地点，而是融资路径、股权结构和未来国际资本故事。",
        tags=["新加坡", "海外融资", "企业出海"],
        scripts=[
            TopicScript(
                script_type="30s",
                estimated_duration_seconds=30,
                full_script="如果你是一家准备出海融资的中国企业，最近一定要重新看新加坡资本市场。关键不是哪里估值最高，而是哪条路径最适合你的业务、股东结构和未来融资节奏。真正专业的准备，是先把资本结构、境外主体和投资人故事设计好，再去谈市场窗口。",
            ),
            TopicScript(
                script_type="60s",
                estimated_duration_seconds=60,
                full_script="最近很多企业重新关注新加坡资本市场。对中国企业来说，这不是简单地多一个上市地点，而是多一种国际融资路径。问题在于，你的业务收入、股东结构、境外主体、未来投资人画像，是否支持这个路径。很多企业等到融资前才开始调整结构，其实已经很被动。更好的做法，是提前做全球化资本结构设计，再比较香港、新加坡、美国或私募融资的组合方案。以上只是市场观察，不构成投资建议。",
            ),
        ],
        created_at=now(),
    ),
    Topic(
        id=uuid4(),
        production_date=date.today(),
        status="approved",
        category="family_office",
        score=81.2,
        risk_score=35,
        topic_title="为什么越来越多高净值家庭关注新加坡家族办公室？",
        hot_summary="新加坡家族办公室仍是跨境财富管理和全球资产配置中的高关注方向。",
        target_client="企业家、高净值家庭、拟进行全球资产配置的家族客户。",
        user_pain_point="想做全球资产配置，但担心合规、税务、投资管理和家族治理问题复杂。",
        business_entry_point="引导客户了解新加坡家族办公室设立、架构规划和海外投资机会对接。",
        cover_title="新加坡家办适合谁？",
        risk_notice="不构成法律、税务或投资建议，家办方案需结合家庭资产、身份和投资目标评估。",
        publish_copy="新加坡家族办公室不是一个简单壳结构，而是资产配置、传承治理和国际投资能力的系统工程。",
        tags=["家族办公室", "新加坡", "全球资产配置"],
        scripts=[
            TopicScript(script_type="30s", estimated_duration_seconds=30, full_script="新加坡家族办公室为什么受关注？核心不是赶潮流，而是把资产配置、家族治理和全球投资能力放进一个合规框架里。适不适合设立，取决于资产规模、投资目标、家庭成员安排和长期治理需求。"),
            TopicScript(script_type="60s", estimated_duration_seconds=60, full_script="很多人一提新加坡家族办公室，就先问成本和门槛。但真正重要的问题是：你的家族资产是否需要跨市场配置？下一代治理如何安排？投资决策和风险控制谁来负责？新加坡的价值在于成熟的金融体系、国际化投资网络和相对清晰的监管框架。但这不等于所有家庭都适合，需要结合资产规模、身份规划和投资目标来设计。"),
        ],
        created_at=now(),
    ),
]

PUBLICATIONS: list[Publication] = []
SNAPSHOTS: list[PerformanceSnapshot] = []
ANALYSES: list[PerformanceAnalysis] = []


def platform_name(platform: Platform) -> str:
    return {
        "wechat_channels": "微信视频号",
        "douyin": "抖音",
        "xiaohongshu": "小红书",
    }[platform]


def list_topics(status: TopicStatus | None = None) -> list[Topic]:
    if status:
        return [topic for topic in TOPICS if topic.status == status]
    return TOPICS


def get_topic(topic_id: UUID) -> Topic:
    for topic in TOPICS:
        if topic.id == topic_id:
            return topic
    raise KeyError("topic not found")


def update_topic(topic_id: UUID, payload: TopicUpdateRequest) -> Topic:
    topic = get_topic(topic_id)
    values = payload.model_dump(exclude_unset=True)
    index = TOPICS.index(topic)
    updated = topic.model_copy(update=values)
    TOPICS[index] = updated
    return updated


def set_topic_status(topic_id: UUID, status: TopicStatus) -> Topic:
    topic = get_topic(topic_id)
    index = TOPICS.index(topic)
    updated = topic.model_copy(update={"status": status})
    TOPICS[index] = updated
    return updated


def create_publication(topic_id: UUID, channel_id: UUID, platform: Platform, published_url: str, published_at: datetime, notes: str | None) -> Publication:
    topic = get_topic(topic_id)
    publication = Publication(
        id=uuid4(),
        topic_id=topic_id,
        channel_id=channel_id,
        platform=platform,
        platform_name=platform_name(platform),
        topic_title=topic.topic_title,
        published_url=published_url,
        published_at=published_at,
        status="metrics_pending",
        notes=notes,
    )
    PUBLICATIONS.append(publication)
    set_topic_status(topic_id, "metrics_pending")
    return publication


def get_publication(publication_id: UUID) -> Publication:
    for publication in PUBLICATIONS:
        if publication.id == publication_id:
            return publication
    raise KeyError("publication not found")


def create_snapshot(publication_id: UUID, payload: PerformanceSnapshotCreate) -> PerformanceSnapshot:
    snapshot = PerformanceSnapshot(id=uuid4(), publication_id=publication_id, captured_at=now(), **payload.model_dump())
    SNAPSHOTS.append(snapshot)
    publication = get_publication(publication_id)
    index = PUBLICATIONS.index(publication)
    PUBLICATIONS[index] = publication.model_copy(update={"status": "metrics_collected"})
    return snapshot


def analyze_publication(publication_id: UUID) -> PerformanceAnalysis:
    publication = get_publication(publication_id)
    publication_snapshots = [snapshot for snapshot in SNAPSHOTS if snapshot.publication_id == publication_id]
    if not publication_snapshots:
        raise ValueError("no performance snapshot available")
    snapshot = sorted(publication_snapshots, key=lambda item: item.hours_since_publish)[-1]
    engagement_rate = (
        snapshot.like_count + snapshot.comment_count * 2 + snapshot.share_count * 3 + snapshot.favorite_count * 2
    ) / max(snapshot.view_count, 1)
    lead_rate = (snapshot.dm_count + snapshot.lead_count * 3) / max(snapshot.view_count, 1)
    view_score = min(snapshot.view_count / 20000 * 100, 100)
    engagement_score = min(engagement_rate / 0.08 * 100, 100)
    lead_score = min(lead_rate / 0.003 * 100, 100)
    completion_score = min((snapshot.completion_rate or 0) / 45 * 100, 100)
    performance_score = round(view_score * 0.25 + engagement_score * 0.3 + min(snapshot.share_count / 200 * 100, 100) * 0.15 + completion_score * 0.1 + lead_score * 0.2, 2)

    if lead_score >= 70:
        label = "high_lead"
    elif engagement_score >= 75:
        label = "high_engagement"
    elif view_score >= 75:
        label = "high_reach"
    else:
        label = "low_performance"

    analysis = PerformanceAnalysis(
        id=uuid4(),
        publication_id=publication_id,
        topic_id=publication.topic_id,
        snapshot_id=snapshot.id,
        performance_score=performance_score,
        engagement_rate=round(engagement_rate, 6),
        lead_rate=round(lead_rate, 6),
        performance_label=label,
        winning_factors=[
            "选题与海外融资、家族办公室或资本市场服务存在明确业务连接",
            "标题具备问题感，适合微信视频号、抖音和小红书的财经用户理解",
        ],
        weak_points=[
            "如果观看高但线索低，下一版需要更早提出客户场景和咨询入口",
        ],
        recommendation="后续生成选题时优先保留清晰客户画像、明确业务切入点和低承诺风险提示。",
        prompt_learning_summary="优先生成能把热点、客户痛点和咨询场景连接起来的选题，标题使用问题式或避坑式表达，脚本前 3 秒直接点出企业家/CFO/家族客户的决策问题。",
        created_at=now(),
    )
    ANALYSES.append(analysis)
    publication_index = PUBLICATIONS.index(publication)
    PUBLICATIONS[publication_index] = publication.model_copy(update={"status": "performance_analyzed"})
    set_topic_status(publication.topic_id, "performance_analyzed")
    return analysis
