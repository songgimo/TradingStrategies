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


class CryptoType(Enum):
    STORE_OF_VALUE = "Store of Value" # Similar as an Index
    SMART_CONTRACT = "Smart Contract" # Similar as a Technology
    PAYMENT = "Payment"  # Similar as a Financials


class Interval(Enum):
    MINUTE_1 = "minute1"
    MINUTE_3 = "minute3"
    MINUTE_5 = "minute5"
    MINUTE_15 = "minute15"
    MINUTE_30 = "minute30"
    MINUTE_60 = "minute60"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

    def __str__(self):
        return self.value