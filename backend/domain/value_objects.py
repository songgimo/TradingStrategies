from dataclasses import dataclass
from backend.domain.reference_data import CryptoMarketType, StockMarketType, SectorType
import typing
import re


@dataclass(frozen=True)
class CryptoName:
    value: str

    def __post_init__(self):
        if not re.match(r"^[A-Z0-9]{2,10}$", self.value):
            raise ValueError(f"Invalid Crypto Symbol: {self.value}")

    def __str__(self):
        return self.value

    def __format__(self, format_spec):
        return self.value


@dataclass(frozen=True)
class Symbol:
    symbol: str
    description: str


@dataclass(frozen=True)
class TradingPair:
    name: str
    market: typing.Optional[CryptoMarketType]

    def make_symbol(self, market_base=False, splitter=None):
        if splitter is None:
            splitter = ""

        symbol = f"{self.market}{splitter}{self.name}" if market_base else f"{self.name}{splitter}{self.market}"
        if market_base:
            # KRW --> BTC = KRW|BTC
            return Symbol(
                symbol=symbol,
                description=f"{self.market} --> {self.name}",
            )
        else:
            # BTC --> KRW = BTC|KRW
            return Symbol(
                symbol=symbol,
                description=f"{self.name} --> {self.market}",
            )


@dataclass(frozen=True)
class Stock:
    name: str
    code: str
    market: typing.Optional[StockMarketType]
    sector: typing.Optional[SectorType]

    def make_symbol(self):
        return Symbol(
            symbol=self.code,
            description=f"{self.name} ({self.code}), ({self.market}), ({self.sector})"
        )


@dataclass(frozen=True)
class DataOHLCV:
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: int

@dataclass(frozen=True)
class Ticker:
    symbol: Symbol
    price: float
    timestamp: int

