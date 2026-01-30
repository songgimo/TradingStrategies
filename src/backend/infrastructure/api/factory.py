from src.backend.application.ports.output import MarketOutputPort
from src.backend.domain.reference_data import StockMarketType
from src.backend.infrastructure.api.pykrx_api import PykrxAPI, YFinanceAPI


class MarketAPIFactory:
    @staticmethod
    def get_port(market_type: StockMarketType) -> MarketOutputPort:
        if market_type in [StockMarketType.KOSPI, StockMarketType.KOSDAQ]:
            return PykrxAPI()
        elif market_type in [StockMarketType.NASDAQ, StockMarketType.NYSE]:
            return YFinanceAPI()
        raise ValueError(f"Unsupported market: {market_type}")

