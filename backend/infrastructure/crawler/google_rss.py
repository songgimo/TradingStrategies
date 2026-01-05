import aiohttp
import asyncio
import json
import xml.etree.ElementTree as ET
import hashlib
from datetime import datetime
from backend.domain.entities import News
from config.config import STATIC_FOLDER_PATH
from typing import List

from backend.application.ports.output import NewsCrawlerOutputPort


class GoogleNews(NewsCrawlerOutputPort):
    def __init__(self):
        self._rss_urls = self.load_rss_urls()["GOOGLE"]

    def load_rss_urls(self):
        rss_urls_path = STATIC_FOLDER_PATH / "rss_url.json"

        with open(rss_urls_path, "r") as f:
            urls = json.loads(f.read())

        return urls

    async def fetch_news(self) -> List[News]:
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_single_rss(session, url)
                for url in self._rss_urls.values()
            ]
            results = await asyncio.gather(*tasks)

        all_news = [news for batch in results for news in batch]
        return all_news

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
                        title = item.find('title').text
                        link = item.find('link').text
                        pub_date_str = item.find('pubDate').text

                        pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")

                        news_id = hashlib.md5(link.encode()).hexdigest()

                        news = News(
                            id=news_id,
                            title=title,
                            content=title,
                            published_at=pub_date,
                            source="GoogleNews",
                            url=link
                        )
                        news_list.append(news)
                    except Exception as parse_e:
                        print(f"Error parsing item in {url}: {parse_e}")
                        continue

        except Exception as e:
            print(f"Error fetching RSS {url}: {e}")

        return news_list
