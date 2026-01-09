from src.backend.domain.value_objects import Symbol
from src.config.config import settings
from src.backend.application.ports.output import CryptoMarketOutputPort
import pandas as pd



class UpbitAPI(CryptoMarketOutputPort):
    API_URL = "https://api.upbit.com/v1"
    KEY = settings.upbit_key.get_secret_value()
    SECRET = settings.upbit_secret.get_secret_value()

    def get_candle_history(self, symbol: Symbol) -> pd.DataFrame:
        ...
