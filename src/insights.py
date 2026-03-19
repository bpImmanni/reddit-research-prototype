def generate_insights(df, trend_results):
    if df.empty:
        return {
            "executive_summary": "No posts were available for the selected query and date range.",
            "top_themes": [],
            "source_shifts": "No source concentration detected.",
            "response_focus": "Collect more data before drawing conclusions.",
            "representative_examples": []
        }

    total_posts = len(df)
    top_topic = df["topic"].mode().iloc[0] if "topic" in df.columns else "unknown"
    top_sentiment = df["sentiment"].mode().iloc[0] if "sentiment" in df.columns else "unknown"
    top_subreddit = df["subreddit"].mode().iloc[0] if "subreddit" in df.columns else "unknown"
    high_concern_count = int((df["concern"] == "high").sum()) if "concern" in df.columns else 0

    top_themes = df["topic"].value_counts().head(3).index.tolist() if "topic" in df.columns else []

    executive_summary = (
        f"Over the selected period, the tool analyzed {total_posts} Reddit posts. "
        f"The most common topic was '{top_topic}', and the prevailing tone was '{top_sentiment}'. "
        f"High-concern content accounted for {high_concern_count} posts, with activity most concentrated in {top_subreddit}."
    )

    source_shifts = (
        f"Discussion appears to be concentrated rather than broadly distributed, with {top_subreddit} "
        f"emerging as the primary source of visible activity in the selected dataset."
    )

    response_focus = (
        "Monitor high-concern posts, especially where misinformation, political rhetoric, or harassment themes "
        "cluster within a small number of subreddits."
    )

    representative_examples = []
    if "summary" in df.columns:
        representative_examples = df["summary"].head(3).tolist()

    return {
        "executive_summary": executive_summary,
        "top_themes": top_themes,
        "source_shifts": source_shifts,
        "response_focus": response_focus,
        "representative_examples": representative_examples
    }