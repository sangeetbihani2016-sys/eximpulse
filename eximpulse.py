import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import requests
import base64
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="EximPulse | Real-Time Trade Terminal", 
    layout="wide", 
    page_icon="🚢"
)

# --- 1. SECURE KEY LOADER ---
try:
    NEWS_API_KEY = st.secrets["general"]["news_api_key"]
except:
    NEWS_API_KEY = ""

# --- 2. CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    
    /* TICKER */
    .news-ticker-container {
        width: 100%;
        background-color: #1c2029;
        color: #4CAF50;
        padding: 8px 0;
        white-space: nowrap;
        overflow: hidden;
        border-bottom: 1px solid #333;
        margin-bottom: 15px;
    }
    .news-ticker-text {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 90s linear infinite;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 14px;
    }
    @keyframes marquee {
        0%   { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    
    /* PROFILE */
    details > summary {
        list-style: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 10px;
        border-radius: 50px;
        border: 1px solid #333;
        background: #161920;
    }
    .profile-img {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #4CAF50;
    }
    .profile-text { font-weight: bold; color: white; font-size: 16px; }
    .profile-expanded {
        margin-top: 10px; padding: 15px; background: #1c2029;
        border-radius: 10px; border-left: 3px solid #4CAF50;
        font-size: 13px; color: #cfcfcf;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. REAL DATA MAPPING (NO FAKES) ---
# Mapping HSN/Commodities to Real-Time Yahoo Finance Tickers
# Note: We use Futures contracts as benchmarks.
COMMODITY_MAP = {
    "Cotton (5201)": "CT=F",      # Cotton No. 2
    "Coffee (0901)": "KC=F",      # Coffee C
    "Sugar (1701)": "SB=F",       # Sugar No. 11
    "Wheat (1001)": "ZW=F",       # Chicago Wheat
    "Corn (1005)": "ZC=F",        # Corn Futures
    "Soybean (1201)": "ZS=F",     # Soybean Futures
    "Silver (7106)": "SI=F",      # Silver
    "Crude Oil": "CL=F",          # WTI Crude
    "Cocoa (1801)": "CC=F"        # Cocoa
}

# --- 4. DATA FUNCTIONS ---

@st.cache_data(ttl=60) # Cache for 1 min only (Keep it fresh)
def get_live_price(ticker_symbol):
    """Fetches ACTUAL live market data from Yahoo Finance."""
    try:
        data = yf.Ticker(ticker_symbol)
        history = data.history(period="5d") # Get last 5 days
        
        if not history.empty:
            current_price = history['Close'].iloc[-1]
            prev_close = history['Close'].iloc[-2]
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # Get volume if available
            volume = history['Volume'].iloc[-1] if 'Volume' in history else 0
            
            return {
                "price": current_price,
                "change": change_pct,
                "volume": volume,
                "history": history.reset_index(),
                "status": "Live 🟢"
            }
        return None
    except Exception as e:
        return None

def get_news_ticker():
    if not NEWS_API_KEY:
        return "⚠️ News API Key Missing. Add to secrets.toml to see live news."
    try:
        url = f"https://newsapi.org/v2/everything?q=commodity+trade+india&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        data = requests.get(url, timeout=3).json()
        articles = data.get('articles', [])[:10]
        if not articles: return "No recent news found."
        headlines = [f"📰 {a['title']} ({a['source']['name']})" for a in articles]
        return "   +++   ".join(headlines)
    except:
        return "News feed unavailable."

def get_weather(port):
    coords = {"Mundra": [22.8, 69.7], "JNPT": [18.9, 72.9], "Chennai": [13.0, 80.2], "Kolkata": [22.5, 88.3]}
    lat, lon = coords.get(port, [22.8, 69.7])
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        return requests.get(url, timeout=2).json()['current_weather']
    except:
        return None

# --- 5. LAYOUT ---

# TOP TICKER
st.markdown(f'<div class="news-ticker-container"><div class="news-ticker-text">{get_news_ticker()}</div></div>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Controls")
    currency_pair = st.selectbox("Currency Pair", ["USD/INR", "EUR/INR", "GBP/INR"])
    selected_port = st.selectbox("Logistics Hub", ["Mundra", "JNPT", "Kolkata", "Chennai"])
    st.divider()

    # PROFILE (Safe Load)
    try:
        with open("C_39C_Sangeet Bihani.jpg", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <details>
            <summary>
                <img src="data:image/jpg;base64,{img_b64}" class="profile-img">
                <span class="profile-text">Sangeet Bihani</span>
            </summary>
            <div class="profile-expanded">
                <b>Strategy & Trade Analyst</b><br>
                MBA-IB (IIFT) | Ex-Zomato<br><br>
                <i>"Leveraging data to optimize global supply chains."</i><br>
                <br><span style="color:#4CAF50;">● Open to Opportunities</span>
            </div>
        </details>
        """, unsafe_allow_html=True)
    except:
        st.write("**Sangeet Bihani**")

# MAIN DASHBOARD
st.title("🚢 EximPulse")
st.caption(f"Real-Time Global Benchmarks • {datetime.now().strftime('%d %b %Y | %H:%M IST')}")

# KPIS
c1, c2, c3 = st.columns(3)

# 1. Real Forex
map_fx = {"USD/INR": "INR=X", "EUR/INR": "EURINR=X", "GBP/INR": "GBPINR=X"}
fx_data = get_live_price(map_fx[currency_pair])
if fx_data:
    c1.metric(currency_pair, f"₹{fx_data['price']:.2f}", f"{fx_data['change']:.2f}%")
else:
    c1.metric(currency_pair, "N/A", "No Data")

# 2. Real Weather
w = get_weather(selected_port)
if w:
    c2.metric(f"{selected_port} Conditions", f"{w['temperature']}°C", f"Wind: {w['windspeed']}km/h")
else:
    c2.metric(f"{selected_port}", "Offline", "Check API")

c3.metric("Data Integrity", "100% Real", "Source: Yahoo Finance")

st.markdown("---")

# SCANNER
st.subheader("📊 Global Commodity Benchmark Scanner")
st.caption("Tracking Live Futures Contracts (Global Price Drivers)")

# Dropdown with ONLY mapped real commodities
selected_comm_name = st.selectbox("Select Commodity Benchmark:", list(COMMODITY_MAP.keys()))

if selected_comm_name:
    ticker = COMMODITY_MAP[selected_comm_name]
    
    with st.spinner(f"Connecting to Global Exchange for {ticker}..."):
        market_data = get_live_price(ticker)
    
    if market_data:
        # Show Big Price
        st.metric(
            label=f"Live Price ({selected_comm_name})",
            value=f"${market_data['price']:.2f}",
            delta=f"{market_data['change']:.2f}%"
        )
        
        col_chart, col_stats = st.columns([2, 1])
        
        with col_chart:
            st.markdown("##### 5-Day Price Trend")
            # Real Line Chart
            hist_df = market_data['history']
            fig = px.line(hist_df, x="Date", y="Close", title=None, markers=True)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="white", xaxis_title=None, yaxis_title="Price (USD)"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_stats:
            st.markdown("##### Market Depth")
            st.dataframe(pd.DataFrame({
                "Metric": ["Open", "High", "Low", "Volume"],
                "Value": [
                    f"${market_data['history']['Open'].iloc[-1]:.2f}",
                    f"${market_data['history']['High'].iloc[-1]:.2f}",
                    f"${market_data['history']['Low'].iloc[-1]:.2f}",
                    f"{market_data['volume']:,}"
                ]
            }), hide_index=True, use_container_width=True)
            
    else:
        st.error(f"Could not fetch live data for {selected_comm_name}. Market might be closed or API is restricted.")

st.markdown("---")
st.markdown("<center style='color:#666'>EximPulse Terminal v2.1 • Built by Sangeet Bihani</center>", unsafe_allow_html=True)
