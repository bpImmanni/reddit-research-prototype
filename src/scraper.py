import requests
import pandas as pd
from datetime import datetime


HEADERS = {
    "User-Agent": "desktop:reddit_research_prototype:v1.0 (by /u/researchprototypebot)"
}


def scrape_reddit(query, subreddit="", max_posts=50):
    """
    Scrape Reddit search results using the public JSON endpoint.
    Returns: (dataframe, error_message)
    """
    empty_df = pd.DataFrame(columns=[
        "date", "subreddit", "title", "body", "score", "num_comments", "url"
    ])

    if not query.strip():
        return empty_df, "Query is empty."

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
        status_code = response.status_code

        if status_code != 200:
            return empty_df, f"Reddit request failed with status code {status_code}."

        payload = response.json()
        children = payload.get("data", {}).get("children", [])

        if not children:
            return empty_df, "Reddit returned 0 matching posts for this query."

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
        return df, None

    except Exception as e:
        return empty_df, f"Request error: {str(e)}"