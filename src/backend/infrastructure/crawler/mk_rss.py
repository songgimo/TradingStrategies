import logging
import aiohttp
import asyncio
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

    async def fetch_news(self) -> List[News]:
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_single_rss(session, url)
                for url in self._rss_urls.values()
            ]
            results = await asyncio.gather(*tasks)

        all_news = [news for batch in results for news in batch]
        return all_news

    async def _crawl_article(self, session, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://news.google.com/"
        }
        try:
            async with session.get(url, headers=headers, timeout=5) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                data = soup.find("div", class_="news_cnt_detail_wrap").text
                return data if data else None
        except Exception as e:
            logger.warning(f"Failed to crawl content from {url}: {e}")
            return None

    async def _fetch_single_rss(self, session, url) -> List[News]:
        news_list = []
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Failed to fetch {url}: {response.status}")
                    return []

                content = await response.text()

                root = ET.fromstring(content)
                for item in root.findall('./channel/item'):
                    try:
                        pub_date_str = item.find('pubDate').text
                        pub_date = parsedate_to_datetime(pub_date_str)
                        if not datetime.now().date() == pub_date.date():
                            # crawling only today's news
                            return news_list

                        title = item.find('title').text
                        link = item.find('link').text

                        crawled_content = await self._crawl_article(session, link)
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
                        print(f"Error parsing item in {url}: {parse_e}")
                        continue

        except Exception as e:
            print(f"Error fetching RSS {url}: {e}")

        return news_list


class HKNews(NewsCrawlerOutputPort):
    def __init__(self):
        self._rss_urls = RSS_URLS[str(NewsSourceType.HK_FINANCE)]

    async def fetch_news(self) -> List[News]:
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_single_rss(session, url)
                for url in self._rss_urls.values()
            ]
            results = await asyncio.gather(*tasks)

        all_news = [news for batch in results for news in batch]
        return all_news

    async def _crawl_article(self, session, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://news.google.com/"
        }
        try:
            async with session.get(url, headers=headers, timeout=5) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                data = soup.find("div", class_="article-body").text
                return data if data else None
        except Exception as e:
            logger.warning(f"Failed to crawl content from {url}: {e}")
            return None

    async def _fetch_single_rss(self, session, url) -> List[News]:
        news_list = []
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Failed to fetch {url}: {response.status}")
                    return []

                content = await response.text()

                root = ET.fromstring(content)
                for item in root.findall('./channel/item'):
                    try:
                        pub_date_str = item.find('pubDate').text
                        pub_date = parsedate_to_datetime(pub_date_str)
                        if not datetime.now().date() == pub_date.date():
                            return news_list

                        title, link = item.find('title').text, item.find('link').text

                        crawled_content = await self._crawl_article(session, link)
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
                        print(f"Error parsing item in {url}: {parse_e}")
                        continue

        except Exception as e:
            print(f"Error fetching RSS {url}: {e}")

        return news_list


if __name__ == '__main__':
    asyncio.run(HKNews().fetch_news())