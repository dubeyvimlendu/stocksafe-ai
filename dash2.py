import streamlit as st
import plotly.graph_objects as go

from stock_data import get_company_info, get_company_history
from list import full_company_df
from utils import format_indian
from predict_safety import predict_safety
from ai_news import fetch_recent_news, analyze_news_sentiment

# ================================================================
# PAGE CONFIG
# ================================================================
st.set_page_config(page_title="StockSafe AI Dashboard", layout="wide")

# ================================================================
# -------------------- CACHING LAYER ------------------------------
# ================================================================

@st.cache_data(ttl=3600)
def cached_company_info(symbol):
    return get_company_info(symbol)

@st.cache_data(ttl=3600)
def cached_price_history(symbol):
    return get_company_history(symbol)

@st.cache_data(ttl=1800)
def cached_news(company):
    return fetch_recent_news(company)

@st.cache_data(ttl=3600)
def cached_safety(symbol):
    return predict_safety(symbol)

# ================================================================
# CUSTOM CSS
# ================================================================
st.markdown("""
<style>
.main {padding: 1.5rem;}
.dashboard-title {font-size: 32px;font-weight: 700;color: #2c3e50;}
.section-header {font-size: 20px;font-weight: 600;margin: 20px 0 10px;}
.card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    border: 1px solid #e8e8e8;
}
.news-card {
    background: #fff;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    border-left: 6px solid #2e86de;
}
.safe {border-left: 6px solid #00b894;}
.moderate {border-left: 6px solid #fdcb6e;}
.risky {border-left: 6px solid #d63031;}
</style>
""", unsafe_allow_html=True)

# ================================================================
# HEADER
# ================================================================
st.markdown("<div class='dashboard-title'>📊 StockSafe AI Dashboard</div>", unsafe_allow_html=True)
st.caption("Professional analytics for Indian stocks — ML Safety + Sentiment + Charts")

# ================================================================
# COMPANY SELECTION
# ================================================================
st.markdown("### 🔍 Select Company")

company = st.selectbox("", full_company_df["Company Name"].tolist())
symbol = full_company_df.loc[
    full_company_df["Company Name"] == company, "Symbol"
].iloc[0]

# ================================================================
# COMPANY INFO (CACHED)
# ================================================================
info = cached_company_info(symbol)

st.markdown("<div class='section-header'>Company Overview</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"<div class='card'><h4>Market Cap</h4><h2>{format_indian(info.get('marketCap',0))}</h2></div>",
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        f"<div class='card'><h4>P/E Ratio</h4><h2>{info.get('trailingPE','N/A')}</h2></div>",
        unsafe_allow_html=True
    )
with c3:
    st.markdown(
        f"<div class='card'><h4>Sector</h4><h2>{info.get('sector','N/A')}</h2></div>",
        unsafe_allow_html=True
    )
with c4:
    st.markdown(
        f"<div class='card'><h4>52W High</h4><h2>₹{format_indian(info.get('fiftyTwoWeekHigh',0))}</h2></div>",
        unsafe_allow_html=True
    )

# ================================================================
# PRICE CHART (CACHED)
# ================================================================
st.markdown("<div class='section-header'>Price Action</div>", unsafe_allow_html=True)

data = cached_price_history(symbol)

if data is not None and not data.empty:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price"
    ))

    data['SMA20'] = data['Close'].rolling(20).mean()
    data['SMA50'] = data['Close'].rolling(50).mean()

    fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], name="SMA 20"))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], name="SMA 50"))

    fig.update_layout(height=500, template="plotly_white", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# ================================================================
# SAFETY + NEWS
# ================================================================
st.markdown("<div class='section-header'>AI Safety & News</div>", unsafe_allow_html=True)
left, right = st.columns([1.1, 1])

# ---------- SAFETY ----------
with left:
    safety = cached_safety(symbol)
    st.markdown(
        f"""
        <div class="card {safety['label'].lower()}">
            <h3>🛡 Safety Score</h3>
            <h1>{safety['emoji']} {safety['score']:.2f}</h1>
            <h4>{safety['label']}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- NEWS ----------
with right:
    st.markdown("### 📰 Latest News")
    headlines = cached_news(company)

    if headlines:
        for h in headlines[:5]:
            st.markdown(
                f"<div class='news-card'><strong>{h}</strong></div>",
                unsafe_allow_html=True
            )

        senti = analyze_news_sentiment(headlines)
        st.metric("Sentiment", senti["sentiment"], delta=senti["score"])
    else:
        st.info("No recent news found")

# ================================================================
# AI CHAT (NO API CALLS HERE)
# ================================================================
st.markdown("<div class='section-header'>💬 AI Investment Assistant</div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Ask about buy/sell/risk...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    if "buy" in prompt.lower():
        reply = "Safe for accumulation." if safety["score"] >= 0.7 else "Moderate risk — SIP preferred."
    elif "risk" in prompt.lower():
        reply = "Risk driven by volatility and sentiment."
    else:
        reply = "Use safety score and sentiment together."

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)
