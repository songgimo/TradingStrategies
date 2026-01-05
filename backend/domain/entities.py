from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List

from backend.domain.value_objects import Symbol


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