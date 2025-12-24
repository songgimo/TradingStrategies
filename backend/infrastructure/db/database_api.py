import sqlite3
import pandas as pd
from backend.application.ports import input, output
from backend.domain.entities import Stock
from backend.domain.reference_data import StockMarketType


class SQLiteDB(output.StockMarketOutputPort):
    TABLE_STOCK = "stock_info"
    TABLE_REPORT = "financial_reports"
    def __init__(self, con):
        self.__con = con

    def get_stock_reports(self, stock: Stock) -> pd.DataFrame:
        # 3. SQL 쿼리 실행 결과를 pandas 데이터프레임으로 바로 로드
        df = pd.read_sql_query(
            sql=f"SELECT * FROM {self.TABLE_REPORT} WHERE stock_code = ? ORDER BY bsns_year",
            con=self.__con,
            params=[stock.code]
        )

        return df

    def get_stock_ohlc(self, stock: Stock):
        ...

    def get_all_stocks(self, market: StockMarketType):
        ...
