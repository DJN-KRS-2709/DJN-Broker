import os, time
from typing import List, Dict
import requests
import feedparser
from dotenv import load_dotenv

load_dotenv()

def fetch_news_newsapi(query: str, languages: List[str]) -> List[Dict]:
    key = os.getenv("NEWSAPI_KEY")
    if not key:
        return []
    out = []
    for lang in languages:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": lang,
            "sortBy": "publishedAt",
            "pageSize": 25,
            "apiKey": key
        }
        r = requests.get(url, params=params, timeout=20)
        if r.status_code == 200:
            js = r.json()
            for a in js.get("articles", []):
                out.append({
                    "source": a.get("source", {}).get("name"),
                    "title": a.get("title"),
                    "url": a.get("url"),
                    "publishedAt": a.get("publishedAt"),
                    "content": a.get("description") or a.get("content") or "",
                })
        time.sleep(1)
    return out

def fetch_news_rss(feeds: List[str]) -> List[Dict]:
    out = []
    for feed in feeds:
        try:
            parsed = feedparser.parse(feed)
            for e in parsed.entries:
                out.append({
                    "source": parsed.feed.get("title", "rss"),
                    "title": e.get("title"),
                    "url": e.get("link"),
                    "publishedAt": e.get("published"),
                    "content": e.get("summary", ""),
                })
        except Exception:
            continue
    return out
