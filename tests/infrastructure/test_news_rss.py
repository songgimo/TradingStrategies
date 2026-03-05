import pytest
import hashlib
from datetime import datetime
from unittest.mock import MagicMock, patch
from src.backend.infrastructure.crawler.mk_rss import MKNews, HKNews
from src.backend.domain.entities import News
from src.backend.domain.reference_data import NewsSourceType

# 1. 목데이터(Mock Data) 준비
MOCK_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss>
    <channel>
        <item>
            <title>테스트 뉴스 제목</title>
            <link>http://test-news.com/123</link>
            <pubDate>Tue, 03 Feb 2026 10:00:00 +0900</pubDate>
            <description>뉴스 요약 내용</description>
        </item>
    </channel>
</rss>
"""

MOCK_ARTICLE_HTML = """
<html>
    <body>
        <div class="news_cnt_detail_wrap">실제 본문 내용입니다.</div>
        <div class="article-body">한경 본문 내용입니다.</div>
    </body>
</html>
"""


@pytest.fixture
def mk_crawler():
    return MKNews()


@pytest.fixture
def hk_crawler():
    return HKNews()


class TestRSSCrawler:
    @patch("requests.get")
    def test_crawl_article_success(self, mock_get, mk_crawler):
        """본문 크롤링 성공 테스트"""
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = MOCK_ARTICLE_HTML
        mock_get.return_value = mock_response

        # When
        content = mk_crawler._crawl_article("http://test.com")

        # Then
        assert content == "실제 본문 내용입니다."
        mock_get.assert_called_once_with("http://test.com", timeout=5)

    @patch("requests.get")
    def test_fetch_single_rss_filtering_by_date(self, mock_get, mk_crawler):
        """날짜 필터링이 정상적으로 작동하는지 테스트 (오늘 뉴스만 수집)"""
        # Given
        # 1. RSS XML 응답 설정
        mock_rss_res = MagicMock()
        mock_rss_res.status_code = 200
        mock_rss_res.content = MOCK_RSS_XML.encode("utf-8")

        # 2. 본문 HTML 응답 설정
        mock_content_res = MagicMock()
        mock_content_res.status_code = 200
        mock_content_res.text = MOCK_ARTICLE_HTML

        # requests.get 호출 순서에 따른 반환값 설정
        mock_get.side_effect = [mock_rss_res, mock_content_res]

        # 테스트 시점의 날짜를 RSS 데이터와 맞춤 (2026-02-03)
        with patch("src.backend.infrastructure.crawler.mk_rss.datetime") as mock_datetime:
            mock_datetime.now.return_value.date.return_value = datetime(2026, 2, 3).date()

            # When
            news_list = mk_crawler._fetch_single_rss("http://rss-url.com")

            # Then
            assert len(news_list) == 1
            assert isinstance(news_list[0], News)
            assert news_list[0].title == "테스트 뉴스 제목"
            assert news_list[0].source == str(NewsSourceType.MK_STOCK)
            assert news_list[0].id == hashlib.md5("http://test-news.com/123".encode()).hexdigest()

    @patch("src.backend.infrastructure.crawler.mk_rss.MKNews._fetch_single_rss")
    def test_fetch_news_calls_all_urls(self, mock_fetch_single, mk_crawler):
        """정의된 모든 RSS URL에 대해 수집을 시도하는지 테스트"""
        # Given
        mock_fetch_single.return_value = [MagicMock(spec=News)]
        num_urls = len(mk_crawler._rss_urls)

        # When
        result = mk_crawler.fetch_news()

        # Then
        assert mock_fetch_single.call_count == num_urls
        assert len(result) == num_urls

    def test_crawler_inheritance_settings(self, mk_crawler, hk_crawler):
        """자식 클래스들이 올바른 설정값(class_name)을 가지고 있는지 테스트"""
        assert mk_crawler.content_class == "news_cnt_detail_wrap"
        assert mk_crawler.source_type == NewsSourceType.MK_STOCK

        assert hk_crawler.content_class == "article-body"
        assert hk_crawler.source_type == NewsSourceType.HK_FINANCE