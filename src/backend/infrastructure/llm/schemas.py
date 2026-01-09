from pydantic import BaseModel, Field

from typing import List


class MarketAnalysisSchema(BaseModel):
    thought_process: str = Field(description="Step-by-step reasoning process analyzing the news impact")

    sentiment_score: float = Field(description="Market sentiment score between -1.0 and 1.0")
    summary: str = Field(description="One sentence summary of the market")
    primary_sectors: List[str] = Field(description="List of leading sectors")
    reasons: str = Field(description="Reasoning for the analysis")

    cited_news_ids: List[str] = Field(description="List of news IDs used for this conclusion")

