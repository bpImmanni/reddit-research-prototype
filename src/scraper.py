import requests
import pandas as pd
from datetime import datetime


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RedditResearchPrototype/1.0"
}


def scrape_reddit(query, subreddit="", max_posts=50):
    """
    Scrape live Reddit search results using Reddit's public JSON endpoint.
    No Reddit app setup required for this prototype.
    """
    if not query.strip():
        return pd.DataFrame(columns=[
            "date", "subreddit", "title", "body", "score", "num_comments", "url"
        ])

    if subreddit.strip():
        full_query = f"{query} subreddit:{subreddit}"
    else:
        full_query = query

    url = "https://www.reddit.com/search.json"
    params = {
        "q": full_query,
        "limit": max_posts,
        "sort": "new",
        "type": "link"
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return pd.DataFrame(columns=[
            "date", "subreddit", "title", "body", "score", "num_comments", "url"
        ])

    children = payload.get("data", {}).get("children", [])
    rows = []

    for item in children:
        post = item.get("data", {})
        created_utc = post.get("created_utc")

        rows.append({
            "date": datetime.fromtimestamp(created_utc) if created_utc else None,
            "subreddit": post.get("subreddit", ""),
            "title": post.get("title", ""),
            "body": post.get("selftext", ""),
            "score": post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "url": f"https://www.reddit.com{post.get('permalink', '')}" if post.get("permalink") else ""
        })

    df = pd.DataFrame(rows)
    return df