import logging
from typing import List

from backend.application.ports.input import CollectMarketDataUseCase
from backend.application.ports.output import MarketOutputPort
from backend.domain.value_objects import Symbol
from backend.domain.reference_data import Interval, StockMarketType

logger = logging.getLogger(__name__)


class MarketDataService(CollectMarketDataUseCase):
    """
    Application service implementing CollectMarketDataUseCase

    Orchestrates data collection from market APIs and storage
    """

    def __init__(
            self,
            market_output_port: MarketOutputPort,
    ):
        self._market_output_port = market_output_port

    def collecting_ohlcv(
            self,
            targets: List[Symbol],
            interval: Interval,
            count: int
    ):
        self._market_output_port.get_candles_history(
            targets,
            interval,
            count
        )
        ...

    def get_all_symbols(self, market: StockMarketType) -> List[Symbol]:
        ...