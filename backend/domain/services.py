import pandas as pd
import numpy as np
from dataclasses import dataclass

from backend.domain.value_objects import SMAResult, EMAResult, RSIResult


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


    @staticmethod
    def get_relative_strength_index(prices: pd.Series) -> RSIResult:
        """
        Calculates RSI

        Args:
            prices: A pandas series of close prices.

        Returns:
            RSI Value Object
        """

        delta = prices.diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)

        rsi_data = []
        for period in (2, 7, 9, 14, 50):
            avg_gain = gain.ewm(com=period - 1, adjust=False, min_periods=period).mean()
            avg_loss = loss.ewm(com=period - 1, adjust=False, min_periods=period).mean()

            rs = avg_gain / avg_loss
            rsi_series = 100 - (100 / (1 + rs))

            latest_rsi = rsi_series.iloc[-1]

            if np.isnan(latest_rsi):
                latest_rsi = 0.0
            rsi_data.append(latest_rsi)

        return RSIResult(
            rsi_2=rsi_data[0],
            rsi_7=rsi_data[1],
            rsi_9=rsi_data[2],
            rsi_14=rsi_data[3],
            rsi_50=rsi_data[4],
        )
