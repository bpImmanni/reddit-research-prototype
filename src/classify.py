import pandas as pd


TOPIC_RULES = {
    "antisemitic rhetoric": [
        "antisemitism", "antisemitic", "anti jewish", "anti-jewish",
        "jew hatred", "dirty jew", "jews are", "zionist pig"
    ],
    "conspiracy narratives": [
        "globalist", "cabal", "shadow government", "media control",
        "elite control", "jewish control", "zionist control", "replacement"
    ],
    "identity-based hostility": [
        "jewish", "jews", "zionist", "religion", "ethnic",
        "minority", "bigot", "racist", "hate group"
    ],
    "political amplification": [
        "election", "government", "policy", "party", "president",
        "politics", "senate", "congress", "left wing", "right wing"
    ],
    "harassment / abuse": [
        "harassment", "abuse", "targeting", "bullying", "hostility",
        "slur", "dogwhistle", "mocking", "insult"
    ],
    "threats / incitement": [
        "kill", "attack", "violent", "violence", "threat",
        "murder", "burn", "shoot", "wipe out", "hurt them"
    ],
    "misinformation / false claims": [
        "fake", "hoax", "lie", "false flag", "misinformation",
        "propaganda", "fabricated", "made up", "not real"
    ],
    "community response / support": [
        "support", "solidarity", "condemn", "protect", "stand with",
        "peace", "community", "safety", "defend"
    ],
    "news / event discussion": [
        "reported", "incident", "event", "news", "article",
        "happened", "coverage", "statement", "breaking"
    ],
}

HOSTILE_WORDS = [
    "hate", "attack", "threat", "kill", "abuse", "hostility",
    "harassment", "violent", "slur", "bullying", "wipe out"
]

SUPPORTIVE_WORDS = [
    "support", "solidarity", "care", "peace", "help", "protect",
    "condemn", "defend", "safety", "community"
]


def count_matches(text, keywords):
    text = str(text).lower()
    return sum(1 for word in keywords if word in text)


def classify_topic(text):
    text = str(text).lower()
    scores = {}

    for topic, keywords in TOPIC_RULES.items():
        scores[topic] = count_matches(text, keywords)

    best_topic = max(scores, key=scores.get)

    if scores[best_topic] == 0:
        return "unrelated / low signal"

    return best_topic


def classify_sentiment(text):
    text = str(text).lower()
    hostile_score = count_matches(text, HOSTILE_WORDS)
    supportive_score = count_matches(text, SUPPORTIVE_WORDS)

    if hostile_score > supportive_score and hostile_score > 0:
        return "hostile"
    if supportive_score > hostile_score and supportive_score > 0:
        return "supportive"
    return "neutral"


def classify_concern(text):
    text = str(text).lower()

    high_terms = [
        "kill", "attack", "violent", "threat", "murder",
        "shoot", "burn", "wipe out", "extremist"
    ]
    medium_terms = [
        "hate", "harassment", "misinformation", "hostility",
        "abuse", "slur", "dogwhistle", "conspiracy"
    ]

    high_score = count_matches(text, high_terms)
    medium_score = count_matches(text, medium_terms)

    if high_score > 0:
        return "high"
    if medium_score > 0:
        return "medium"
    return "low"


def classify_relevance(text, query):
    text = str(text).lower()
    query_words = [w.strip().lower() for w in str(query).split() if w.strip()]

    if not query_words:
        return "relevant"

    matches = sum(1 for w in query_words if w in text)
    if matches > 0:
        return "relevant"

    related_terms = [
        "jewish", "jews", "antisemitic", "antisemitism",
        "zionist", "synagogue", "hate crime", "religious targeting"
    ]

    related_matches = count_matches(text, related_terms)
    return "relevant" if related_matches > 0 else "not relevant"


def summarize_post(text):
    text = str(text).strip()
    if len(text) <= 180:
        return text
    return text[:180] + "..."


def run_classification(df, query="antisemitism"):
    if df.empty:
        return df

    work = df.copy()
    work["relevance"] = work["clean_text"].apply(lambda x: classify_relevance(x, query))
    work["topic"] = work["clean_text"].apply(classify_topic)
    work["sentiment"] = work["clean_text"].apply(classify_sentiment)
    work["concern"] = work["clean_text"].apply(classify_concern)
    work["summary"] = work["full_text"].apply(summarize_post)
    return work