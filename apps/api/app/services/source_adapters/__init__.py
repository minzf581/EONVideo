from app.services.source_adapters.baidu_hotsearch import BaiduHotsearchAdapter
from app.services.source_adapters.finance_news import FinanceNewsAdapter
from app.services.source_adapters.manual_seed_source import ManualSeedSourceAdapter
from app.services.source_adapters.third_party_hot_api import ThirdPartyHotApiAdapter
from app.services.source_adapters.wechat_article_source import WechatArticleSourceAdapter
from app.services.source_adapters.weibo_hotsearch import WeiboHotsearchAdapter

__all__ = [
    "BaiduHotsearchAdapter",
    "FinanceNewsAdapter",
    "ManualSeedSourceAdapter",
    "ThirdPartyHotApiAdapter",
    "WechatArticleSourceAdapter",
    "WeiboHotsearchAdapter",
]
