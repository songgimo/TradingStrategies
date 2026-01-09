from pydantic import BaseModel, Field
from pyparsing import Literal

from src.backend.domain.entities import MarketAnalysis
from typing import List, TypedDict, Optional

from src.backend.domain.reference_data import MarketSentiment, TradingStrategy


class MarketAnalysisSchema(BaseModel):
    thought_process: str = Field(description="Step-by-step reasoning process analyzing the news impact")

    sentiment_score: float = Field(description="Market sentiment score between -1.0 and 1.0")
    summary: str = Field(description="One sentence summary of the market")
    primary_sectors: List[str] = Field(description="List of leading sectors")
    reasons: str = Field(description="Reasoning for the analysis")

    cited_news_ids: List[str] = Field(description="List of news IDs used for this conclusion")


class AgentState(TypedDict):
    news_contents: List[str]
    analysis_dict: Optional[dict]
    market_analysis: Optional[MarketAnalysis]
    
    market_sentiment: Optional[MarketSentiment]
    trading_strategy: Optional[TradingStrategy]

    strategy_action: Optional[str]
