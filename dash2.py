import streamlit as st
from stock_data import get_company_info, get_company_history
import plotly.graph_objects as go
from list import full_company_df
from utils import format_indian
from predict_safety import predict_safety
from ai_news import fetch_recent_news, analyze_news_sentiment

st.set_page_config(page_title="StockSafe AI Dashboard", layout="wide")

# ================================================================
# CUSTOM CSS - Modern Admin Template Style
# ================================================================
st.markdown("""
    <style>

    /* Main container spacing */
    .main {padding: 1.5rem;}

    /* Title */
    .dashboard-title {
        font-size: 32px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.3rem;
    }

    /* Section Title */
    .section-header {
        font-size: 20px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
        color: #34495e;
    }

    /* Cards */
    .card {
        background: white;
        padding: 18px 20px;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8;
    }

    .metric-icon {
        font-size: 32px;
        opacity: 0.9;
        margin-bottom: 8px;
    }

    /* News Cards */
    .news-card {
        background: #ffffff;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        border-left: 6px solid #2e86de;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    }

    .news-title {
        font-size: 15px;
        font-weight: 600;
        color: #2d3436;
    }

    /* Safety card colors */
    .safe {border-left: 6px solid #00b894;}
    .moderate {border-left: 6px solid #fdcb6e;}
    .risky {border-left: 6px solid #d63031;}

    </style>
""", unsafe_allow_html=True)

# ================================================================
# HEADER
# ================================================================
st.markdown("<div class='dashboard-title'>📊 StockSafe AI Dashboard</div>", unsafe_allow_html=True)
st.caption("Professional analytics for Indian stocks — ML Safety + Sentiment + Charts + Assistant")

# ================================================================
# TOP: Company Selection
# ================================================================
st.markdown("### 🔍 Select Company")
company = st.selectbox("", full_company_df["Company Name"].tolist())
symbol = full_company_df[full_company_df["Company Name"] == company]["Symbol"].iloc[0]

# ================================================================
# COMPANY METRIC CARDS
# ================================================================
info = get_company_info(symbol)

st.markdown("<div class='section-header'>Company Overview</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='card'><div class='metric-icon'>📦</div><h4>Market Cap</h4><h2>{format_indian(info.get('marketCap',0))}</h2></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='card'><div class='metric-icon'>📈</div><h4>P/E Ratio</h4><h2>{info.get('trailingPE','N/A')}</h2></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='card'><div class='metric-icon'>🏭</div><h4>Sector</h4><h2>{info.get('sector','N/A')}</h2></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='card'><div class='metric-icon'>⭐</div><h4>52W High</h4><h2>₹{format_indian(info.get('fiftyTwoWeekHigh',0))}</h2></div>", unsafe_allow_html=True)

# ================================================================
# PRICE CHART SECTION (Big Chart)
# ================================================================
data = get_company_history(symbol)

st.markdown("<div class='section-header'>Price Action & Volume</div>", unsafe_allow_html=True)

chart_container = st.container()
with chart_container:
    if data is not None and not data.empty:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'],
            name="Price",
            increasing_line_color='#00b894',
            decreasing_line_color='#e74c3c'
        ))
        data['SMA20'] = data['Close'].rolling(20).mean()
        data['SMA50'] = data['Close'].rolling(50).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], name="SMA 20"))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], name="SMA 50"))

        fig.update_layout(height=500, xaxis_rangeslider_visible=False, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# ================================================================
# SAFETY SCORE + NEWS SIDE-BY-SIDE (Admin-Style)
# ================================================================
st.markdown("<div class='section-header'>AI Safety Score & Market Headlines</div>", unsafe_allow_html=True)

left, right = st.columns([1.1, 1])

# ---------- SAFETY SCORE ----------
with left:
    safety = predict_safety(symbol)
    rating_class = safety["label"].lower()

    st.markdown(f"""
    <div class="card {rating_class}">
        <h3>🛡 Safety Score</h3>
        <h1>{safety['emoji']} {safety['score']:.2f}</h1>
        <h4>{safety['label']}</h4>
        <p style="color:#636e72;">
            Score derived from market volatility, alpha, index comparison & predicted future drawdown.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------- NEWS (CARDS) ----------
with right:
    st.markdown("### 📰 Latest News")
    headlines = fetch_recent_news(company)

    if not headlines:
        st.info("No news found")
    else:
        for i, h in enumerate(headlines[:5], 1):
            st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">{h}</div>
                </div>
            """, unsafe_allow_html=True)

    # Sentiment
    senti = analyze_news_sentiment(headlines)
    st.metric("Sentiment", senti["sentiment"], delta=senti["score"])

# ================================================================
# AI Assistant Section
# ================================================================
st.markdown("<div class='section-header'>💬 AI Investment Assistant</div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Ask about risk, buy/sell, price targets...")

def make_reply(question):
    # Simple rule-based advisor
    if "buy" in question.lower():
        if safety["score"] >= 0.7:
            return "This stock looks safe for accumulation."
        elif safety["score"] >= 0.4:
            return "Moderate safety — SIP entry preferred."
        else:
            return "Risky currently — avoid new entries."

    if "risk" in question.lower():
        return "Key risks: volatility, sector trends & weak sentiment."

    return f"Use safety score ({safety['score']}) + sentiment ({senti['sentiment']}) to form a decision."

if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    reply = make_reply(prompt)
    st.session_state.messages.append({"role":"assistant","content":reply})
    with st.chat_message("assistant"):
        st.write(reply)
