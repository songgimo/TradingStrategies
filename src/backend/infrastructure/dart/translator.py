_MAP_FOR_FINANCIAL_REPORT = {
    # --- 손익계산서 (Income Statement) 주요 항목 ---
    "매출액": "revenue",
    "영업이익": "operating_income",
    "당기순이익": "net_income",
    "당기순이익(손실)": "net_income",  # '당기순이익'과 동일하게 취급
    "법인세비용차감전순이익": "pretax_net_income",  # 기존 'net_income' 대신 명확한 이름으로 변경

    # --- 재무상태표 (Balance Sheet) 주요 항목 ---
    "유동자산": "current_assets",
    "비유동자산": "non_current_assets",
    "자산총계": "total_assets",

    "유동부채": "current_liabilities",
    "비유동부채": "non_current_liabilities",
    "부채총계": "total_liabilities",

    "자본금": "capital_stock",
    "이익잉여금": "retained_earnings",
    "자본총계": "total_equity",

    # Key: Korean name from API, Value: Standardized English name
    "주당액면가액(원)": "par_value_per_share",
    "당기순이익(백만원)": "net_income",
    "주당순이익(원)": "eps",
    "현금배당금총액(백만원)": "total_cash_dividend",
    "주식배당금총액(백만원)": "total_stock_dividend",
    "현금배당성향(%)": "payout_ratio",
    "현금배당수익률(%)": "dividend_yield",
    "주식배당수익률(%)": "stock_dividend_yield",
    "주당 현금배당금(원)": "dps_cash",
    "주당 주식배당(주)": "dps_stock",
}

STOCK_KIND_MAP = {
    "보통주": "common",
    "우선주": "preferred",
}

def translate_to_english_key(korean_key: str) -> str:
    return _MAP_FOR_FINANCIAL_REPORT.get(korean_key, None)


def translate_financial_report(external_data: dict) -> dict:
    result = {}
    for k, v in external_data.items():
        eng_key = _MAP_FOR_FINANCIAL_REPORT.get(k)
        if eng_key:
            result[eng_key] = v
    return result

