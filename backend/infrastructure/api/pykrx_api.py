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
            from_date = to_date - datetime.timedelta(days=count)

            from_str, to_str = from_date.strftime("%Y%m%d"), to_date.strftime("%Y%m%d")

            logger.debug(f"Fetching candle history from {from_str} to {to_str}")
            result = stock.get_market_ohlcv(from_str, to_str, str(target), freq)
            ohlcv_df = pd.concat([ohlcv_df, result])
            if len(ohlcv_df) >= count:
                break
            if ohlcv_df.empty:
                logger.error(f"The target is not available symbol: {target}")
                return pd.DataFrame()
            to_date = from_date

        ohlcv_df.index.name = 'candle_date_time'
        df = ohlcv_df.sort_index(ascending=False).head(count).rename(columns=self._ENG_COLUMNS).assign(interval=str(Interval.DAY), symbol=str(target))
        df.reset_index(inplace=True)
        return df

    def get_candles_last_day_history(self, targets: List[Symbol], market: StockMarketType) -> pd.DataFrame:
        logger.info(f"Fetching candle history: ticker={targets}")
        to_date = datetime.datetime.now()
        ohlcv_df = pd.DataFrame()

        for _ in range(10):
            from_date = to_date - datetime.timedelta(days=1)
            from_str, to_str = from_date.strftime("%Y%m%d"), to_date.strftime("%Y%m%d")
            data = stock.get_market_ohlcv(date=from_str, market=str(market))
            if data.iloc[-1].values[-1] != 0:
                ohlcv_df = data
                break

            to_date = from_date
        ohlcv_df.drop(columns=["거래대금", "시가총액"], inplace=True)
        ohlcv_df.rename(columns=self._ENG_COLUMNS, inplace=True)
        ohlcv_df.assign(interval=str(Interval.DAY), candle_date_time=to_date.strftime("%Y-%m-%d"))
        return ohlcv_df

    def get_all_symbols(self, market_type: StockMarketType):
        ...
        # logger.info("Fetching all symbols from markets.")
        #
        # if not market_type in [market_type.KOSPI, market_type.KOSDAQ]:
        #     logger.error(f"Invalid MarketType '{market_type}'")
        #     raise ValueError("Pykrx only supports KOSPI and KOSDAQ markets")
        #
        # json_file = settings.json_file_path + "stock_codes.json"
        # with open(json_file, "r") as f:
        #     data = json.loads(f.read())
