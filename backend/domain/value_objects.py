from dataclasses import dataclass
from backend.domain.reference_data import CryptoMarketType
import typing
import re


@dataclass(frozen=True)
class DataOHLCV:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Ticker:
    market: str
    price: float
    timestamp: int


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
class TradingPair:
    name: str
    market: typing.Optional[CryptoMarketType]

    def make_symbol(self, market_base=False):
        if self.name is None:
            raise ValueError("Currency name is not valid")
        elif self.market is None:
            raise ValueError("Market name is not valid")

        # KRW --> BTC = KRWBTC || BTC --> KRW = BTCKRW
        return f"{self.market}{self.name}" if market_base else f"{self.name}{self.market}"
