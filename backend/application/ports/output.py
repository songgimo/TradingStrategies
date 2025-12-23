from abc import ABC, abstractmethod
from backend.domain.entities import Stock
from backend.domain.reference_data import MarketType
import typing

class StockOutputPort(ABC):
    @abstractmethod
    def get_a_stock_report(self, stock: Stock) -> typing.List[Stock]:
        ...

    @abstractmethod
    def get_a_stock_ohlc(self, stock: Stock) -> typing.List[Stock]:
        ...

    @abstractmethod
    def get_all_stocks(self, market: MarketType) -> typing.List[Stock]:
        ...
