from enum import Enum

class StockMarketType(Enum):
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"
    NASDAQ = "NASDAQ"
    NYSE = "NYSE"

    def __str__(self):
        return self.value

    def __format__(self, format_spec):
        return self.value


class SectorType(Enum):
    ENERGY = "Energy"
    MATERIALS = "Materials"
    INDUSTRIALS = "Industrials"
    CONSUMER_DISCRETIONARY = "Consumer Discretionary"
    CONSUMER_STAPLES = "Consumer Staples"
    HEALTH_CARE = "Health Care"
    FINANCIALS = "Financials"
    INFORMATION_TECHNOLOGY = "Information Technology"
    COMMUNICATION_SERVICES = "Communication Services"
    UTILITIES = "Utilities"
    REAL_ESTATE = "Real Estate"

    def __str__(self):
        return self.value

    def __format__(self, format_spec):
        return self.value


class CryptoMarketType(Enum):
    KOREAN_WON = "KRW"
    BITCOIN = "BTC"
    ETHEREUM = "ETH"

    def __str__(self):
        return self.value

    def __format__(self, format_spec):
        return self.value
