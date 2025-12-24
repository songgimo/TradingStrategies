from abc import ABC, abstractmethod
from backend.domain.entities import Stock
from backend.domain.value_objects import Ticker
from backend.domain.reference_data import StockMarketType
import typing


class StockMarketOutputPort(ABC):
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
    def get_ticker(self, ) -> Ticker:
        ...
