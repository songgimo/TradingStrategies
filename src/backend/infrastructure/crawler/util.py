import json
from src.config.config import STATIC_FOLDER_PATH


def rss_urls():
    rss_urls_path = STATIC_FOLDER_PATH / "rss_url.json"

    with open(rss_urls_path, "r") as f:
        urls = json.loads(f.read())

    return urls


RSS_URLS = rss_urls()
