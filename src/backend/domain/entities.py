from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict

from src.backend.domain.value_objects import Symbol
from src.backend.domain.reference_data import MarketSentiment, TradingStrategy


@dataclass
class News:
    id: str
    title: str
    content: str
    published_at: datetime
    source: str

    related_stocks: List[Symbol] = field(default_factory=list)
    related_sectors: List[str] = field(default_factory=list)

    sentiment_score: float = 0.0

    # AI comment for logging.
    ai_summary: Optional[str] = None

    url: Optional[str] = None


@dataclass
class Stock:
    symbol: Symbol
    name: str
    market: str
    sector: str
    financials: dict = None


@dataclass
class MarketAnalysis:
    date: str

    sentiment_score: float
    summary: str
    primary_sectors: List[str]
    reasons: str

    market_sentiment: Optional[MarketSentiment] = MarketSentiment.NEUTRAL
    trading_strategy: Optional[TradingStrategy] = TradingStrategy.CASH_HOLD

    thought_process: Optional[str] = None
    cited_news_ids: List[str] = field(default_factory=list)

    @property
    def determined_market_sentiment(self) -> MarketSentiment:
        if self.sentiment_score >= 0.3:
            return MarketSentiment.BULLISH
        elif self.sentiment_score <= -0.3:
            return MarketSentiment.BEARISH
        else:
            return MarketSentiment.NEUTRAL

    @property
    def get_recommended_strategy(self) -> TradingStrategy:
        sentiment = self.determined_market_sentiment

        if sentiment == MarketSentiment.BULLISH:
            return TradingStrategy.LONG
        elif sentiment == MarketSentiment.BEARISH:
            return TradingStrategy.SHORT
        else:
            return TradingStrategy.CASH_HOLD
