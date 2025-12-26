from dataclasses import dataclass
from typing import Optional

from backend.domain.reference_data import CryptoMarketType, StockMarketType, SectorType
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
    market: Optional[CryptoMarketType]

    def make_symbol(self, market_base=False, splitter=None) -> Symbol:
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
    market: Optional[StockMarketType]
    sector: Optional[SectorType]

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


@dataclass(frozen=True)
class EMAResult:
    ema_20: float
    ema_60: float
    ema_120: float

    @property
    def is_perfect_order(self) -> bool:
        return self.ema_20 > self.ema_60 > self.ema_120


@dataclass(frozen=True)
class SMAResult:
    sma_20: float
    sma_60: float
    sma_120: float

    @property
    def is_a_trend_market(self) -> bool:
        return self.sma_20 > self.sma_120


@dataclass(frozen=True)
class RSIResult:
    rsi_2: float
    rsi_7: float
    rsi_9: float
    rsi_14: float
    rsi_50: float

    @property
    def fast_cross_over_slow(self) -> bool:
        return self.rsi_14 < self.rsi_9


@dataclass(frozen=True)
class MarketContext:
    sma: Optional[SMAResult] = None
    ema: Optional[EMAResult] = None
    rsi: Optional[RSIResult] = None


@dataclass(frozen=True)
class StrategyConfig:
    rsi_oversold_limit: float = 30.0
    rsi_overbought_limit: float = 70.0
