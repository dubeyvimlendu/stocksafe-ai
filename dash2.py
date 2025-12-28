import streamlit as st
import plotly.graph_objects as go

from stock_data import get_company_info, get_company_history
from list import full_company_df
from utils import format_indian
from predict_safety import predict_safety
from ai_news import get_news_analysis


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
    return get_news_analysis(company)

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
    st.plotly_chart(fig, width="stretch")


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

    news_data = get_news_analysis(company)

    st.metric(
        "Sentiment",
        news_data["sentiment"],
        delta=round(news_data["final_score"], 2)
    )

    for h in news_data["headlines"]:
        st.markdown(
            f"""
            <div class="news-card">
                <div class="news-title">{h}</div>
            </div>
            """,
            unsafe_allow_html=True
        )



# ================================================================
# AI Investment Assistant (Smart Version)
# ================================================================

st.markdown("<div class='section-header'>💬 AI Investment Assistant</div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Ask about buy/sell, risk, or outlook...")

def make_reply(question, safety_data, news_data):
    score = safety_data["score"]
    market_score = safety_data["market_score"]
    news_score = safety_data["news_score"]
    sentiment = news_data["sentiment"]

    question = question.lower()

    # ---------------- BUY / INVEST ----------------
    if "buy" in question or "invest" in question:
        if score >= 0.75:
            return (
                "✅ **Strong Buy Signal**\n\n"
                f"• Overall score: {score}\n"
                f"• Market trend is strong\n"
                f"• News sentiment is **{sentiment}**\n\n"
                "This stock looks suitable for accumulation."
            )
        elif score >= 0.4:
            return (
                "⚠️ **Moderate Opportunity**\n\n"
                f"• Score: {score}\n"
                "• Some volatility present\n"
                "• SIP or partial entry recommended."
            )
        else:
            return (
                "🚨 **High Risk**\n\n"
                "• Weak market structure\n"
                "• Negative or unstable sentiment\n"
                "• Avoid fresh positions for now."
            )

    # ---------------- RISK ----------------
    if "risk" in question:
        return (
            f"📉 **Risk Analysis**\n\n"
            f"• Market Risk Score: {market_score}\n"
            f"• News Sentiment: {sentiment}\n"
            "• Risk comes from volatility & recent momentum\n"
        )

    # ---------------- TARGET / FUTURE ----------------
    if "target" in question or "future" in question:
        return (
            "📊 **Outlook Summary**\n\n"
            "This projection is based on:\n"
            "• Market momentum\n"
            "• News sentiment\n"
            "• Historical price behavior\n\n"
            "⚠️ Not a price prediction, but a risk-adjusted outlook."
        )

    # ---------------- DEFAULT ----------------
    return (
        "🤖 You can ask things like:\n"
        "• Is this stock safe to buy?\n"
        "• What is the risk level?\n"
        "• Should I invest now?\n"
        "• What does sentiment say?\n"
    )

# Handle input
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    reply = make_reply(prompt, safety, news_data)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)
