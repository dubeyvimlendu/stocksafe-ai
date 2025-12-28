# ai_news.py

import requests
import nltk
import joblib
import streamlit as st
from nltk.sentiment import SentimentIntensityAnalyzer

# ======================================================
# CONFIG
# ======================================================

NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

MODEL_PATH = "models/news_sentiment_model.joblib"
VECTORIZER_PATH = "models/news_vectorizer.joblib"

sentiment_model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# Download VADER if missing
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except:
    nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

# ======================================================
# FETCH NEWS
# ======================================================

def fetch_recent_news(company):
    if not NEWS_API_KEY:
        return []

    url = (
        "https://newsapi.org/v2/everything?"
        f"q={company} OR {company} stock OR {company} shares&"
        "language=en&sortBy=publishedAt&pageSize=5&"
        f"apiKey={NEWS_API_KEY}"
    )

    try:
        res = requests.get(url)
        data = res.json()
        return [a["title"] for a in data.get("articles", [])]
    except:
        return []

# ======================================================
# VADER SENTIMENT
# ======================================================

def vader_sentiment(headlines):
    if not headlines:
        return {"score": 0, "sentiment": "Neutral"}

    scores = [sia.polarity_scores(h)["compound"] for h in headlines]
    avg = sum(scores) / len(scores)

    if avg > 0.2:
        sentiment = "Positive"
    elif avg < -0.2:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "score": round(avg, 2),
        "sentiment": sentiment
    }

# ======================================================
# ML SENTIMENT
# ======================================================

def ml_sentiment_score(headlines):
    if not headlines:
        return 0.5

    text = " ".join(headlines)
    vec = vectorizer.transform([text])
    return float(sentiment_model.predict_proba(vec)[0][1])

# ======================================================
# FINAL NEWS INTELLIGENCE
# ======================================================

def get_news_analysis(company):
    headlines = fetch_recent_news(company)

    vader = vader_sentiment(headlines)
    ml_score = ml_sentiment_score(headlines)

    final_score = (0.6 * ml_score) + (0.4 * ((vader["score"] + 1) / 2))

    return {
        "headlines": headlines,
        "sentiment": vader["sentiment"],
        "vader_score": vader["score"],
        "ml_score": round(ml_score, 3),
        "final_score": round(final_score, 3)
    }
