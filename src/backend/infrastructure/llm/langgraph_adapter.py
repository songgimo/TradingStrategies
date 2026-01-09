import asyncio
import logging
import json

from typing import List, Literal, Dict, Any
from datetime import datetime
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END, START

from src.backend.application.ports.output import LLMOutputPort
from src.backend.domain.entities import MarketAnalysis
from src.backend.domain.reference_data import MarketSentiment, TradingStrategy

from src.backend.infrastructure.llm.schemas import MarketAnalysisSchema, AgentState
from src.backend.infrastructure.llm.prompts import create_analyst_prompt
from src.backend.infrastructure.llm.clients import LLMClients

from src.config.config import settings, STATIC_FOLDER_PATH

logger = logging.getLogger(__name__)


class LangGraphAdapter(LLMOutputPort):
    def __init__(self):
        self._graph_app = RoutingPattern()

    async def analyze_market(self, news_contents: List[str]) -> MarketAnalysis:
        inputs = {"news_contents": news_contents}
        result_state = await self._graph_app.ainvoke(inputs)

        analysis_entity = result_state["market_analysis"]
        analysis_entity.market_condition = result_state.get("sentiment_category", "neutral")
        analysis_entity.recommended_strategy = result_state.get("strategy_action", "wait")

        return analysis_entity


class RoutingPattern:
    def __init__(self):
        self.llm = LLMClients.google_llm_client(temperature=0.3)
        self.parser = JsonOutputParser(pydantic_object=MarketAnalysisSchema)
        self.prompts = create_analyst_prompt()
        self.chain = self.prompts | self.llm | self.parser

        self.app = self._build_graph()

    async def ainvoke(self, inputs: Dict[str, Any]):
        return await self.app.ainvoke(inputs)

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Add Nodes
        workflow.add_node("market_analyst", self._market_analyst_node)
        workflow.add_node(TradingStrategy.LONG.value, self._long_strategy_node)
        workflow.add_node(TradingStrategy.CASH_HOLD.value, self._wait_and_see_node)
        workflow.add_node(TradingStrategy.SHORT.value, self._short_strategy_node)

        workflow.add_edge(START, "market_analyst")

        workflow.add_conditional_edges(
            "market_analyst",
            self._sentiment_router,
            {
                MarketSentiment.BULLISH: TradingStrategy.LONG.value,
                MarketSentiment.NEUTRAL: TradingStrategy.CASH_HOLD.value,
                MarketSentiment.BEARISH: TradingStrategy.SHORT.value,
            }
        )
        workflow.add_edge(TradingStrategy.LONG.value, END)
        workflow.add_edge(TradingStrategy.SHORT.value, END)
        workflow.add_edge(TradingStrategy.CASH_HOLD.value, END)

        return workflow.compile()

    def _sentiment_router(self, state: AgentState):
        analysis = state.get("market_analysis")
        if not analysis:
            return MarketSentiment.NEUTRAL
        return analysis.determined_market_sentiment

    async def _market_analyst_node(self, state: AgentState):
        news_list = state.get("news_contents")
        full_text = "\n".join(news_list)
        try:
            result = await self.chain.ainvoke({
                "news_data": full_text,
                "format_instructions": self.parser.get_format_instructions()
            })
            analysis_entity = MarketAnalysis(
                date=datetime.now().strftime("%Y-%m-%d"),
                sentiment_score=result.get('sentiment_score', 0.0),
                summary=result.get('summary', "Analysis Failed"),
                primary_sectors=result.get('primary_sectors', []),
                reasons=result.get('reasons', ""),
                thought_process=result.get('thought_process', ""),
                cited_news_ids=result.get('cited_news_ids', [])
            )
            return {"analysis_dict": result, "market_analysis": analysis_entity}
        except Exception as e:
            logger.error(f"Market Analysis Node Failed: {e}")
            return {"market_analysis": MarketAnalysis(
                date=datetime.now().strftime("%Y-%m-%d"),
                sentiment_score=0.0,
                summary=f"Error: {str(e)}",
                primary_sectors=[],
                reasons="System Error"
            )}

    async def _long_strategy_node(self, state: AgentState):
        return {"sentiment_category": "bullish", "strategy_action": "long_momentum"}

    async def _short_strategy_node(self, state: AgentState):
        return {"sentiment_category": "bearish", "strategy_action": "short_selling"}

    async def _wait_and_see_node(self, state: AgentState):
        return {"sentiment_category": "neutral", "strategy_action": "cash_hold"}


if __name__ == '__main__':
    graph = RoutingPattern()
    news_path = STATIC_FOLDER_PATH / "contents_for_test.json"
    with open(news_path, "r") as f:
        data = json.loads(f.read())

    asyncio.run(graph.ainvoke({"news_contents": data}))
