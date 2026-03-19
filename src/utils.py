from datetime import datetime
import pandas as pd


def safe_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def truncate_text(text, max_len=180):
    text = safe_text(text)
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def to_datetime_series(series):
    return pd.to_datetime(series, errors="coerce")


def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")