import logging
from typing import List

import pandas as pd

from backend.application.ports.output import MarketOutputPort, DatabaseOutputPort
from backend.domain.value_objects import Symbol
from backend.domain.reference_data import Interval, StockMarketType

logger = logging.getLogger(__name__)


class CollectMarketDataService:
    """
        Use case for collecting market data.

        Orchestrates:
        - Fetching OHLCV data from APIs
        - Storing data in database.
        - Error handling and retry logic
    """

    def __init__(
            self,
            market_port: MarketOutputPort,
            database_port: DatabaseOutputPort,
            market: StockMarketType
    ):
        self._market_output_port = market_port
        self._database_port = database_port
        self._market = market

    def execute(self):
        if self._market in [StockMarketType.KOSPI, StockMarketType.KOSDAQ]:
            history_data = self._market_output_port.get_candles_last_day_history(
                [],
                self._market
            )

        else:
            raise ValueError(
                f"Unsupported market type: {self._market}"
            )

        self._database_port.put_ohlcv_to_database(history_data)
