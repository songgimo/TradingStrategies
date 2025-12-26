import sqlite3
import pandas as pd
from datetime import date
from backend.application.ports import input, output
from backend.domain.reference_data import StockMarketType
from backend.domain.value_objects import Symbol



class SQLiteDB(output.StockMarketOutputPort):
    TABLE_STOCK = "stock_info"
    TABLE_REPORT = "financial_reports"
    def __init__(self, con):
        self.__con = con

    def get_stock_reports(self, target: Symbol, start: date, end: date) -> pd.DataFrame:
        # 3. SQL 쿼리 실행 결과를 pandas 데이터프레임으로 바로 로드
        df = pd.read_sql_query(
            sql=f"SELECT * FROM {self.TABLE_REPORT} WHERE symbol = ? ORDER BY bsns_year",
            con=self.__con,
            params=[target.symbol]
        )

        return df

    def get_candle_history(self, target: Symbol, start: date, end: date) -> pd.DataFrame:
        """
        Fetch OHLCV Candle History

        Args:
            target: The Value Object
            start: Python date object
            end: Python date object
        """
        df = pd.read_sql_query(
            sql=f"SELECT * FROM {self.TABLE_STOCK} WHERE symbol = ? AND date BETWEEN ? AND ? ORDER BY date",
            con=self.__con,
            params=[target.symbol, start, end]
        )

        return df
