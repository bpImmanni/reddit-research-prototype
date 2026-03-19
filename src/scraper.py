import requests
import pandas as pd
from datetime import datetime, timezone


def scrape_posts(query, subreddit="", max_posts=50, platform="Bluesky"):
    if platform == "Bluesky":
        return scrape_bluesky(query=query, max_posts=max_posts)

    empty_df = pd.DataFrame(columns=[
        "date", "subreddit", "title", "body", "score", "num_comments", "url"
    ])
    return empty_df, "Unsupported platform selected."


def scrape_bluesky(query, max_posts=50):
    empty_df = pd.DataFrame(columns=[
        "date", "subreddit", "title", "body", "score", "num_comments", "url"
    ])

    if not query.strip():
        return empty_df, "Query is empty."

    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    params = {
        "q": query,
        "limit": min(max_posts, 100),
        "sort": "latest"
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code != 200:
            return empty_df, f"Bluesky request failed with status code {response.status_code}."

        payload = response.json()
        posts = payload.get("posts", [])

        if not posts:
            return empty_df, "Bluesky returned 0 matching posts for this query."

    except Exception as e:
        return empty_df, f"Request error: {str(e)}"

    rows = []

    for item in posts:
        record = item.get("record", {})
        author = item.get("author", {})
        created_at = record.get("createdAt")

        parsed_date = None
        if created_at:
            try:
                parsed_date = datetime.fromisoformat(
                    created_at.replace("Z", "+00:00")
                ).astimezone(timezone.utc)
            except Exception:
                parsed_date = None

        text = record.get("text", "")

        post_uri = item.get("uri", "")
        post_id = post_uri.split("/")[-1] if post_uri else ""
        handle = author.get("handle", "")

        rows.append({
            "date": parsed_date,
            "subreddit": handle if handle else "bluesky",
            "title": text[:80] if text else "",
            "body": text,
            "score": item.get("likeCount", 0),
            "num_comments": item.get("replyCount", 0),
            "url": f"https://bsky.app/profile/{handle}/post/{post_id}" if handle and post_id else ""
        })

    df = pd.DataFrame(rows)
    return df, None