from abc import ABC, abstractmethod

from backend.domain.reference_data import Interval, StockMarketType
from backend.domain.value_objects import Symbol
from typing import List


class CollectMarketDataUseCase(ABC):
    """
        Use case for collecting market data.

        Orchestrates:
        - Fetching OHLCV data from APIs
        - Storing data in database.
        - Error handling and retry logic
    """

    @abstractmethod
    def collecting_ohlcv(
            self,
            targets: List[Symbol],
            interval: Interval,
            count: int
    ):
        """
            Collect market data for symbols.
            Args:
                interval: Candle interval (DAY, WEEK, MONTH)
                count: Number of candles to fetch

            Returns:
                {
                    'success_count': int,
                    'failed_count': int,
                    'failed_symbols': List[str],
                    'total_rows': int
                }
        """
