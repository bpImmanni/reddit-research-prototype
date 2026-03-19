import re
import pandas as pd
import nltk
from langdetect import detect, DetectorFactory
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

DetectorFactory.seed = 0

nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

STOPWORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()


def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = []
    for word in text.split():
        if word not in STOPWORDS and len(word) > 2:
            tokens.append(LEMMATIZER.lemmatize(word))

    return " ".join(tokens)


def detect_language(text):
    try:
        if not text or not str(text).strip():
            return "unknown"
        return detect(text)
    except Exception:
        return "unknown"


def extract_keywords_simple(text, top_n=15):
    if not text or not str(text).strip():
        return []

    words = [w for w in text.split() if len(w) > 3]
    if not words:
        return []

    freq = pd.Series(words).value_counts().head(top_n)
    return list(freq.index)


def extract_entities_simple(text, top_n=10):
    """
    Simple placeholder entity extraction for V1:
    grabs repeated title-case-like tokens from original text.
    """
    if not text or not str(text).strip():
        return []

    tokens = re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", str(text))
    if not tokens:
        return []

    freq = pd.Series(tokens).value_counts().head(top_n)
    return list(freq.index)


def preprocess_dataframe(df):
    if df.empty:
        return df, {
            "duplicates_removed": 0,
            "null_rows_removed": 0,
            "rows_retained": 0,
            "language_detected": "unknown"
        }

    work = df.copy()

    original_rows = len(work)

    work["title"] = work["title"].fillna("")
    work["body"] = work["body"].fillna("")
    work["full_text"] = (work["title"] + " " + work["body"]).str.strip()

    work = work[work["full_text"].str.len() > 0].copy()
    after_null_drop = len(work)

    work = work.drop_duplicates(subset=["full_text"]).copy()
    after_dedup = len(work)

    work["language"] = work["full_text"].apply(detect_language)
    work["text_length"] = work["full_text"].apply(lambda x: len(str(x)))
    work["clean_text"] = work["full_text"].apply(clean_text)

    combined_clean_text = " ".join(work["clean_text"].fillna("").tolist())
    combined_original_text = " ".join(work["full_text"].fillna("").tolist())

    keywords = extract_keywords_simple(combined_clean_text, top_n=15)
    entities = extract_entities_simple(combined_original_text, top_n=10)

    stats = {
        "duplicates_removed": after_null_drop - after_dedup,
        "null_rows_removed": original_rows - after_null_drop,
        "rows_retained": after_dedup,
        "language_detected": work["language"].mode().iloc[0] if not work.empty else "unknown"
    }

    return work, stats, keywords, entities