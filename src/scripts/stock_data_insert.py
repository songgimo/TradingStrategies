import asyncio
import json

from src.backend.domain.reference_data import Interval, StockMarketType
from src.backend.domain.value_objects import Symbol
from src.backend.infrastructure.api.pykrx_api import PykrxAPI
from src.backend.infrastructure.db.database_api import SQLiteDatabase
from src.config.config import STATIC_FOLDER_PATH


def get_pykrx_data():
    pyr = PykrxAPI()
    db = SQLiteDatabase()
    with open(STATIC_FOLDER_PATH / "kospi_200_codes.json", "r") as f:
        codes = json.loads(f.read())

    symbols = [Symbol(code) for code in codes]
    data = await pyr.get_candles_history(symbols, Interval.DAY, 1)
    data = data.assign(market_type=str(StockMarketType.KOSPI))
    db.put_ohlcv_to_database(data)


def get_google_news():
    gnews = GoogleNews()
    db = SQLiteDatabase()

    results = await gnews.fetch_news()

    db.put_news(results)


# asyncio.run(get_pykrx_data())
asyncio.run(get_google_news())
