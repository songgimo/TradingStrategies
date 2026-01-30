import time
import random
import logging
import datetime
import pandas as pd
from typing import List

from pykrx import stock
from src.backend.application.ports.output import MarketOutputPort
from src.backend.domain.value_objects import Symbol
from src.backend.domain.reference_data import Interval, StockMarketType

logger = logging.getLogger(__name__)


class PykrxAPI(MarketOutputPort):
    _ENG_COLUMNS = {
        '시가': 'open_price', '고가': 'high_price', '저가': 'low_price',
        '종가': 'close_price', '거래량': 'volume', "등락률": "change", "티커": "symbol"
    }
    _INTERVAL_MAP = {
        Interval.DAY: 'd',
        Interval.WEEK: 'w',
        Interval.MONTH: 'm'
    }

    def get_candle_history(self, target: Symbol, interval: Interval, count: int = 1) -> pd.DataFrame:
        logger.info(f"Fetching candle history: ticker={target}, interval={interval}, count={count}")
        freq = self._INTERVAL_MAP.get(interval)
        if not freq:
            logger.error(f"Invalid interval '{interval}'")
            raise ValueError("Pykrx only supports Day, Week, and Month intervals.")

        ohlcv_df = pd.DataFrame()
        to_date = datetime.datetime.now()
        for _ in range(10):
            from_date = to_date - datetime.timedelta(days=count + 5)
            from_str, to_str = from_date.strftime("%Y%m%d"), to_date.strftime("%Y%m%d")

            logger.debug(f"Fetching candle history from {from_str} to {to_str}")
            result = stock.get_market_ohlcv(
                from_str,
                to_str,
                str(target),
                freq
            )
            ohlcv_df = pd.concat([ohlcv_df, result])
            if len(ohlcv_df) >= count:
                break
            if ohlcv_df.empty and result.empty:
                logger.error(f"The target is not available symbol: {target}")
                return pd.DataFrame()
            to_date = from_date

        ohlcv_df.index.name = 'candle_date_time'
        df = ohlcv_df.sort_index(ascending=False).head(count).rename(columns=self._ENG_COLUMNS).assign(
            interval=str(interval),
            symbol=str(target)
        )
        df.reset_index(inplace=True)
        return df

    def get_candles_history(self, targets: List[Symbol], interval: Interval, count: int = 1) -> pd.DataFrame:
        results = []
        for target in targets:
            time.sleep(random.uniform(0.2, 0.7))
            try:
                df = self.get_candle_history(target, interval, count)
                if not df.empty:
                    results.append(df)
            except Exception as e:
                logger.error(f"Failed to fetch {target}: {e}")

        if not results:
            return pd.DataFrame()

        return pd.concat(results, ignore_index=True)

    def get_all_symbols(self, market_type: StockMarketType):
        pass