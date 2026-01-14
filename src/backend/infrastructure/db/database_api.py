import datetime
import sqlite3
import pandas as pd
import json
import logging

from typing import List, Optional
from src.backend.application.ports.output import DatabaseOutputPort
from src.backend.domain.entities import News, MarketAnalysis
from src.config.config import SQLITE_DB_FOLDER_PATH


logger = logging.getLogger(__name__)


class SQLiteDatabase(DatabaseOutputPort):
    SQLITE_PATH = SQLITE_DB_FOLDER_PATH / "main.db"

    def _connect(self):
        conn = sqlite3.connect(self.SQLITE_PATH)
        cursor = conn.cursor()
        return conn, cursor

    def put_ohlcv_to_database(self, data: pd.DataFrame):
        if data.empty:
            return

        for col in ['candle_date_time', 'symbol', 'market_type', 'interval']:
            if col in data.columns:
                data[col] = data[col].astype(str)

        db_columns = [
            'symbol', 'market_type', 'interval', 'candle_date_time',
            'open_price', 'high_price', 'low_price', 'close_price', 'volume'
        ]
        # Select only columns present in the DataFrame
        columns_to_insert = [c for c in db_columns if c in data.columns]

        if not columns_to_insert:
            return

        conn, cursor = self._connect()
        try:
            placeholders = ', '.join(['?'] * len(columns_to_insert))
            columns_str = ', '.join(columns_to_insert)
            
            # INSERT OR REPLACE handles the Primary Key constraint (stock_code, interval, candle_date_time)
            sql = f"INSERT OR REPLACE INTO ohlcv_candles ({columns_str}) VALUES ({placeholders})"
            
            # Convert DataFrame to list of tuples ensuring column order
            values = [tuple(x) for x in data[columns_to_insert].to_numpy()]
            
            cursor.executemany(sql, values)
            conn.commit()
        except Exception as e:
            print(f"Failed to insert OHLCV data: {e}")
            conn.rollback()
        finally:
            conn.close()

    def put_news(self, news_list: List[News]):
        """
            뉴스 리스트를 DB에 저장 (중복 ID는 무시)
        """
        if not news_list:
            return

        conn, cursor = self._connect()

        try:
            data_to_insert = []
            for n in news_list:
                stocks_str = json.dumps([str(s) for s in n.related_stocks]) if n.related_stocks else "[]"
                sectors_str = json.dumps(n.related_sectors) if n.related_sectors else "[]"

                data_to_insert.append((
                    n.id,
                    n.title,
                    n.content,
                    n.published_at,
                    n.source,
                    n.url,
                    stocks_str,
                    sectors_str,
                    n.sentiment_score
                ))

            cursor.executemany('''
                INSERT OR IGNORE INTO news (
                    id, title, content, published_at, source, url, 
                    related_stocks, related_sectors, sentiment_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data_to_insert)

            conn.commit()

        except Exception as e:
            print(f"Failed to insert news: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_news_by_date(self, target_date: datetime.date) -> Optional[List[News]]:
        conn, cursor = self._connect()
        date_str = target_date.strftime("%Y-%m-%d")
        query = """SELECT id, title, content, published_at, source, url, 
                          related_stocks, related_sectors, sentiment_score 
                   FROM news 
                   WHERE published_at LIKE ?
                """
        try:
            cursor.execute(query, (f"{date_str}%",))
            rows = cursor.fetchall()
            news_list = []
            for row in rows:
                news = News(
                    id=row[0],
                    title=row[1],
                    content=row[2],
                    published_at=row[3],
                    source=row[4],
                    url=row[5],
                    related_stocks=json.loads(row[6]),
                    related_sectors=json.loads(row[7]),
                    sentiment_score=row[8]
                )
                news_list.append(news)
            return news_list

        except Exception as ex:
            logger.error(f"Failed to get news data: {ex}")
            return []
        finally:
            conn.close()

    def save_market_analysis(self, analysis: MarketAnalysis):
        ...
