import logging
import requests
import xml.etree.ElementTree as ET
import hashlib
from datetime import datetime
from src.backend.domain.entities import News
from src.backend.infrastructure.crawler.util import RSS_URLS
from email.utils import parsedate_to_datetime
from typing import List
from bs4 import BeautifulSoup

from src.backend.application.ports.output import NewsCrawlerOutputPort
from src.backend.domain.reference_data import NewsSourceType

logger = logging.getLogger(__name__)


class MKNews(NewsCrawlerOutputPort):
    def __init__(self):
        self._rss_urls = RSS_URLS[str(NewsSourceType.MK_STOCK)]

    def fetch_news(self) -> List[News]:
        all_news = []
        for url in self._rss_urls.values():
            try:
                batch = self._fetch_single_rss(url)
                all_news.extend(batch)
            except Exception as e:
                logger.error(f"Error fetching RSS from {url}: {e}")
        return all_news

    def _crawl_article(self, url):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            element = soup.find("div", class_="news_cnt_detail_wrap")
            return element.text.strip() if element else None
        except Exception as e:
            logger.warning(f"Failed to crawl content from {url}: {e}")
            return None

    def _fetch_single_rss(self, url) -> List[News]:
        news_list = []
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to fetch {url}: {response.status_code}")
                return []

            root = ET.fromstring(response.content)
            for item in root.findall('./channel/item'):
                try:
                    pub_date_str = item.find('pubDate').text
                    pub_date = parsedate_to_datetime(pub_date_str)

                    if datetime.now().date() != pub_date.date():
                        continue

                    title = item.find('title').text
                    link = item.find('link').text

                    crawled_content = self._crawl_article(link)

                    news_id = hashlib.md5(link.encode()).hexdigest()
                    news = News(
                        id=news_id,
                        title=title,
                        content=crawled_content,
                        published_at=pub_date,
                        source="MKNews",
                        url=link
                    )
                    news_list.append(news)
                except Exception as parse_e:
                    logger.error(f"Error parsing item in {url}: {parse_e}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching RSS {url}: {e}")

        return news_list


class HKNews(NewsCrawlerOutputPort):
    def __init__(self):
        self._rss_urls = RSS_URLS[str(NewsSourceType.HK_FINANCE)]

    def fetch_news(self) -> List[News]:
        all_news = []
        for url in self._rss_urls.values():
            batch = self._fetch_single_rss(url)
            all_news.extend(batch)
        return all_news

    def _crawl_article(self, url):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            # 한경 본문 영역 클래스: article-body
            element = soup.find("div", class_="article-body")
            return element.text.strip() if element else None
        except Exception as e:
            logger.warning(f"Failed to crawl content from {url}: {e}")
            return None

    def _fetch_single_rss(self, url) -> List[News]:
        news_list = []
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return []

            root = ET.fromstring(response.content)
            for item in root.findall('./channel/item'):
                try:
                    pub_date_str = item.find('pubDate').text
                    pub_date = parsedate_to_datetime(pub_date_str)

                    if datetime.now().date() != pub_date.date():
                        continue

                    title = item.find('title').text
                    link = item.find('link').text

                    crawled_content = self._crawl_article(link)
                    news_id = hashlib.md5(link.encode()).hexdigest()
                    news = News(
                        id=news_id,
                        title=title,
                        content=crawled_content,
                        published_at=pub_date,
                        source=str(NewsSourceType.HK_FINANCE),
                        url=link
                    )
                    news_list.append(news)
                except Exception as parse_e:
                    logger.error(f"Error parsing item in {url}: {parse_e}")
                    continue
        except Exception as e:
            logger.error(f"Error fetching RSS {url}: {e}")

        return news_list
