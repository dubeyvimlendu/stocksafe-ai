import numpy as np
import json
from joblib import load

from ml_pipeline import build_features_for_ticker
from ai_news import get_news_analysis

# ======================================================
# LOAD MODEL + METADATA
# ======================================================

model = load("models/safety_model.joblib")

with open("safety_model_metadata.json", "r") as f:
    meta = json.load(f)

FEATURES = meta["features"]

# ======================================================
# UTILS
# ======================================================

def categorize_score(score):
    if score >= 0.75:
        return "SAFE", "🟢"
    elif score >= 0.40:
        return "MODERATE", "🟡"
    else:
        return "RISKY", "🔴"

# ======================================================
# MAIN PREDICTION FUNCTION
# ======================================================

def predict_safety(symbol):
    """
    Final stock safety prediction using:
    - ML market model
    - News sentiment (ML + VADER)
    """

    # -------------------------------
    # Market-based ML prediction
    # -------------------------------
    df = build_features_for_ticker(symbol, period="1y")

    if df is None or df.empty:
        return None

    latest_row = df.iloc[-1]
    X = latest_row[FEATURES].values.reshape(1, -1)

    market_score = float(model.predict(X)[0])

    # -------------------------------
    # News-based sentiment
    # -------------------------------
    news_data = get_news_analysis(symbol)
    news_score = news_data["final_score"]

    # -------------------------------
    # Final weighted score
    # -------------------------------
    final_score = (
        0.65 * market_score +
        0.35 * news_score
    )

    label, emoji = categorize_score(final_score)

    return {
        "score": round(final_score, 3),
        "label": label,
        "emoji": emoji,
        "market_score": round(market_score, 3),
        "news_score": round(news_score, 3),
        "sentiment": news_data["sentiment"]
    }
