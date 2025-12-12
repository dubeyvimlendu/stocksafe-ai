import numpy as np
import pandas as pd
from joblib import load
from ml_pipeline import build_features_for_ticker
import json

# Load model + metadata
model = load("safety_model.joblib")

with open("safety_model_metadata.json", "r") as f:
    meta = json.load(f)

FEATURES = meta["features"]

def categorize_score(score):
    if score >= 0.75:
        return "SAFE", "🟩"
    elif score >= 0.40:
        return "MODERATE", "🟨"
    else:
        return "RISKY", "🟥"

def predict_safety(symbol):
    df = build_features_for_ticker(symbol, period="1y")

    if df is None or df.empty:
        return None

    # last available row
    row = df.iloc[-1]

    # extract features
    x = row[FEATURES].values.reshape(1, -1)

    score = float(model.predict(x)[0])
    label, emoji = categorize_score(score)

    return {
        "score": round(score, 3),
        "label": label,
        "emoji": emoji
    }
