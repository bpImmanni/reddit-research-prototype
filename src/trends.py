import pandas as pd
import numpy as np


def detect_trends(df):
    if df.empty:
        return {
            "daily_counts": pd.DataFrame(),
            "topic_by_day": pd.DataFrame(),
            "concern_by_day": pd.DataFrame(),
            "top_keywords": [],
            "top_subreddits": pd.DataFrame(),
            "spike_alert": None,
        }

    work = df.copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce")
    work = work.dropna(subset=["date"]).copy()
    work["day"] = work["date"].dt.date

    daily_counts = work.groupby("day").size().reset_index(name="post_count")
    daily_counts["rolling_avg_3"] = daily_counts["post_count"].rolling(3, min_periods=1).mean()

    mean_count = daily_counts["post_count"].mean()
    std_count = daily_counts["post_count"].std()

    if std_count and std_count > 0:
        daily_counts["z_score"] = (daily_counts["post_count"] - mean_count) / std_count
    else:
        daily_counts["z_score"] = 0

    spikes = daily_counts[daily_counts["z_score"] > 1.0]

    topic_by_day = work.groupby(["day", "topic"]).size().reset_index(name="count")
    concern_by_day = work.groupby(["day", "concern"]).size().reset_index(name="count")

    top_subreddits = work["subreddit"].value_counts().reset_index()
    top_subreddits.columns = ["subreddit", "count"]

    all_words = " ".join(work["clean_text"].fillna("").tolist()).split()
    if all_words:
        top_keywords = list(pd.Series(all_words).value_counts().head(10).index)
    else:
        top_keywords = []

    spike_alert = None
    if not spikes.empty:
        spike_day = spikes.iloc[0]["day"]
        subset = work[work["day"] == spike_day]
        top_topic = subset["topic"].mode().iloc[0] if not subset.empty else "unknown"

        spike_alert = {
            "date": str(spike_day),
            "spike_size": int(spikes.iloc[0]["post_count"]),
            "probable_topic_driver": top_topic,
        }

    return {
        "daily_counts": daily_counts,
        "topic_by_day": topic_by_day,
        "concern_by_day": concern_by_day,
        "top_keywords": top_keywords,
        "top_subreddits": top_subreddits,
        "spike_alert": spike_alert,
    }