import sqlite3

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import json
import requests
import re

import sqlite3


def setup_news_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    qry = """
        CREATE TABLE IF NOT EXISTS news (
        id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        published_at TEXT,
        source TEXT,
        url TEXT,
        related_stocks TEXT,   -- JSON String으로 저장
        related_sectors TEXT,  -- JSON String으로 저장
        sentiment_score REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    cursor.execute(qry)

    conn.commit()
    conn.close()


def setup_ohlcv_database(db_path):
    """데이터베이스와 테이블을 초기 설정합니다. 테이블이 이미 존재하면 만들지 않습니다."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS ohlcv_candles (
            symbol TEXT NOT NULL,           -- 종목 코드
            market_type TEXT,                   -- 시장 구분 (KOSPI, KOSDAQ 등)
            interval TEXT NOT NULL,             -- 캔들 간격 (day, week, month 등)
            candle_date_time TEXT NOT NULL,     -- 캔들 기준 시각 (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
            
            open_price REAL,                    -- 시가
            high_price REAL,                    -- 고가
            low_price REAL,                     -- 저가
            close_price REAL,                   -- 종가
            volume INTEGER,                     -- 거래량
            
            rsi REAL,                           
            ema REAL,
            sma REAL,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (symbol, interval, candle_date_time)
        );
    """
    cursor.execute(create_table_sql)
    
    # 검색 속도 향상을 위한 인덱스 생성
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ohlcv_stock_date ON ohlcv_candles (symbol, candle_date_time);")
    
    conn.commit()
    conn.close()
    print(f"OHLCV 데이터베이스 '{db_path}' 및 'ohlcv_candles' 테이블이 준비되었습니다.")


def setup_database(db_path):
    """데이터베이스와 테이블을 초기 설정합니다. 테이블이 이미 존재하면 만들지 않습니다."""
    # 1. 데이터베이스에 연결 (파일이 없으면 자동으로 생성됩니다)
    conn = sqlite3.connect(db_path)
    # 2. SQL을 실행하기 위한 커서(cursor) 생성
    cursor = conn.cursor()

    # 3. 테이블 생성 SQL 구문 (IF NOT EXISTS 구문으로 오류 방지)
    # rcept_no를 PRIMARY KEY로 지정하여 중복 저장을 방지합니다.
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS financial_reports (
            -- 메타데이터 (보고서의 고유 정보)
            rcept_no TEXT PRIMARY KEY,          -- 접수번호 (이것으로 각 보고서를 구분, 고유값)
            corp_code TEXT NOT NULL,            -- 공시대상회사 고유번호
            stock_code TEXT,                    -- 상장된 경우의 종목 코드
            bsns_year TEXT NOT NULL,            -- 사업 연도
            reprt_code TEXT NOT NULL,           -- 보고서 코드 (11011: 사업보고서 등)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 데이터 저장 시각
        
            -- 연결 재무제표 (CFS) 데이터
            cfs_revenue INTEGER,                -- 매출액 (CFS)
            cfs_operating_income INTEGER,       -- 영업이익 (CFS)
            cfs_net_income INTEGER,             -- 당기순이익 (CFS)
            cfs_total_assets INTEGER,           -- 자산총계 (CFS)
            cfs_total_liabilities INTEGER,      -- 부채총계 (CFS)
            cfs_total_equity INTEGER,           -- 자본총계 (CFS)
            cfs_current_assets INTEGER,         -- 유동자산 (CFS)
            cfs_current_liabilities INTEGER,    -- 유동부채 (CFS)
            cfs_capital_stock INTEGER,          -- 자본금 (CFS)
            cfs_retained_earnings INTEGER,      -- 이익잉여금 (CFS)
            cfs_non_current_assets INTEGER,     -- 비유동자산 (CFS)
            cfs_non_current_liabilities INTEGER,-- 비유동부채 (CFS)
        
            -- 별도 재무제표 (OFS) 데이터
            ofs_revenue INTEGER,                -- 매출액 (OFS)
            ofs_operating_income INTEGER,       -- 영업이익 (OFS)
            ofs_net_income INTEGER,             -- 당기순이익 (OFS)
            ofs_total_assets INTEGER,           -- 자산총계 (OFS)
            ofs_total_liabilities INTEGER,      -- 부채총계 (OFS)
            ofs_total_equity INTEGER,           -- 자본총계 (OFS)
            ofs_current_assets INTEGER,         -- 유동자산 (OFS)
            ofs_current_liabilities INTEGER,    -- 유동부채 (OFS)
            ofs_capital_stock INTEGER,          -- 자본금 (OFS)
            ofs_retained_earnings INTEGER,      -- 이익잉여금 (OFS)
            ofs_non_current_assets INTEGER,     -- 비유동자산 (OFS)
            ofs_non_current_liabilities INTEGER -- 비유동부채 (OFS)
        );
    """

    # 4. SQL 실행
    cursor.execute(create_table_sql)
    conn.commit()
    print(f"데이터베이스 '{db_path}' 및 'financial_reports' 테이블이 준비되었습니다.")

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_reports_corp_code ON financial_reports (corp_code);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_reports_stock_code ON financial_reports (stock_code);"
    )
    print("검색용 인덱스가 준비되었습니다.")

    create_dividends_table_sql = """
    CREATE TABLE IF NOT EXISTS dividends (
        -- 메타데이터 (보고서의 고유 정보)
        rcept_no TEXT PRIMARY KEY,
        corp_code TEXT,
        corp_name TEXT,
        stock_code TEXT,
        stlm_dt DATE,
        stock_kind TEXT,

        -- 연결 재무제표 기반 배당 지표 (CFS)
        cfs_eps REAL,
        cfs_net_income REAL,
        cfs_payout_ratio REAL,

        -- 별도 재무제표 기반 배당 지표 (OFS)
        ofs_dividend_yield REAL,
        ofs_dps_cash REAL,
        ofs_dps_stock REAL,
        ofs_net_income REAL,
        ofs_par_value_per_share REAL,
        ofs_stock_dividend_yield REAL,
        ofs_total_cash_dividend REAL,
        ofs_total_stock_dividend REAL,

        -- 데이터 생성 시각
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_dividends_table_sql)
    print("Table 'dividends' is ready with the new schema.")

    # ... (rest of the function) ...
    conn.commit()
    conn.close()

def test_code():
    # 1. DB 연결
    db_path = "../database/financial_data.db"
    table_name = "financial_reports"
    conn = sqlite3.connect(db_path)

    # 2. 특정 종목의 데이터를 시간순으로 정렬하여 가져오는 SQL 쿼리
    stock_to_find = '005380'
    query = f"SELECT * FROM {table_name} WHERE stock_code = '{stock_to_find}' ORDER BY bsns_year"

    # 3. SQL 쿼리 실행 결과를 pandas 데이터프레임으로 바로 로드
    df = pd.read_sql_query(query, conn)

    # 4. 연결 종료 및 결과 확인
    conn.close()

    # 주요 항목만 선택하여 출력
    print(f"--- {stock_to_find} (현대자동차) 재무 데이터 ---")
    print(df[['bsns_year', 'reprt_code', 'cfs_revenue', 'cfs_operating_income', 'ofs_net_income']])

    # 한글 폰트 설정 (Windows: 'Malgun Gothic', macOS: 'AppleGothic')
    plt.rc('axes', unicode_minus=False) # 마이너스 기호 깨짐 방지


    # 1. 시각화를 위한 데이터 준비
    df_annual = df[df['reprt_code'] == '11011'].copy() # 연간 실적(사업보고서)만 필터링
    df_annual['bsns_year'] = pd.to_numeric(df_annual['bsns_year'])
    scale_factor = 1_000_000_000_000
    df_annual['cfs_revenue_scaled'] = df_annual['cfs_revenue'] / scale_factor
    df_annual['cfs_operating_income_scaled'] = df_annual['cfs_operating_income'] / scale_factor
    # 2. 차트 그리기
    plt.figure(figsize=(10, 6)) # 차트 크기 설정
    plt.plot(df_annual['bsns_year'], df_annual['cfs_revenue_scaled'], marker='o', label='revenue')
    plt.plot(df_annual['bsns_year'], df_annual['cfs_operating_income_scaled'], marker='s', label='operating_income')

    # 3. 차트 꾸미기
    plt.title(f'{stock_to_find}', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.xticks(ticks=df_annual['bsns_year'])
    plt.legend() # 범례 표시
    plt.grid(True) # 그리드 표시
    plt.ticklabel_format(style='plain', axis='y') # y축 지수 표현 없애기
    plt.show()


def flatten_for_inserting_db(data: dict) -> dict:
    flat_data = dict()
    flat_data.update(data["metadata"])

    for k, v in data["cfs"].items():
        flat_data[f"cfs_{k}"] = v

    for k, v in data["ofs"].items():
        flat_data[f"ofs_{k}"] = v

    return flat_data


def insert_data_to_db(db_path, data, table_name="financial_reports"):
    """
    (수정됨) 딕셔너리 데이터를 데이터베이스 테이블에 안전하게 삽입합니다.

    :param db_path: 데이터베이스 파일 경로
    :param data: 삽입할 데이터 (딕셔너리 형태)
    :param table_name: 데이터를 삽입할 테이블 이름
    """
    # 0. 데이터가 비어있으면 함수를 종료합니다.
    if not data:
        print("삽입할 데이터가 없습니다.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 입력된 딕셔너리에서 컬럼(key) 리스트와 값(value) 리스트를 분리합니다.
    #    Python 3.7+ 부터 딕셔너리는 삽입 순서를 보장하므로, keys()와 values()의 순서는 항상 일치합니다.
    columns = list(data.keys())
    values = list(data.values())

    # 2. SQL 구문을 동적으로 생성합니다.
    #    - 컬럼 목록: 'col1, col2, ...'
    #    - 값 목록(Parameter marker): '?, ?, ...'
    #    - 'INSERT OR IGNORE': PRIMARY KEY가 겹치는 데이터는 무시하고 넘어갑니다. (중복 저장 방지)
    insert_sql = f"INSERT OR IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"

    try:
        # 3. SQL 실행: 값은 두 번째 인자로 전달하여 SQL Injection을 방지합니다.
        cursor.execute(insert_sql, values)

        # 4. 변경사항 저장(commit)
        conn.commit()

        print(f"데이터 삽입 완료: '{table_name}' 테이블에 rcept_no='{data.get('rcept_no')}' 삽입")

    except sqlite3.Error as e:
        # DB 작업 중 에러 발생 시 출력
        print(f"데이터베이스 오류 발생: {e}")

    finally:
        # 5. 연결 종료
        conn.close()


def safe_division(numerator, denominator):
    """0으로 나누는 오류를 방지하는 안전한 나눗셈 함수"""
    # 분모가 0이거나, 계산에 필요한 값이 없으면(None) None을 반환
    if denominator is None or denominator == 0 or numerator is None:
        return None
    return numerator / denominator


def insert_stocks():
    dartAPI = OpenDartAPI("3a25446507f9471bc778a9b83e1d14f259f81680")

    years = [2024]
    rpt_codes = [11013, 11012, 11014, 11011]
    stock_list = ["017670"]
    for stock in stock_list:
        cp_info = dartAPI.get_corp_info_by_stock_code(stock)

        for i in years:
            for j in rpt_codes:
                fin_di = dartAPI.get_financial(i, j, cp_info["corp_code"])
                fixed = dartAPI.processing_financial_data(stock, fin_di)
                div_di = dartAPI.get_dividend(i, j, cp_info["corp_code"])
                div_fixed = dartAPI.processing_dividend_data(stock, div_di)
                flatten_financial = flatten_for_inserting_db(fixed)
                flatten_dividend = flatten_for_inserting_db(div_fixed)
                print(flatten_financial)
                print(flatten_dividend)
                insert_data_to_db("../database/financial_data.db", flatten_financial, "financial_reports")
                insert_data_to_db("../database/financial_data.db", flatten_dividend, "dividends")


# --- 메인 실행 부분 ---
if __name__ == "__main__":
    setup_news_database("../../database/main.db")
    setup_ohlcv_database("../../database/main.db")
    # setup_database("./financial_data.db")
    # test_code()
