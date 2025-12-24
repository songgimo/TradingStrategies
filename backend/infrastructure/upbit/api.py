from backend.domain.value_objects import Ticker
from config.config import settings
from backend.application.ports.output import CryptoMarketOutputPort


class UpbitAPI(CryptoMarketOutputPort):
    API_URL = "https://api.upbit.com/v1"
    KEY = settings.upbit_key.get_secret_value()
    SECRET = settings.upbit_secret.get_secret_value()

    def get_ticker(self, ) -> Ticker:
        ...
