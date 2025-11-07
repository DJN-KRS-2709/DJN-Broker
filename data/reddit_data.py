from typing import List, Dict
from dotenv import load_dotenv
import os
import praw
import time

load_dotenv()

def _client():
    cid = os.getenv("REDDIT_CLIENT_ID")
    secret = os.getenv("REDDIT_CLIENT_SECRET")
    ua = os.getenv("REDDIT_USER_AGENT", "free-mvp/0.1 by dejank")
    if not cid or not secret:
        return None
    return praw.Reddit(
        client_id=cid,
        client_secret=secret,
        user_agent=ua,
        check_for_async=False
    )

def fetch_submissions(subreddits: List[str], limit_per_sub: int = 25) -> List[Dict]:
    cli = _client()
    if cli is None:
        return []
    out = []
    for sub in subreddits:
        try:
            for s in cli.subreddit(sub).hot(limit=limit_per_sub):
                out.append({
                    "subreddit": sub,
                    "title": s.title,
                    "url": f"https://www.reddit.com{s.permalink}",
                    "created_utc": s.created_utc,
                    "content": (s.selftext or "")[:1000],
                })
            time.sleep(1)
        except Exception:
            continue
    return out
