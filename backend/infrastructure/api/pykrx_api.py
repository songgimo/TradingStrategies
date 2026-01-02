from pykrx import stock
import pandas as pd
import datetime
from backend.application.ports.output import MarketOutputPort
from backend.domain.value_objects import Symbol
from backend.domain.reference_data import Interval, StockMarketType
from typing import List
import logging

logger = logging.getLogger(__name__)


class PykrxAPI(MarketOutputPort):
    _ENG_COLUMNS = {
        '시가': 'Open', '고가': 'High', '저가': 'Low',
        '종가': 'Close', '거래량': 'Volume', '등락률': 'Change'
    }
    _INTERVAL_MAP = {
        Interval.DAY: 'd',
        Interval.WEEK: 'w',
        Interval.MONTH: 'm'
    }

    def _validate_and_get_freq(self, interval: Interval) -> str:
        frq = self._INTERVAL_MAP.get(interval)
        if not frq:
            logger.error(f"Invalid interval '{interval}'")
            raise ValueError("Pykrx only supports Day, Week, and Month intervals.")
        return frq

    def _post_process_df(self, df: pd.DataFrame, count: int) -> pd.DataFrame:
        df.index.name = 'Date'
        df = df.sort_index(ascending=False).tail(count)
        df.rename(columns=self._ENG_COLUMNS, inplace=True)
        return df

    def get_candle_history(self, target: Symbol, interval: Interval, count: int = 1) -> pd.DataFrame:
        logger.info(f"Fetching candle history: ticker={target}, interval={interval}, count={count}")
        freq = self._validate_and_get_freq(interval)

        ohlcv_df = pd.DataFrame()
        to_date = datetime.datetime.now()
        for _ in range(10):
            from_date = to_date - datetime.timedelta(days=count)

            from_str, to_str = from_date.strftime("%Y%m%d"), to_date.strftime("%Y%m%d")

            logger.debug(f"Fetching candle history from {from_str} to {to_str}")
            result = stock.get_market_ohlcv(from_str, to_str, str(target), freq)
            ohlcv_df = pd.concat([ohlcv_df, result])
            if len(ohlcv_df) >= count:
                break
            to_date = from_date

        return self._post_process_df(ohlcv_df, count)

    def get_candles_history(self, targets: List[Symbol], interval: Interval, count: int = 200) -> pd.DataFrame:
        logger.info(f"Fetching candle history: ticker={targets}, interval={interval}, count={count}")
        freq = self._validate_and_get_freq(interval)

        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=count)
        from_str, to_str = from_date.strftime("%Y%m%d"), to_date.strftime("%Y%m%d")
        ohlcv_df = stock.get_market_ohlcv(from_date=from_str, to_date=to_str, freq=freq)

        return self._post_process_df(ohlcv_df, count)
