import json
import logging
from typing import List
from datetime import datetime
from langchain_core.output_parsers import JsonOutputParser


from backend.application.ports.output import LLMOutputPort
from backend.domain.entities import MarketAnalysis
from backend.infrastructure.llm.schemas import MarketAnalysisSchema
from backend.infrastructure.llm.prompts import create_analyst_prompt
from backend.infrastructure.llm.clients import LLMClients

logger = logging.getLogger(__name__)


class LangChainAdapter(LLMOutputPort):
    def __init__(self):
        self.llm = LLMClients.google_llm_client(temperature=0.3)

        self.parser = JsonOutputParser(pydantic_object=MarketAnalysisSchema)

        self.prompts = create_analyst_prompt()


    async def analyze_market(self, news_items: List[str]) -> MarketAnalysis:
        chain = self.prompts | self.llm | self.parser
        full_text = "\n".join(news_items)
        try:
            result = await chain.ainvoke({
                "news_data": full_text,
                "format_instructions": self.parser.get_format_instructions()
            })

            return MarketAnalysis(
                date=datetime.now().strftime("%Y-%m-%d"),
                sentiment_score=result['sentiment_score'],
                summary=result['summary'],
                primary_sectors=result['primary_sectors'],
                reasons=result['reasons'],

                thought_process=result['thought_process'],
                cited_news_ids=result['cited_news_ids']
            )

        except Exception as e:
            logger.error(f"LangChain Analysis Failed: {e}")
            return MarketAnalysis(
                date=datetime.now().strftime("%Y-%m-%d"),
                sentiment_score=0.0,
                summary="Analysis Failed",
                primary_sectors=[],
                reasons=str(e)
            )
