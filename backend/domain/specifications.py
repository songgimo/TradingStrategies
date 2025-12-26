from backend.domain.value_objects import SMAResult, EMAResult, MarketContext, StrategyConfig
from abc import ABC, abstractmethod


class TradingCondition(ABC):
    @abstractmethod
    def is_satisfied_by(self, context: MarketContext) -> bool:
        ...

    def and_(self, other: "TradingCondition") -> "TradingCondition":
        return AndSpecification(self, other)

    def or_(self, other: "TradingCondition") -> "TradingCondition":
        return OrSpecification(self, other)

    def __and__(self, other):
        return self.and_(other)

    def __or__(self, other):
        return self.or_(other)

class AndSpecification(TradingCondition):
    def __init__(self, one: TradingCondition, other: TradingCondition):
        self.one = one
        self.other = other

    def is_satisfied_by(self, ctx: MarketContext) -> bool:
        return self.one.is_satisfied_by(ctx) and self.other.is_satisfied_by(ctx)


class OrSpecification(TradingCondition):
    def __init__(self, one: TradingCondition, other: TradingCondition):
        self.one = one
        self.other = other

    def is_satisfied_by(self, ctx: MarketContext) -> bool:
        return self.one.is_satisfied_by(ctx) or self.other.is_satisfied_by(ctx)


class TrendAndPerfectOrderSpec(TradingCondition):
    def is_satisfied_by(self, ctx: MarketContext) -> bool:
        if not ctx.sma or not ctx.ema:
            return False
        return ctx.sma.is_a_trend_market and ctx.ema.is_perfect_order


class RsiFastCrossOverSlowSpec(TradingCondition):
    def __init__(self, config: StrategyConfig):
        self.__config = config

    def is_satisfied_by(self, ctx: MarketContext) -> bool:
        if ctx.rsi is None:
            return False
        return ctx.rsi.fast_cross_over_slow
