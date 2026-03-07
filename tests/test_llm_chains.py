import asyncio
import json
from src.backend.infrastructure.llm.langgraph_adapter import StrategyGenerationGraph

import pytest

@pytest.fixture
def graph():
    return StrategyGenerationGraph()

@pytest.mark.asyncio
async def test_market_analyst(graph: StrategyGenerationGraph):
    print("=== 1. Testing Market Analyst ===")
    mock_news = [
        "삼성전자, 4분기 어닝쇼크... 반도체 재고 증가 및 영업이익 반토막",
        "한국은행 기준금리 인하, 증시 부양 기대감 커져"
    ]
    
    # Simulate news parsing directly
    full_text = "\n".join(mock_news)
    result = await graph.analyst_chain.ainvoke({
        "news_data": full_text,
        "format_instructions": graph.analyst_parser.get_format_instructions()
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n")


@pytest.mark.asyncio
async def test_strategy_generator(graph: StrategyGenerationGraph):
    print("=== 2. Testing Strategy Generator ===")
    mock_context_str = (
        "Symbol: 005930 (Samsung Electronics)\n"
        "Technical: SMA(20=71000, 60=74000), RSI(14=28.5)\n"
        "Market Sentiment: Bearish\n"
        "Sectors: ['Semiconductors']"
    )
    
    result = await graph.strategy_chain.ainvoke({
        "context_data": mock_context_str,
        "format_instructions": graph.strategy_parser.get_format_instructions()
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n")


@pytest.mark.asyncio
async def test_risk_manager(graph: StrategyGenerationGraph):
    print("=== 3. Testing Risk Manager ===")
    mock_strategy = {
        "symbol": "005930",
        "action": "LONG",
        "confidence_score": 0.3,
        "entry_price": 71000,
        "take_profit": 90000,
        "stop_loss": 40000,
        "reasoning": "RSI is extremely oversold. Going all in on the rebound."
    }
    
    # Intentionally passing a very risky strategy (stop loss is way too low, confidence is low)
    # in a bearish market to see if Risk Manager adjusts it.
    mock_market_context = "Market Sentiment Score: -0.6\nSummary: Bearish"
    
    result = await graph.risk_chain.ainvoke({
        "strategy_data": json.dumps(mock_strategy),
        "market_context": mock_market_context,
        "format_instructions": graph.strategy_parser.get_format_instructions()
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n")

