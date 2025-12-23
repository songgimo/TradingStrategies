from dataclasses import dataclass


@dataclass(frozen=True)
class DataOHLCV:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
