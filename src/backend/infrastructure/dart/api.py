import json
import re
import requests
import io
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class OpenDartAPI:
    def __init__(self, openapi_key=None):
        self._openapi_key = openapi_key
        self._base_url = "https://opendart.fss.or.kr/api"

        with open("./corp_codes.json", "r", encoding="utf-8") as f:
            self._corp_code_dict = json.loads(f.read())

    def get_corp_info_by_stock_code(self, stock_code):
        return self._corp_code_dict[stock_code]

    def report_list(self, corp_code, begin_date):
        params = {
            "crtfc_key": self._openapi_key,
            "corp_code": corp_code,
            "bgn_de": begin_date,
            "last_reprt_at": "Y",  # 최종보고서 검색 여부 Y / N
            "pblntf_ty": "A",  # A: 정기공시
            "corp_cls": "Y",  # Y(유가), K(코스닥), N(코넥스), E(기타)
            "page_count": 100,
        }

        report_list = requests.get(self._base_url + "/list.json", params=params).json()
        latest_report = report_list["list"][0]
        report_nm = latest_report["report_nm"]

        match = re.search(r"(\d{4})\.(\d{2})", report_nm)
        if match:
            bsns_year = match.group(1)  # '2025'
            month = int(match.group(2))  # 3

            # 보고서 종류와 월에 따라 reprt_code 결정
            if "사업보고서" in report_nm:
                reprt_code = "11011"
            elif "반기보고서" in report_nm:
                reprt_code = "11012"
            elif "분기보고서" in report_nm:
                if month == 3:  # 1분기
                    reprt_code = "11013"
                elif month == 9:  # 3분기
                    reprt_code = "11014"
        return bsns_year, reprt_code

    def get_financial(self, base_year, report_code, corp_code) -> list:
        finance_rpt_code = {
            "crtfc_key": self._openapi_key,
            "corp_code": corp_code,
            "bsns_year": base_year,
            "reprt_code": report_code,
            # "fs_div": "CFS",
        }
        try:
            finance_rpt = requests.get(
                self._base_url + "/fnlttSinglAcnt.json", params=finance_rpt_code
            )

            finance_rpt.raise_for_status()
            data = finance_rpt.json()

            if data.get('status') == '000':
                return data.get('list', [])
            else:
                print(f"DART API 오류: {data.get('message')}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"failed to get financial data for {report_code}: {e}")
            return []

    def processing_financial_data(self, stock_code: str, financial_data_list: list):
        cfs, ofs = dict(), dict()

        meta_info = {
            "rcept_no": financial_data_list[0]["rcept_no"],
            "corp_code": financial_data_list[0]["corp_code"],
            "bsns_year": financial_data_list[0]["bsns_year"],
            "reprt_code": financial_data_list[0]["reprt_code"],
            "stock_code": stock_code,
        }
        for each in financial_data_list:
            if each["account_nm"] not in ACCOUNT_NM_MAP.keys():
                continue
            key = ACCOUNT_NM_MAP[each["account_nm"]]

            amount_to_use_str = each.get('thstrm_amount') \
                if each.get("reprt_code") == "11011" else each.get('thstrm_add_amount', each['thstrm_amount'])
            try:
                amount_to_use = int(amount_to_use_str.replace(',', ''))
            except (ValueError, TypeError):
                amount_to_use = None

            if each["fs_div"] == "CFS":
                cfs[key] = amount_to_use
            elif each["fs_div"] == "OFS":
                ofs[key] = amount_to_use
        result = {
            "metadata": meta_info,
            "cfs": cfs,
            "ofs": ofs,
        }
        return result

    def get_dividend(self, base_year, report_code, corp_code):
        finance_rpt_code = {
            "crtfc_key": self._openapi_key,
            "corp_code": corp_code,
            "bsns_year": base_year,
            "reprt_code": report_code,
        }
        try:
            raw = requests.get(self._base_url + "/alotMatter.json", params=finance_rpt_code)
            raw.raise_for_status()
            data = raw.json()
            if data.get('status') == '000':
                return data.get('list', [])
            else:
                print(f"DART API 오류: {data.get('message')}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            return []

    def processing_dividend_data(self, stock_code: str, dividend_data_list: list):
        if not dividend_data_list:
            return {
                "metadata": {"stock_code": stock_code},
                "cfs": {},
                "ofs": {},
            }

        def _clean_value(value_str: str):
            """Helper to clean and convert numeric string values."""
            if not isinstance(value_str, str) or value_str == '-':
                return None
            try:
                # Remove commas and convert to float to handle decimals
                return float(value_str.replace(',', ''))
            except (ValueError, TypeError):
                return None
        first_item = dividend_data_list[0]
        meta_info = {
            "rcept_no": first_item.get("rcept_no"),
            "corp_code": first_item.get("corp_code"),
            "corp_name": first_item.get("corp_name"),
            "stlm_dt": first_item.get("stlm_dt"),
            "stock_code": stock_code,
            "stock_kind": "common"
        }

        cfs, ofs = {}, {}
        for item in dividend_data_list:
            stock_kind_raw = item.get("stock_knd")
            if stock_kind_raw == "우선주":
                continue  # Immediately skip to the next item in the list

            se = item.get("se", "")
            # Step 1: Determine financial statement type (CFS/OFS) and get the clean metric name
            target_dict = ofs  # Default to separate (OFS)
            clean_se = se
            if se.startswith("(연결)"):
                target_dict = cfs
                clean_se = se.replace("(연결)", "").strip()
            elif se.startswith("(별도)"):
                target_dict = ofs
                clean_se = se.replace("(별도)", "").strip()

            # Step 2 (Prioritized): Check if the metric is one we want to process.
            # This acts as a guard clause to exit early for irrelevant data.
            if clean_se not in DIVIDEND_KEY_MAP:
                continue

            # Step 3: If relevant, proceed with processing
            key = DIVIDEND_KEY_MAP[clean_se]
            value = _clean_value(item.get("thstrm"))

            # Handle data distinguished by stock kind (common vs. preferred)
            target_dict[key] = value

        result = {
            "metadata": meta_info,
            "cfs": cfs,
            "ofs": ofs,
        }
        return result
