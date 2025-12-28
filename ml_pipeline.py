import numpy as np
import pandas as pd
import yfinance as yf

# ===============================================================
# 1) Fetch Index Data
# ===============================================================

def fetch_index_history(index_symbol="^NSEI", period="3y"):
    try:
        t = yf.Ticker(index_symbol)
        df = t.history(period=period)
        return df
    except Exception as e:
        print("Index fetch error:", e)
        return pd.DataFrame()

# ===============================================================
# 2) Technical Indicators
# ===============================================================

def add_technical_indicators(df):
    df = df.copy()

    # Daily returns
    df["return"] = df["Close"].pct_change()

    # Rolling returns
    df["7d_return"]  = df["Close"].pct_change(7)
    df["30d_return"] = df["Close"].pct_change(30)
    df["90d_return"] = df["Close"].pct_change(90)

    # Volatility
    df["vol_30"] = df["return"].rolling(30).std()
    df["vol_90"] = df["return"].rolling(90).std()

    # Simple MAs
    df["SMA_20"]  = df["Close"].rolling(20).mean()
    df["SMA_50"]  = df["Close"].rolling(50).mean()

    df["mom_20"] = df["Close"] / df["SMA_20"] - 1
    df["mom_50"] = df["Close"] / df["SMA_50"] - 1

    # RSI
    delta = df["Close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(14).mean()
    avg_loss = pd.Series(loss).rolling(14).mean()

    rs = avg_gain / (avg_loss + 1e-9)
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA_26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    return df

# ===============================================================
# 3) Market Features
# ===============================================================

def compute_market_features(stock_df, index_df):
    out = {}
    price = stock_df["Close"]
    idx = index_df["Close"].reindex(price.index).ffill()

    # Index returns
    out["index_7d_ret"] = idx.pct_change(7)
    out["index_30d_ret"] = idx.pct_change(30)
    out["index_90d_ret"] = idx.pct_change(90)

    # Stock returns (already added above)
    out["alpha_30d"] = stock_df["30d_return"] - out["index_30d_ret"]
    out["alpha_90d"] = stock_df["90d_return"] - out["index_90d_ret"]

    # Rolling correlations
    out["corr_30"] = price.pct_change().rolling(30).corr(idx.pct_change())
    out["corr_90"] = price.pct_change().rolling(90).corr(idx.pct_change())

    # Market regime
    out["market_regime_30_up"] = (out["index_30d_ret"] > 0).astype(int)

    return pd.DataFrame(out, index=stock_df.index)

# ===============================================================
# 4) Fetch Stock History
# ===============================================================

def fetch_history(symbol, period="3y"):
    try:
        if not symbol.endswith(".NS"):
            symbol = symbol + ".NS"

        t = yf.Ticker(symbol)
        df = t.history(period=period)
        return df

    except Exception as e:
        print("Stock fetch error:", e)
        return pd.DataFrame()

# ===============================================================
# 5) Future Stats (labels)
# ===============================================================

def compute_future_stats(df):
    df = df.copy()

    # Future 90-day return
    df["future_90d_return"] = df["Close"].shift(-90) / df["Close"] - 1

    # Future 30-day drawdown
    future_min = df["Close"].shift(-1).rolling(30).min().shift(-29)
    df["future_max_drawdown_30"] = (future_min - df["Close"]) / df["Close"]

    return df

# ===============================================================
# 6) Assemble All Features
# ===============================================================

def build_features_for_ticker(symbol, period="3y", include_info=True, index_symbol="^NSEI"):
    hist = fetch_history(symbol, period)
    if hist is None or hist.empty:
        return None

    # Technical indicators
    hist = add_technical_indicators(hist)

    # Market features
    idx = fetch_index_history(index_symbol, period)
    if not idx.empty:
        market = compute_market_features(hist, idx)
        hist = hist.join(market)

    # Fundamentals
    if include_info:
        t = yf.Ticker(symbol + ".NS" if not symbol.endswith(".NS") else symbol)
        info = t.info
        hist["marketCap"] = info.get("marketCap", np.nan)
        hist["trailingPE"] = info.get("trailingPE", np.nan)
        hist["priceToBook"] = info.get("priceToBook", np.nan)
        hist["beta"] = info.get("beta", np.nan)
        hist["sector"] = info.get("sector", None)

    # Future labels
    hist = compute_future_stats(hist)

    return hist

# ===============================================================
# 7) Safety Label Logic
# ===============================================================

def create_safety_label(df):
    df = df.copy()

    # Defaults
    df["label"] = 0.0
    df["future_max_drawdown_30"] = df["future_max_drawdown_30"].fillna(0)
    df["future_90d_return"] = df["future_90d_return"].fillna(0)
    df["alpha_30d"] = df["alpha_30d"].fillna(0)

    # SAFE LABEL
    cond_safe = (
        (df["future_max_drawdown_30"] > -0.10) &  # drawdown less than -10%
        (df["future_90d_return"] > 0.02) &
        (df["alpha_30d"] > -0.02)
    )

    # MODERATE
    cond_mod = (
        (df["future_max_drawdown_30"] > -0.20) &
        (df["future_90d_return"] > -0.05)
    )

    df.loc[cond_safe, "label"] = 1.0
    df.loc[cond_mod & (~cond_safe), "label"] = 0.5

    return df
