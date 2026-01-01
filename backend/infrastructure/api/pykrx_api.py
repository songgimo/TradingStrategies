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
    def get_candle_history(self, target: Symbol, interval: Interval, count: int = 1) -> pd.DataFrame:
        logger.info(f"Fetching candle history: ticker={target}, interval={interval}, count={count}")
        if interval not in [Interval.DAY, Interval.WEEK, Interval.MONTH]:
            logger.error(f"Invalid interval '{interval}' for ticker {target}")
            raise ValueError("Pykrx only supports Day, Week, Month candle.")

        frq = {
            Interval.DAY: 'd',
            Interval.WEEK: 'w',
            Interval.MONTH: 'm'
        }.get(interval)

        eng_columns = {
            '시가': 'Open',
            '고가': 'High',
            '저가': 'Low',
            '종가': 'Close',
            '거래량': 'Volume',
            '등락률': 'Change'
        }
        ohlcv_df = pd.DataFrame()
        to_date = datetime.datetime.now()
        for _ in range(10):
            from_date = to_date - datetime.timedelta(days=count)

            from_str, to_str = from_date.strftime("%Y%m%d"), to_date.strftime("%Y%m%d")

            logger.debug(f"Fetching candle history from {from_str} to {to_str}")
            result = stock.get_market_ohlcv(from_str, to_str, str(target), frq)
            ohlcv_df = pd.concat([ohlcv_df, result])
            if len(ohlcv_df) >= count:
                break
            to_date = from_date

        ohlcv_df.index.name = 'Date'
        ohlcv_df = ohlcv_df.sort_index(ascending=False).tail(count)
        ohlcv_df.rename(columns=eng_columns, inplace=True)

        return ohlcv_df

    def get_candles_history(self, targets: List[Symbol], interval: Interval, count: int = 200) -> pd.DataFrame:
        logger.info(f"Fetching candle history: ticker={targets}, interval={interval}, count={count}")
        if interval not in [Interval.DAY, Interval.WEEK, Interval.MONTH]:
            logger.error(f"Invalid interval '{interval}' for ticker {targets}")
            raise ValueError("Pykrx only supports Day, Week, Month candle.")

        frq = {
            Interval.DAY: 'd',
            Interval.WEEK: 'w',
            Interval.MONTH: 'm'
        }.get(interval)

        eng_columns = {
            '시가': 'Open',
            '고가': 'High',
            '저가': 'Low',
            '종가': 'Close',
            '거래량': 'Volume',
            '등락률': 'Change'
        }
        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=count)
        from_str, to_str = from_date.strftime("%Y%m%d"), to_date.strftime("%Y%m%d")
        ohlcv_df = stock.get_market_ohlcv(from_date=from_str, to_date=to_str, freq=frq)

        ohlcv_df.index.name = 'Date'
        ohlcv_df = ohlcv_df.sort_index(ascending=False).tail(count)
        ohlcv_df.rename(columns=eng_columns, inplace=True)

        return ohlcv_df
