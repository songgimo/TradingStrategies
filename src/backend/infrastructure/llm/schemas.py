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


class TradeStrategySchema(BaseModel):
    symbol: str = Field(description="The stock symbol or name")
    action: str = Field(description="The recommended action: LONG, SHORT, or CASH_HOLD")
    confidence_score: float = Field(description="Confidence score for this strategy, between 0.0 and 1.0")
    entry_price: Optional[float] = Field(description="Recommended entry price, if applicable", default=None)
    take_profit: Optional[float] = Field(description="Target price to take profit", default=None)
    stop_loss: Optional[float] = Field(description="Stop loss price", default=None)
    reasoning: str = Field(description="Detailed reasoning combining technical and sentiment analysis")



class AgentState(TypedDict):
    news_contents: List[str]
    analysis_dict: Optional[dict]
    market_analysis: Optional[MarketAnalysis]
    
    candidate_stocks: Optional[List[str]]
    stock_analyses: Optional[List[dict]]
    generated_strategies: Optional[List[dict]]
    final_validated_strategies: Optional[List[dict]]
    
    market_sentiment: Optional[MarketSentiment]
    trading_strategy: Optional[TradingStrategy]

    strategy_action: Optional[str]
