from __future__ import annotations

from urllib.parse import quote

import httpx

from app.core.config import settings
from app.services.source_adapters.base import HotTopic, make_hot_topic


class ManualSeedSourceAdapter:
    name = "manual_seed_source"

    async def fetch(self, client: httpx.AsyncClient) -> list[HotTopic]:
        return [
            make_hot_topic(
                platform="manual_seed",
                title=keyword,
                url=f"https://www.baidu.com/s?wd={quote(keyword)}",
                heat_score=max(68 - index, 35),
                keywords=[keyword],
                raw={"adapter": self.name, "index": index},
            )
            for index, keyword in enumerate(settings.manual_seed_keyword_list)
        ]
