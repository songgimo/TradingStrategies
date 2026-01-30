from src.backend.infrastructure.crawler.mk_rss import MKNews, HKNews
from src.backend.domain.reference_data import NewsSourceType

class NewsCrawlerFactory:
    @staticmethod
    def get_port(source_type: NewsSourceType):
        if source_type in [NewsSourceType.MK_STOCK]:
            return MKNews()
        elif source_type in [NewsSourceType.HK_FINANCE]:
            return HKNews()
        raise ValueError(f"Unsupported news source: {source_type}")

