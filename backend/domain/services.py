import pandas as pd
import numpy as np
from dataclasses import dataclass

from backend.domain.value_objects import SMAResult, EMAResult


class IndicatorService:
    """
    Pure Domain Service.
    Contains standard financial formulas.
    Inputs are DF/Series, Outputs are computed values.
    """

    @staticmethod
    def get_simple_moving_average_lines(prices: pd.Series) -> SMAResult:
        """
        Calculate the standard 20/60/120 day moving averages.

        Args:
            prices: The price history (Close prices)

        Returns:
            SMA Value Object.
        """
        ma_20 = prices.rolling(window=20).mean().iloc[-1]
        ma_60 = prices.rolling(window=60).mean().iloc[-1]
        ma_120 = prices.rolling(window=120).mean().iloc[-1]
        return SMAResult(
            sma_20=float(ma_20),
            sma_60=float(ma_60),
            sma_120=float(ma_120)
        )

    @staticmethod
    def get_exponential_moving_average_lies(prices: pd.Series) -> EMAResult:
        """
        Calculates Exponential Moving Average (EMA).

        Args:
            prices: The price history (Close prices)

        Returns:
            EMA Value Object.
        """

        ema_20 = prices.ewm(span=20, adjust=False).mean().iloc[-1]
        ema_60 = prices.ewm(span=60, adjust=False).mean().iloc[-1]
        ema_120 = prices.ewm(span=120, adjust=False).mean().iloc[-1]

        return EMAResult(
            ema_20=float(ema_20),
            ema_60=float(ema_60),
            ema_120=float(ema_120)
        )
