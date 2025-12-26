from abc import ABC, abstractmethod
from backend.domain.value_objects import Ticker, Stock, DataOHLCV
from backend.domain.reference_data import StockMarketType, CryptoMarketType
import typing
import pandas as pd # Pragmatic exception!


class StockMarketOutputPort(ABC):
    def get_ohlcv_history(self, symbol: str) -> pd.DataFrame:
        ...

    @abstractmethod
    def get_orderbook(self, symbol: str) -> pd.DataFrame:
        ...

    @abstractmethod
    def get_dividend_history(self, stock: Stock) -> typing.List[Stock]:
        ...

    @abstractmethod
    def get_stock_reports(self, stock: Stock) -> typing.List[Stock]:
        ...

    @abstractmethod
    def get_stock_ohlc(self, stock: Stock) -> typing.List[Stock]:
        ...

    @abstractmethod
    def get_all_stocks(self, market: StockMarketType) -> typing.List[Stock]:
        ...


class CryptoMarketOutputPort(ABC):
    API_URL: str
    KEY: str
    SECRET: str

    @abstractmethod
    def get_ticker(self, symbol: str) -> Ticker:
        ...

    def get_ohlcv_history(self, symbol: str) -> pd.DataFrame:
        ...

    @abstractmethod
    def get_orderbook(self, symbol: str) -> pd.DataFrame:
        ...
