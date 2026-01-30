from src.backend.application.ports.output import MarketOutputPort
from src.backend.domain.reference_data import StockMarketType, NewsSourceType
from src.backend.infrastructure.api.pykrx_api import PykrxAPI, YFinanceAPI
from src.backend.infrastructure.crawler.mk_rss import MKNews, HKNews


class MarketAPIFactory:
    @staticmethod
    def get_port(market_type: StockMarketType) -> MarketOutputPort:
        if market_type in [StockMarketType.KOSPI, StockMarketType.KOSDAQ]:
            return PykrxAPI()
        elif market_type in [StockMarketType.NASDAQ, StockMarketType.NYSE]:
            return YFinanceAPI()
        raise ValueError(f"Unsupported market: {market_type}")


class NewsCrawlerFactory:
    @staticmethod
    def get_port(source_type: NewsSourceType):
        if source_type in [NewsSourceType.MK_STOCK]:
            return MKNews()
        elif source_type in [NewsSourceType.HK_FINANCE]:
            return HKNews()
        raise ValueError(f"Unsupported news source: {source_type}")
