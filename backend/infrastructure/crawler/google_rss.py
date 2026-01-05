import requests
import json
import xml.etree.ElementTree as ET
import hashlib
from datetime import datetime
from backend.domain.entities import News
from config.config import STATIC_FOLDER_PATH

from backend.application.ports.output import NewsCrawlerOutputPort


class GoogleNews(NewsCrawlerOutputPort):
    def __init__(self):
        self._rss_urls = self.load_rss_urls()["GOOGLE"]

    def load_rss_urls(self):
        rss_urls_path = STATIC_FOLDER_PATH / "rss_url.json"

        with open(rss_urls_path, "r") as f:
            urls = json.loads(f.read())

        return urls

    def fetch_news(self):
        news_list = []
        for rss_url in self._rss_urls.values():
            resp = requests.get(rss_url)
            root = ET.fromstring(resp.content)
            for item in root.findall('./channel/item'):
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

        return news_list


if __name__ == '__main__':
    crawler = GoogleNews()
    crawler.fetch_news()