import logging
import requests
import xml.etree.ElementTree as ET
import hashlib
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Optional
from bs4 import BeautifulSoup

from src.backend.domain.entities import News
from src.backend.infrastructure.crawler.util import RSS_URLS
from src.backend.application.ports.output import NewsCrawlerOutputPort
from src.backend.domain.reference_data import NewsSourceType

logger = logging.getLogger(__name__)


class BaseRSSCrawler(NewsCrawlerOutputPort):
    def __init__(self, source_type: NewsSourceType, content_class: str):
        self.source_type = source_type
        self.content_class = content_class
        self._rss_urls = RSS_URLS[str(source_type)]

    def fetch_news(self) -> List[News]:
        all_news = []
        for url in self._rss_urls.values():
            try:
                batch = self._fetch_single_rss(url)
                all_news.extend(batch)
            except Exception as e:
                logger.error(f"Error fetching RSS from {url}: {e}")
        return all_news

    def _crawl_article(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            element = soup.find("div", class_=self.content_class)
            return element.text.strip() if element else None
        except Exception as e:
            logger.warning(f"Failed to crawl content from {url}: {e}")
            return None

    def _fetch_single_rss(self, url: str) -> List[News]:
        news_list = []
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return []

            root = ET.fromstring(response.content)
            for item in root.findall('./channel/item'):
                try:
                    pub_date = parsedate_to_datetime(item.find('pubDate').text)
                    if datetime.now().date() != pub_date.date():
                        continue

                    link = item.find('link').text
                    news = News(
                        id=hashlib.md5(link.encode()).hexdigest(),
                        title=item.find('title').text,
                        content=self._crawl_article(link),
                        published_at=pub_date,
                        source=str(self.source_type),
                        url=link
                    )
                    news_list.append(news)
                except Exception as parse_e:
                    logger.error(f"Error parsing item in {url}: {parse_e}")
        except Exception as e:
            logger.error(f"Error fetching RSS {url}: {e}")
        return news_list


class MKNews(BaseRSSCrawler):
    def __init__(self):
        super().__init__(NewsSourceType.MK_STOCK, "news_cnt_detail_wrap")


class HKNews(BaseRSSCrawler):
    def __init__(self):
        super().__init__(NewsSourceType.HK_FINANCE, "article-body")