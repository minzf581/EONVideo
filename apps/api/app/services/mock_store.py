from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional
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

TOPIC_BLUEPRINTS = [
    {
        "category": "ai_capital",
        "score": 86.8,
        "risk_score": 30,
        "topic_title": "AI 公司估值越来越高，中国企业出海融资该讲什么故事？",
        "hot_summary": "AI 投资热度持续，海外资本更关注商业化、算力成本和全球客户结构。",
        "target_client": "AI、SaaS、智能制造企业创始人和 CFO。",
        "user_pain_point": "技术亮点很多，但不知道如何把 AI 能力转化成海外投资人听得懂的资本故事。",
        "business_entry_point": "切入海外融资材料、投资人沟通和全球化资本结构设计。",
        "cover_title": "AI 公司出海融资怎么讲？",
        "tags": ["AI", "海外融资", "资本故事"],
    },
    {
        "category": "hongkong_ipo",
        "score": 84.1,
        "risk_score": 32,
        "topic_title": "香港 IPO 回暖，哪些企业应该重新评估上市路径？",
        "hot_summary": "香港资本市场活跃度提升，适合讨论中国企业上市地比较和窗口期判断。",
        "target_client": "计划上市或 Pre-IPO 融资的企业家、董事会和 CFO。",
        "user_pain_point": "不确定香港、新加坡、美国或私募融资哪条路径更合适。",
        "business_entry_point": "切入上市地比较、上市前融资和资本结构梳理。",
        "cover_title": "香港 IPO 值得重看？",
        "tags": ["香港IPO", "上市路径", "融资"],
    },
    {
        "category": "rwa",
        "score": 79.6,
        "risk_score": 48,
        "topic_title": "RWA 很热，但企业不能只看到融资想象力",
        "hot_summary": "RWA 相关话题升温，但监管、底层资产和投资者适当性仍是关键。",
        "target_client": "有资产证券化、跨境融资或数字资产探索需求的企业。",
        "user_pain_point": "希望借 RWA 扩大融资渠道，但担心合规边界和投资人接受度。",
        "business_entry_point": "切入跨境融资结构、合规风险评估和海外投资人对接。",
        "cover_title": "RWA 不是万能融资术",
        "tags": ["RWA", "合规", "跨境融资"],
    },
    {
        "category": "us_china",
        "score": 82.3,
        "risk_score": 55,
        "topic_title": "中美关系变化下，企业出海融资要准备两套预案",
        "hot_summary": "中美关系和监管环境变化，会影响企业海外融资、上市和投资人沟通。",
        "target_client": "有美国客户、美元基金股东或海外上市计划的中国企业。",
        "user_pain_point": "担心政策变化影响估值、投资人信心和上市节奏。",
        "business_entry_point": "切入多市场融资路径和资本结构韧性设计。",
        "cover_title": "出海融资要有备选路",
        "tags": ["中美关系", "企业出海", "资本结构"],
    },
    {
        "category": "family_office",
        "score": 83.7,
        "risk_score": 38,
        "topic_title": "设立新加坡家族办公室前，先问这三个问题",
        "hot_summary": "新加坡家族办公室持续受到企业家家庭关注，但设立前需要明确目标和治理需求。",
        "target_client": "企业家、高净值家庭、家族企业二代。",
        "user_pain_point": "知道新加坡家办很热，但不知道自己是否真的适合。",
        "business_entry_point": "切入家办设立评估、资产配置目标和海外投资机会对接。",
        "cover_title": "家办设立前问3件事",
        "tags": ["家族办公室", "新加坡", "资产配置"],
    },
    {
        "category": "singapore_capital_market",
        "score": 87.4,
        "risk_score": 26,
        "topic_title": "为什么新加坡适合做中国企业的国际资本跳板？",
        "hot_summary": "新加坡的金融体系、国际投资人网络和区域总部属性，适合讨论出海资本结构。",
        "target_client": "准备设立海外总部或进行国际融资的中国企业。",
        "user_pain_point": "想出海但缺少清晰的控股、融资和投资人对接路径。",
        "business_entry_point": "切入新加坡资本市场对接和全球化架构设计。",
        "cover_title": "新加坡为何是资本跳板？",
        "tags": ["新加坡", "企业出海", "资本结构"],
    },
    {
        "category": "overseas_investment",
        "score": 78.9,
        "risk_score": 42,
        "topic_title": "海外投资机会很多，企业家最该先看风险结构",
        "hot_summary": "海外投资机会增加，但区域、汇率、退出和监管风险需要系统评估。",
        "target_client": "寻找海外投资机会的企业家、家族办公室和产业投资人。",
        "user_pain_point": "看到很多项目，但不知道如何判断风险和退出路径。",
        "business_entry_point": "切入海外投资机会筛选、尽调框架和跨境交易结构。",
        "cover_title": "海外投资先看风险",
        "tags": ["海外投资", "尽调", "家族办公室"],
    },
    {
        "category": "enterprise_globalization",
        "score": 85.6,
        "risk_score": 28,
        "topic_title": "中国企业出海，不只是注册一家海外公司",
        "hot_summary": "越来越多中国企业推进全球化，但资本结构、税务合规和融资路径需要同步设计。",
        "target_client": "正在出海的制造业、科技、消费和跨境服务企业。",
        "user_pain_point": "已经有海外业务，但股权、融资和总部架构没有系统设计。",
        "business_entry_point": "切入全球化资本结构设计和海外融资准备。",
        "cover_title": "出海不是只注册公司",
        "tags": ["企业出海", "全球化", "资本结构"],
    },
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


def build_topic(blueprint: dict[str, object]) -> Topic:
    title = str(blueprint["topic_title"])
    target_client = str(blueprint["target_client"])
    user_pain_point = str(blueprint["user_pain_point"])
    business_entry_point = str(blueprint["business_entry_point"])
    risk_notice = "以上内容仅作市场观察和商业信息分享，不构成投资、法律或税务建议。具体方案需结合企业实际情况评估。"
    return Topic(
        id=uuid4(),
        production_date=date.today(),
        status="pending_review",
        category=str(blueprint["category"]),
        score=float(blueprint["score"]),
        risk_score=float(blueprint["risk_score"]),
        topic_title=title,
        hot_summary=str(blueprint["hot_summary"]),
        target_client=target_client,
        user_pain_point=user_pain_point,
        business_entry_point=business_entry_point,
        cover_title=str(blueprint["cover_title"]),
        risk_notice=risk_notice,
        publish_copy=f"{title}。真正重要的不是追热点，而是判断这个热点和你的融资路径、资本结构、投资人沟通是否有关。",
        tags=list(blueprint["tags"]),
        scripts=[
            TopicScript(
                script_type="30s",
                estimated_duration_seconds=30,
                full_script=f"{title} 如果你是{target_client}，最需要关注的不是新闻本身，而是它会不会影响你的融资路径、投资人判断和海外架构。{user_pain_point}，这正是需要提前规划的地方。",
            ),
            TopicScript(
                script_type="60s",
                estimated_duration_seconds=60,
                full_script=f"{title} 很多企业看到热点，第一反应是追窗口。但对{target_client}来说，更重要的是把热点翻译成自己的资本决策。你的痛点可能是：{user_pain_point}。这时候需要看的不是单一市场，而是业务、股东结构、融资节奏和未来投资人画像是否匹配。我的业务切入点是：{business_entry_point}。以上只是市场观察，不构成投资建议。",
            ),
        ],
        created_at=now(),
    )


def ensure_daily_topics(count: int = 10) -> list[Topic]:
    if len(TOPICS) >= count:
        return TOPICS[:count]
    for blueprint in TOPIC_BLUEPRINTS:
        if len(TOPICS) >= count:
            break
        TOPICS.append(build_topic(blueprint))
    return TOPICS[:count]


def list_topics(status: Optional[TopicStatus] = None) -> list[Topic]:
    ensure_daily_topics()
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


def create_publication(topic_id: UUID, channel_id: UUID, platform: Platform, published_url: str, published_at: datetime, notes: Optional[str]) -> Publication:
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
