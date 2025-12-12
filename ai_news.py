# ai_news.py
import requests
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# ---------------------------
# 🔐 HARD-CODED API KEY
# ---------------------------
import streamlit as st
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]   # ← replace this

# ---------------------------
#  DOWNLOAD VADER IF MISSING
# ---------------------------
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except:
    nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

# ============================================================
# 1) Fetch Top 5 Latest News
# ============================================================
def fetch_recent_news(company):
    """
    Fetch top 5 latest financial/news headlines for this company.
    Uses NewsAPI.
    """

    if not NEWS_API_KEY:
        print("❌ ERROR: Missing NEWS_API_KEY")
        return []

    url = (
        "https://newsapi.org/v2/everything?"
        f"q={company} OR {company} stock OR {company} shares&"
        "language=en&"
        "sortBy=publishedAt&"
        "pageSize=5&"
        f"apiKey={NEWS_API_KEY}"
    )

    try:
        response = requests.get(url)
        data = response.json()

        if "articles" not in data:
            return []

        return [article["title"] for article in data["articles"]]

    except Exception as e:
        print("❌ NewsAPI error:", e)
        return []

# ============================================================
# 2) VADER Sentiment Analysis
# ============================================================
def analyze_news_sentiment(headlines):
    """
    Analyze sentiment without using Gemini.
    Output:
    - summary
    - sentiment category
    - score
    - risks
    - opportunities
    """

    if not headlines:
        return {
            "summary": "No recent news about this company.",
            "sentiment": "Neutral",
            "score": 0,
            "risks": [],
            "opportunities": []
        }

    # Sentiment score for each headline
    scores = [sia.polarity_scores(h)["compound"] for h in headlines]
    avg_score = sum(scores) / len(scores)

    # Category
    if avg_score > 0.2:
        senti = "Positive"
    elif avg_score < -0.2:
        senti = "Negative"
    else:
        senti = "Neutral"

    # Simple keyword-based risks & opportunities
    risks = [
        h for h in headlines
        if any(w in h.lower() for w in ["fall", "loss", "down", "fraud", "decline", "risk"])
    ]

    opportunities = [
        h for h in headlines
        if any(w in h.lower() for w in ["rise", "gain", "profit", "growth", "beats", "surge"])
    ]

    summary = (
        f"Based on {len(headlines)} recent news items, "
        f"overall sentiment is **{senti}** with a score of **{avg_score:.2f}**."
    )

    return {
        "summary": summary,
        "sentiment": senti,
        "score": round(avg_score, 2),
        "risks": risks,
        "opportunities": opportunities
    }
