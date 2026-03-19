import os
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st

from src.scraper import scrape_reddit
from src.preprocess import preprocess_dataframe
from src.classify import run_classification
from src.trends import detect_trends
from src.insights import generate_insights
from src.report_builder import build_pdf_report
from src.utils import truncate_text


st.set_page_config(
    page_title="AI Research Analyst Prototype",
    page_icon="📊",
    layout="wide"
)

if os.path.exists("assets/style.css"):
    with open("assets/style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session state
if "raw_df" not in st.session_state:
    st.session_state.raw_df = pd.DataFrame()

if "processed_df" not in st.session_state:
    st.session_state.processed_df = pd.DataFrame()

if "classified_df" not in st.session_state:
    st.session_state.classified_df = pd.DataFrame()

if "preprocess_stats" not in st.session_state:
    st.session_state.preprocess_stats = {}

if "keywords" not in st.session_state:
    st.session_state.keywords = []

if "entities" not in st.session_state:
    st.session_state.entities = []

if "trend_results" not in st.session_state:
    st.session_state.trend_results = {}

if "insights" not in st.session_state:
    st.session_state.insights = {}

st.title("AI-Assisted Research Prototype")
st.caption("Internal analyst tool for scraping, preprocessing, classification, trend detection, insight generation, and report building.")

with st.sidebar:
    st.header("Workflow Controls")

    st.subheader("1. Data Input")
    start_date = st.date_input("Start date", value=date.today().replace(day=max(1, date.today().day - 7)))
    end_date = st.date_input("End date", value=date.today())
    platform = st.selectbox("Platform", ["Reddit"])
    subreddit = st.text_input("Subreddit (optional)", value="")
    query = st.text_input("Keyword / search query", value="antisemitism")
    max_posts = st.selectbox("Max posts", [25, 50, 100, 200], index=1)

    if st.button("Scrape Data", use_container_width=True):
        with st.spinner("Scraping live Reddit data..."):
            df = scrape_reddit(query=query, subreddit=subreddit, max_posts=max_posts)

            if not df.empty:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df = df.dropna(subset=["date"]).copy()
                df = df[
                    (df["date"].dt.date >= start_date) &
                    (df["date"].dt.date <= end_date)
                ].copy()

            st.session_state.raw_df = df
            st.session_state.processed_df = pd.DataFrame()
            st.session_state.classified_df = pd.DataFrame()
            st.session_state.preprocess_stats = {}
            st.session_state.keywords = []
            st.session_state.entities = []
            st.session_state.trend_results = {}
            st.session_state.insights = {}

        st.success(f"Loaded {len(df)} posts.")

    st.subheader("2. Pipeline Actions")

    if st.button("Preprocess", use_container_width=True):
        with st.spinner("Cleaning and structuring text..."):
            processed_df, stats, keywords, entities = preprocess_dataframe(st.session_state.raw_df)
            st.session_state.processed_df = processed_df
            st.session_state.preprocess_stats = stats
            st.session_state.keywords = keywords
            st.session_state.entities = entities
        st.success("Preprocessing complete.")

    if st.button("Run Classification", use_container_width=True):
        with st.spinner("Classifying posts..."):
            classified_df = run_classification(st.session_state.processed_df, query=query)
            st.session_state.classified_df = classified_df
        st.success("Classification complete.")

    if st.button("Detect Trends", use_container_width=True):
        with st.spinner("Detecting trends and spikes..."):
            st.session_state.trend_results = detect_trends(st.session_state.classified_df)
        st.success("Trend detection complete.")

    if st.button("Generate Insights", use_container_width=True):
        with st.spinner("Generating analyst-style insights..."):
            st.session_state.insights = generate_insights(
                st.session_state.classified_df,
                st.session_state.trend_results
            )
        st.success("Insights generated.")

    st.subheader("3. Filters")
    topic_filter = st.selectbox(
    "Topic filter",
    [
        "All",
        "antisemitic rhetoric",
        "conspiracy narratives",
        "identity-based hostility",
        "political amplification",
        "harassment / abuse",
        "threats / incitement",
        "misinformation / false claims",
        "community response / support",
        "news / event discussion",
        "unrelated / low signal",
    ]
)
    concern_filter = st.selectbox("Concern level filter", ["All", "low", "medium", "high"])
    sentiment_filter = st.selectbox("Sentiment filter", ["All", "hostile", "neutral", "supportive"])


def apply_filters(df):
    if df.empty:
        return df

    work = df.copy()

    if topic_filter != "All" and "topic" in work.columns:
        work = work[work["topic"] == topic_filter]

    if concern_filter != "All" and "concern" in work.columns:
        work = work[work["concern"] == concern_filter]

    if sentiment_filter != "All" and "sentiment" in work.columns:
        work = work[work["sentiment"] == sentiment_filter]

    return work


tabs = st.tabs([
    "Scrape Data",
    "Preprocess",
    "Classification Engine",
    "Trend Detection Engine",
    "Insight Generator",
    "Report Builder"
])

with tabs[0]:
    st.subheader("Scraped Data")
    df = st.session_state.raw_df

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total posts scraped", len(df))

    if not df.empty and "date" in df.columns:
        c2.metric("Date range covered", f"{df['date'].min().date()} to {df['date'].max().date()}")
    else:
        c2.metric("Date range covered", "N/A")

    c3.metric("Unique subreddits", df["subreddit"].nunique() if not df.empty and "subreddit" in df.columns else 0)
    c4.metric("Avg post length", int(df["body"].fillna("").astype(str).str.len().mean()) if not df.empty else 0)

    if not df.empty:
        display_df = df.copy()
        display_df["body_preview"] = display_df["body"].apply(lambda x: truncate_text(x, 120))
        st.dataframe(
            display_df[["date", "subreddit", "title", "body_preview", "score", "num_comments", "url"]],
            use_container_width=True
        )

        st.markdown("### Raw Sample Preview")
        sample = df.iloc[0]
        st.write(f"**Title:** {sample['title']}")
        st.write(f"**Body:** {sample['body'] if sample['body'] else 'No body text'}")
    else:
        st.info("No data loaded yet. Use the sidebar and click Scrape Data.")

with tabs[1]:
    st.subheader("Preprocess")
    df = st.session_state.processed_df
    stats = st.session_state.preprocess_stats

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Duplicates removed", stats.get("duplicates_removed", 0))
    c2.metric("Null rows removed", stats.get("null_rows_removed", 0))
    c3.metric("Rows retained", stats.get("rows_retained", 0))
    c4.metric("Language detected", stats.get("language_detected", "N/A"))

    if not df.empty:
        st.markdown("### Before vs After")
        st.write("**Original Text**")
        st.write(df.iloc[0]["full_text"])
        st.write("**Cleaned Text**")
        st.write(df.iloc[0]["clean_text"])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Extracted Keywords")
            st.dataframe(pd.DataFrame({"keyword": st.session_state.keywords}), use_container_width=True)

        with col2:
            st.markdown("### Named Entities Panel")
            st.dataframe(pd.DataFrame({"entity": st.session_state.entities}), use_container_width=True)

        st.markdown("### Cleaned Dataset Preview")
        st.dataframe(
            df[["date", "subreddit", "full_text", "clean_text", "language", "text_length"]],
            use_container_width=True
        )
    else:
        st.info("Run Preprocess after scraping data.")

with tabs[2]:
    st.subheader("Classification Engine")
    df = apply_filters(st.session_state.classified_df)

    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows classified", len(df))
        c2.metric("Top topic", df["topic"].mode().iloc[0])
        c3.metric("Top concern", df["concern"].mode().iloc[0])

        topic_counts = df["topic"].value_counts().reset_index()
        topic_counts.columns = ["topic", "count"]

        sentiment_counts = df["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["sentiment", "count"]

        concern_counts = df["concern"].value_counts().reset_index()
        concern_counts.columns = ["concern", "count"]

        fig1 = px.bar(topic_counts, x="topic", y="count", title="Topic Distribution")
        fig2 = px.bar(sentiment_counts, x="sentiment", y="count", title="Sentiment Distribution")
        fig3 = px.bar(concern_counts, x="concern", y="count", title="Concern Level Distribution")

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### Classified Table")
        display_df = df.copy()
        display_df["post_preview"] = display_df["full_text"].apply(lambda x: truncate_text(x, 120))

        st.dataframe(
            display_df[["post_preview", "topic", "sentiment", "concern", "summary", "url"]],
            use_container_width=True
        )

        st.markdown("### Detail View")
        selected_idx = st.selectbox("Select a row to inspect", list(range(len(display_df))))
        selected_row = display_df.iloc[selected_idx]

        st.write(f"**Topic:** {selected_row['topic']}")
        st.write(f"**Sentiment:** {selected_row['sentiment']}")
        st.write(f"**Concern:** {selected_row['concern']}")
        st.write(f"**Summary:** {selected_row['summary']}")
        st.write(f"**URL:** {selected_row['url']}")
    else:
        st.info("Run Classification after preprocessing.")

with tabs[3]:
    st.subheader("Trend Detection Engine")
    results = st.session_state.trend_results

    if results:
        daily_counts = results.get("daily_counts", pd.DataFrame())
        topic_by_day = results.get("topic_by_day", pd.DataFrame())
        concern_by_day = results.get("concern_by_day", pd.DataFrame())
        top_subreddits = results.get("top_subreddits", pd.DataFrame())
        top_keywords = results.get("top_keywords", [])
        spike_alert = results.get("spike_alert")

        if not daily_counts.empty:
            fig1 = px.line(daily_counts, x="day", y="post_count", markers=True, title="Posts by Day")
            st.plotly_chart(fig1, use_container_width=True)

        if not topic_by_day.empty:
            fig2 = px.bar(topic_by_day, x="day", y="count", color="topic", title="Topic by Day")
            st.plotly_chart(fig2, use_container_width=True)

        if not concern_by_day.empty:
            fig3 = px.density_heatmap(concern_by_day, x="day", y="concern", z="count", title="Concern Level by Day")
            st.plotly_chart(fig3, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Top Keywords")
            st.write(", ".join(top_keywords) if top_keywords else "No keywords available.")

        with col2:
            st.markdown("### Top Subreddits")
            if not top_subreddits.empty:
                st.dataframe(top_subreddits, use_container_width=True)
            else:
                st.write("No subreddit data available.")

        if spike_alert:
            st.warning(
                f"Concern-level posts increased on {spike_alert['date']}. "
                f"Spike size: {spike_alert['spike_size']}. "
                f"Probable topic driver: {spike_alert['probable_topic_driver']}."
            )
    else:
        st.info("Run Detect Trends after classification.")

with tabs[4]:
    st.subheader("Insight Generator")
    insights = st.session_state.insights

    if insights:
        st.markdown("### Executive Summary")
        st.write(insights.get("executive_summary", ""))

        st.markdown("### Top 3 Themes")
        for theme in insights.get("top_themes", []):
            st.write(f"- {theme}")

        st.markdown("### Notable Source Shifts")
        st.write(insights.get("source_shifts", ""))

        st.markdown("### Possible Response Focus")
        st.write(insights.get("response_focus", ""))

        st.markdown("### Representative Examples")
        for example in insights.get("representative_examples", []):
            st.write(f"- {example}")
    else:
        st.info("Run Generate Insights after trend detection.")

with tabs[5]:
    st.subheader("Report Builder")

    report_title = st.text_input("Report title", value="Weekly Research Monitoring Report")
    include_sections = st.multiselect(
        "Included sections",
        ["executive summary", "charts", "top narratives", "examples", "methodology"],
        default=["executive summary", "charts", "top narratives", "examples"]
    )
    tone = st.selectbox("Tone", ["executive", "research", "partner-friendly"])

    st.write(f"Selected tone: **{tone}**")
    st.write(f"Included sections: **{', '.join(include_sections)}**")

    if st.button("Generate Report"):
        classified_df = st.session_state.classified_df

        metrics = {
            "total_posts": len(classified_df),
            "unique_subreddits": classified_df["subreddit"].nunique() if not classified_df.empty else 0,
            "top_topic": classified_df["topic"].mode().iloc[0] if not classified_df.empty and "topic" in classified_df.columns else "N/A"
        }

        output_path = "data/reports/research_report.pdf"

        build_pdf_report(
            output_path=output_path,
            report_title=report_title,
            insights=st.session_state.insights,
            metrics=metrics,
            trend_results=st.session_state.trend_results
        )

        st.success("Report generated successfully.")

        with open(output_path, "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name="research_report.pdf",
                mime="application/pdf"
            )