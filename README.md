
<h1 align="center">📊 StockSafe AI Dashboard</h1>

<p align="center">
  <a href="https://stocksafe-ai.streamlit.app" target="_blank">
    <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Streamlit App">
  </a>
</p>

<p align="center">
  <i>Professional analytics for Indian stocks — combining live market data, AI‑driven safety scoring, sentiment from news, and an interactive investment assistant.</i>
</p>

---

### 📘 Overview

StockSafe AI Dashboard is an interactive Streamlit app that helps investors quickly understand the **risk profile** of Indian stocks.  
It aggregates:

- Live stock price data and technical indicators
- News headlines and sentiment for the selected company
- An AI‑style safety score indicating how risky or safe the stock may be
- A simple rule‑based assistant for quick buy/sell and risk questions

🔗 **Live Demo:**  
https://stocksafe-ai.streamlit.app/

---

### 🔍 Key Features

- 📈 **Live Price Action:**  
  Candlestick chart with **SMA 20** and **SMA 50** overlays for trend analysis.

- 🧠 **AI Safety Score:**  
  Computes a safety score (0–1 style value) based on volatility, index comparison, alpha, and predicted drawdown, and labels the stock as **Safe**, **Moderate**, or **Risky**.

- 📰 **News & Sentiment:**  
  Fetches recent headlines for the selected company via API and runs **sentiment analysis** to show market mood.

- 🧾 **Company Snapshot:**  
  Key metrics like **Market Cap**, **P/E Ratio**, **Sector**, and **52‑Week High** in clean dashboard cards.

- 💬 **AI Investment Assistant:**  
  A rule‑based chat interface that uses safety score and sentiment to respond to questions such as *“Should I buy?”*, *“What is the risk?”*, etc.

- 🇮🇳 **India‑Focused:**  
  Optimized for Indian listed companies with formatted values in the Indian numbering style (e.g., crores, lakhs).

---

### 🧩 Tech Stack

| Component   | Details                                                                 |
|------------|-------------------------------------------------------------------------|
| Framework  | Streamlit                                                               |
| Language   | Python 3.10+                                                            |
| Data/Charts| Plotly, Pandas, yfinance / market data APIs (depending on your setup)   |
| AI / Logic | Custom `predict_safety` logic, news sentiment analyzer                  |
| Utilities  | Custom helpers (`stock_data`, `list`, `utils`, `ai_news`, etc.)        |
| Deployment | Streamlit Community Cloud                                               |

---

### 📂 Project Structure

> Adjust filenames if your structure differs.

```bash
stocksafe-ai/
│
├── dash_2.py                   # Main Streamlit application (dashboard UI)
│
├── stock_data.py            # Functions to get company info & historical prices
├── predict_safety.py        # Logic to compute safety score + label + emoji
├── ai_news.py               # Fetch recent news + run sentiment analysis
├── utils.py                 # Helper utilities (e.g., format_indian)
├── list.py                  # List / DataFrame of companies and symbols
│
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

### ⚙️ How to Run Locally

```bash
# 1. Clone this repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

# 2. (Optional but recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

Then open in your browser:  
http://localhost:8501

If you use any API keys (for news or market data), create a `.env` file or set environment variables as required by `ai_news.py` or `stock_data.py`.

---
### 📈 Technical Indicators Guide

The dashboard displays professional-grade charts with key indicators every investor should know:

| Indicator | What it Shows | How to Use |
|-----------|---------------|------------|
| **Candlestick Chart** | Daily **Open, High, Low, Close** prices in green (up) / red (down) bars | **Green candles** = buying pressure. **Long wicks** = rejection at highs/lows. |
| **SMA 20** (Simple Moving Average, 20-day) | Average closing price over **past 20 trading days** (~1 month) | **Price above SMA20** = short-term uptrend. **Support level** during pullbacks. |
| **SMA 50** (Simple Moving Average, 50-day) | Average closing price over **past 50 trading days** (~2-3 months) | **Price above SMA50** = medium-term bullish. **Golden Cross** when SMA20 crosses above SMA50. |

