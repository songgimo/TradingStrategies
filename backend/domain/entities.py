from dataclasses import dataclass, field
import typing
from backend.domain.value_objects import DataOHLCV
from backend.domain.reference_data import StockMarketType, SectorType, CryptoMarketType

# Aggregate
@dataclass
class Stock:
    code: str
    name: str
    market: typing.Optional[StockMarketType]
    sector: typing.Optional[SectorType]

    ohlcv_list: typing.List[DataOHLCV] = field(default_factory=list)

    def add_ohlcv(self, new_data: DataOHLCV):
        ...

