import asyncio
import logging
import json

from typing import List, Literal, Dict, Any
from datetime import datetime
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END, START

from src.backend.application.ports.output import LLMOutputPort
from src.backend.domain.entities import MarketAnalysis, TradeStrategy, StockAnalysis
from src.backend.domain.reference_data import MarketSentiment, TradingStrategy

from src.backend.infrastructure.llm.schemas import MarketAnalysisSchema, TradeStrategySchema, TechnicalScreenerSchema, AgentState
from src.backend.infrastructure.llm.prompts import (
    create_analyst_prompt,
    create_screener_prompt,
    create_strategy_generator_prompt,
    create_risk_manager_prompt
)
from src.backend.infrastructure.llm.clients import LLMClients

from src.config.config import settings, STATIC_FOLDER_PATH

logger = logging.getLogger(__name__)


class StrategyGenerationGraph(LLMOutputPort):
    def __init__(self):
        
        self.llm = LLMClients.google_llm_client(temperature=0.3)
        self.analyst_parser = JsonOutputParser(pydantic_object=MarketAnalysisSchema)
        self.screener_parser = JsonOutputParser(pydantic_object=TechnicalScreenerSchema)
        self.strategy_parser = JsonOutputParser(pydantic_object=TradeStrategySchema)
        
        self.analyst_chain = create_analyst_prompt() | self.llm | self.analyst_parser
        self.screener_chain = create_screener_prompt() | self.llm | self.screener_parser
        self.strategy_chain = create_strategy_generator_prompt() | self.llm | self.strategy_parser
        self.risk_chain = create_risk_manager_prompt() | self.llm | self.strategy_parser

        self.app = self._build_graph()

    async def analyze_market(self, news_contents: List[str]) -> MarketAnalysis:
        inputs = {"news_contents": news_contents}
        result_state = await self.ainvoke(inputs)

        analysis_entity = result_state["market_analysis"]
        return analysis_entity
        
    async def generate_strategies(self, news_contents: List[str], stock_analyses: List[dict]) -> List[TradeStrategy]:
        inputs = {
            "news_contents": news_contents,
            "stock_analyses": stock_analyses
        }
        result_state = await self.ainvoke(inputs)
        
        strategies_data = result_state.get("final_validated_strategies", [])
        strategies = []
        for s in strategies_data:
            strategies.append(TradeStrategy(
                symbol=s.get("symbol", ""),
                action=TradingStrategy(s.get("action", "CASH_HOLD")),
                confidence_score=s.get("confidence_score", 0.0),
                entry_price=s.get("entry_price"),
                take_profit=s.get("take_profit"),
                stop_loss=s.get("stop_loss"),
                reasoning=s.get("reasoning", "")
            ))
        return strategies

    async def ainvoke(self, inputs: Dict[str, Any]):
        return await self.app.ainvoke(inputs)

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Add Nodes
        workflow.add_node("market_analyst", self._market_analyst_node)
        workflow.add_node("technical_screener", self._technical_screener_node)
        workflow.add_node("strategy_generator", self._strategy_generator_node)
        workflow.add_node("risk_manager", self._risk_manager_node)

        workflow.add_edge(START, "market_analyst")
        workflow.add_edge("market_analyst", "technical_screener")
        workflow.add_edge("technical_screener", "strategy_generator")
        workflow.add_edge("strategy_generator", "risk_manager")
        workflow.add_edge("risk_manager", END)

        return workflow.compile()

    async def _market_analyst_node(self, state: AgentState):
        news_list = state.get("news_contents", [])
        if not news_list:
            return {"market_analysis": MarketAnalysis(
                date=datetime.now().strftime("%Y-%m-%d"),
                sentiment_score=0.0,
                summary="No news provided",
                primary_sectors=[],
                reasons="N/A"
            )}
            
        full_text = "\n".join(news_list)
        try:
            result = await self.analyst_chain.ainvoke({
                "news_data": full_text,
                "format_instructions": self.analyst_parser.get_format_instructions()
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

    async def _technical_screener_node(self, state: AgentState):
        stock_analyses = state.get("stock_analyses", [])
        market_analysis = state.get("market_analysis")
        
        candidate_stocks = []
        market_context_str = f"Market Sentiment Score: {market_analysis.sentiment_score if market_analysis else 0.0}\nSummary: {market_analysis.summary if market_analysis else 'Unknown'}\nPrimary Sectors: {', '.join(market_analysis.primary_sectors) if market_analysis and market_analysis.primary_sectors else 'None'}"
        
        for stock_ctx in stock_analyses:
            context_str = f"Symbol: {stock_ctx.get('symbol')}\nTechnical: {stock_ctx.get('technical_context')}\nMarket Context:\n{market_context_str}"
            try:
                result = await self.screener_chain.ainvoke({
                    "context_data": context_str,
                    "format_instructions": self.screener_parser.get_format_instructions()
                })
                
                if result.get("is_candidate", False):
                    candidate_stocks.append(stock_ctx.get("symbol"))
                    logger.info(f"Screener logic passed for {stock_ctx.get('symbol')} - Reason: {result.get('reasoning')}")
                else:
                    logger.info(f"Screener logic rejected {stock_ctx.get('symbol')} - Reason: {result.get('reasoning')}")
            except Exception as e:
                logger.error(f"Screener failed for {stock_ctx.get('symbol')}: {e}")
                # Fallback to include the stock if the screener fails
                candidate_stocks.append(stock_ctx.get("symbol"))
                
        return {"candidate_stocks": candidate_stocks}

    async def _strategy_generator_node(self, state: AgentState):
        stock_analyses = state.get("stock_analyses", [])
        market_analysis = state.get("market_analysis")
        candidate_stocks = state.get("candidate_stocks", [])
        
        generated_strategies = []
        for stock_ctx in stock_analyses:
            symbol = stock_ctx.get('symbol')
            if symbol not in candidate_stocks:
                continue
                
            context_str = f"Symbol: {symbol}\nTechnical: {stock_ctx.get('technical_context')}\nMarket Sentiment: {market_analysis.summary if market_analysis else 'Neutral'}\nSectors: {market_analysis.primary_sectors if market_analysis else []}"
            
            try:
                result = await self.strategy_chain.ainvoke({
                    "context_data": context_str,
                    "format_instructions": self.strategy_parser.get_format_instructions()
                })
                generated_strategies.append(result)
            except Exception as e:
                logger.error(f"Strategy generation failed for {stock_ctx.get('symbol')}: {e}")
                
        return {"generated_strategies": generated_strategies}

    async def _risk_manager_node(self, state: AgentState):
        strategies_data = state.get("generated_strategies", [])
        market_analysis = state.get("market_analysis")
        
        final_strategies = []
        market_context_str = f"Market Sentiment Score: {market_analysis.sentiment_score if market_analysis else 0.0}\nSummary: {market_analysis.summary if market_analysis else 'Unknown'}"
        
        for strategy in strategies_data:
            try:
                result = await self.risk_chain.ainvoke({
                    "strategy_data": json.dumps(strategy),
                    "market_context": market_context_str,
                    "format_instructions": self.strategy_parser.get_format_instructions()
                })
                final_strategies.append(result)
            except Exception as e:
                logger.error(f"Risk Management failed for strategy {strategy}: {e}")
                # Fallback to the original strategy if risk check fails
                final_strategies.append(strategy)
                
        return {"final_validated_strategies": final_strategies}


if __name__ == '__main__':
    graph = StrategyGenerationGraph()
    news_path = STATIC_FOLDER_PATH / "contents_for_test.json"
    try:
        with open(news_path, "r") as f:
            data = json.loads(f.read())
        
        asyncio.run(graph.analyze_market(data))
    except FileNotFoundError:
        print("Mock file not found. Skipping standalone execution.")