**Quick Trading Signals:**
- **Bullish:** Price > SMA20 > SMA50 (stacked upward)
- **Bearish:** Price < SMA20 < SMA50 (stacked downward)  
- **Trend Change:** Watch SMA20 crossing SMA50 (major signal)
- **Support/Resistance:** Price often bounces off these moving averages

**Volume** (bottom of chart): Higher volume confirms the price move's strength.

> 💡 **Pro Tip:** Use SMA20 for short-term trades (1-3 months), SMA50 for position trading (3-12 months).


### 🧮 Safety Score & Logic

The **Safety Score** is designed as a quick, intuitive indicator of risk for a selected stock.  
It typically considers:

- **Market volatility**
- **Alpha vs benchmark / index**
- **Historical drawdowns**
- **Stability of recent price action**

The output:

- A numeric **score** (e.g., 0.0–1.0 scale)
- A **label**: `Safe`, `Moderate`, or `Risky`
- An **emoji** for a quick visual cue

Example interpretation:

- 🟢 **Safe** (score ≥ 0.7):  
  Stock appears relatively stable; corrections historically limited.

- 🟡 **Moderate** (0.4 ≤ score < 0.7):  
  Balanced risk–reward, better suited for phased or SIP‑style entries.

- 🔴 **Risky** (score < 0.4):  
  High volatility / downside risk; avoid new entries or handle with caution.

> Note: The logic can be tuned inside `predict_safety.py` to match your own risk model.

---

### 📰 News & Sentiment

For each selected company, the app:

1. Uses `fetch_recent_news(company_name)` from `ai_news.py` to fetch latest headlines.
2. Displays these headlines in **card‑style UI** with an admin‑dashboard look.
3. Calls `analyze_news_sentiment(headlines)` to compute an overall sentiment label and score.
4. Shows a **sentiment metric** (e.g., Positive/Neutral/Negative with a numeric score).

This gives a quick view of whether current news flow is supportive or negative for the stock.

---

### 💬 AI Investment Assistant

The dashboard includes a lightweight, rule‑based assistant:

- Chat interface using `st.chat_input` and `st.chat_message`.
- Stores the conversation in `st.session_state.messages`.
- Uses both **Safety Score** and **Sentiment** to answer:
  - “Is it safe to buy now?”
  - “What is the risk?”
  - “Should I avoid this stock?”
  - “How do I use the score?”

Example internal logic (simplified):

- If the prompt contains “buy”:
  - High safety → suggests accumulation
  - Medium safety → suggests SIP / staggered entry
  - Low safety → suggests avoiding new entries

This is intentionally transparent and rule‑based, not a black‑box trading system.

---

### 🚀 Deployment Details

| Item        | Value                                                                  |
|-------------|------------------------------------------------------------------------|
| GitHub Repo | `https://github.com/<your-username>/<your-repo-name>`                 |
| Branch      | `main`                                                                 |
| App File    | `app.py`                                                               |
| Live App    | https://stocksafe-ai.streamlit.app/                                   |

---

### ⚠️ Disclaimer

This dashboard is built **for educational and research purposes only**.

- It is **not** financial advice.
- It does **not** guarantee accuracy or future performance.
- Always do your own research and consult a registered financial advisor before making investment decisions.

By using this tool, you agree that the author is not responsible for any financial losses or decisions based on the dashboard.

---

### 🌟 Future Enhancements

- More advanced safety scoring with ML models (e.g., XGBoost, Random Forests).
- Sector and index‑level risk comparison.
- Portfolio view: safety, correlation, and drawdown metrics for multiple holdings.
- Richer sentiment using full article bodies and transformer models.
- Dark mode and additional theme customizations.

---

### 👨‍💻 Author

Developed with ❤️ by **Vimlendu Dubey**  
📧 Email: [dubeyvimlendu@gmail.com](mailto:dubeyvimlendu@gmail.com)  
💼 GitHub: [https://github.com/dubeyvimlendu](https://github.com/dubeyvimlendu)  
🌐 Live Dashboard: [https://stocksafe-ai.streamlit.app](https://stocksafe-ai.streamlit.app)

---

<h3 align="center">⭐ If you find this project helpful, please consider starring the repository!</h3>


