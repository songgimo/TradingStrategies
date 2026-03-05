import logging
from typing import List

from datetime import datetime
from src.backend.application.ports.output import LLMOutputPort, DatabaseOutputPort, MarketOutputPort
from src.backend.domain.entities import TradeStrategy
from src.backend.domain.services import IndicatorService
from src.backend.domain.value_objects import MarketContext
from src.backend.domain.reference_data import Interval

logger = logging.getLogger(__name__)

class StrategyGenerationService:
    def __init__(self, 
                 llm_port: LLMOutputPort, 
                 db_port: DatabaseOutputPort, 
                 market_port: MarketOutputPort):
        self.llm_port = llm_port
        self.db_port = db_port
        self.market_port = market_port

    async def run_strategy_generation(self) -> List[TradeStrategy]:
        """
        Orchestrates the multi-agent strategy workflow.
        """
        logger.info("Starting Strategy Generation Service...")
        
        # 1. Fetch recent news
        today = datetime.now().date()
        news_items = self.db_port.get_news_by_date(today)
        news_contents = [n.content for n in news_items] if news_items else []
        
        # 2. Candidate Selection & Technical Screening (Pre-filtering)
        candidate_symbols = self.db_port.get_all_symbols()
        if not candidate_symbols:
            logger.warning("No candidate symbols found in the DB. Ensure data collector is running.")
            return []
            
        from src.backend.domain.specifications import RsiOverSoldSpec, TrendAndPerfectOrderSpec
        
        # Build our custom hard-filter rule: "Either RSI is oversold OR it's in a perfect uptrend order"
        # This prevents sending 200+ useless symbols to the LLM
        screening_rule = RsiOverSoldSpec() | TrendAndPerfectOrderSpec()
            
        stock_analyses = []
        for sym in candidate_symbols:
            try:
                # Need at least 150 days for indicators
                df = self.market_port.get_candle_history(target=sym, interval=Interval.DAY, count=150)
                if df is not None and not df.empty:
                    close_prices = df['Close']
                    sma_result = IndicatorService.get_simple_moving_average_lines(close_prices)
                    ema_result = IndicatorService.get_exponential_moving_average_lies(close_prices)
                    rsi_result = IndicatorService.get_relative_strength_index(close_prices)
                    
                    market_context = MarketContext(sma=sma_result, ema=ema_result, rsi=rsi_result)
                    
                    # Apply Domain Specification Filter
                    if screening_rule.is_satisfied_by(market_context):
                        logger.info(f"Symbol {sym} passed the technical screen.")
                        tech_context_str = (
                            f"SMA(20={sma_result.sma_20:.2f}, 60={sma_result.sma_60:.2f}), "
                            f"RSI(14={rsi_result.rsi_14:.2f})"
                        )
                        
                        stock_analyses.append({
                            "symbol": sym,
                            "technical_context": tech_context_str
                        })
            except Exception as e:
                logger.error(f"Failed to fetch data for {sym}: {e}")
                
        if not stock_analyses:
            logger.info("No stocks passed the technical screen today. Skipping strategy generation.")
            return []
            
        # 3. Graph Execution via LLM Adapter (Only for the surviving candidates)
        logger.info(f"Sending {len(stock_analyses)} screened candidates to the LLM.")
        strategies = await self.llm_port.generate_strategies(news_contents, stock_analyses)
        
        # 4. Save/Log generated strategies
        for s in strategies:
            logger.info(f"Generated Strategy for {s.symbol}: {s.action} at {s.entry_price}")
            
        return strategies
