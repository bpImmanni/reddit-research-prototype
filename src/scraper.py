import requests
import pandas as pd
from datetime import datetime, timezone


def scrape_posts(query, subreddit="", max_posts=50, platform="Bluesky"):
    if platform == "Bluesky":
        return scrape_bluesky(query=query, max_posts=max_posts)
    return pd.DataFrame(columns=[
        "date", "subreddit", "title", "body", "score", "num_comments", "url"
    ])


def scrape_bluesky(query, max_posts=50):
    empty_df = pd.DataFrame(columns=[
        "date", "subreddit", "title", "body", "score", "num_comments", "url"
    ])

    if not query.strip():
        return empty_df

    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    params = {
        "q": query,
        "limit": min(max_posts, 100),
        "sort": "latest"
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return empty_df

    posts = payload.get("posts", [])
    rows = []

    for item in posts:
        record = item.get("record", {})
        author = item.get("author", {})
        created_at = record.get("createdAt")

        parsed_date = None
        if created_at:
            try:
                parsed_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(timezone.utc)
            except Exception:
                parsed_date = None

        text = record.get("text", "")

        rows.append({
            "date": parsed_date,
            "subreddit": author.get("handle", "bluesky"),
            "title": text[:80] if text else "",
            "body": text,
            "score": item.get("likeCount", 0),
            "num_comments": item.get("replyCount", 0),
            "url": f"https://bsky.app/profile/{author.get('handle', '')}/post/{item.get('uri', '').split('/')[-1]}" if author.get("handle") and item.get("uri") else ""
        })

    return pd.DataFrame(rows)