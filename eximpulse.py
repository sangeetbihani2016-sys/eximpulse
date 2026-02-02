import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import requests
import base64
import random
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="EximPulse | Trade Command Center", 
    layout="wide", 
    page_icon="🚢"
)

# --- 1. SECURE KEY LOADER ---
try:
    NEWS_API_KEY = st.secrets["general"]["news_api_key"]
except:
    NEWS_API_KEY = ""

# --- 2. CUSTOM CSS (PREMIUM DARK THEME) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #0E1117; }
    
    /* SCROLLING TICKER - SLOWED DOWN TO 90s */
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
        animation: marquee 90s linear infinite; /* CHANGED FROM 35s TO 90s */
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 14px;
    }
    @keyframes marquee {
        0%   { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    
    /* INSTAGRAM STYLE PROFILE */
    details > summary {
        list-style: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 10px;
        border-radius: 50px;
        transition: background 0.3s;
        border: 1px solid #333;
        background: #161920;
    }
    details > summary:hover {
        border-color: #4CAF50;
        background: #1F2329;
    }
    .profile-img {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #4CAF50;
    }
    .profile-text {
        font-weight: bold;
        color: white;
        font-size: 16px;
    }
    .profile-expanded {
        margin-top: 10px;
        padding: 15px;
        background: #1c2029;
        border-radius: 10px;
        border-left: 3px solid #4CAF50;
        font-size: 13px;
        color: #cfcfcf;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA FUNCTIONS ---

@st.cache_data(ttl=600)
def get_market_data(ticker):
    try:
        mapping = {"USD/INR": "INR=X", "EUR/INR": "EURINR=X", "GBP/INR": "GBPINR=X"}
        symbol = mapping.get(ticker, ticker)
        data = yf.Ticker(symbol).history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            change = ((price - data['Open'].iloc[0]) / data['Open'].iloc[0]) * 100
            return price, change
        return 0.0, 0.0
    except:
        return 0.0, 0.0

def get_news_ticker():
    # If API fails or key is missing, show default scrolling text
    default_news = "MARKET UPDATE: Exports surge 15% • Gold stabilizes at $2030 • USD/INR touches 83.4 • Wheat export ban review next week"
    if not NEWS_API_KEY:
        return default_news
    try:
        url = f"https://newsapi.org/v2/everything?q=economy+india&apiKey={NEWS_API_KEY}"
        data = requests.get(url, timeout=2).json()
        articles = data.get('articles', [])[:8]
        if not articles: return default_news
        headlines = [f"📰 {a['title']} ({a['source']['name']})" for a in articles]
        return "   +++   ".join(headlines)
    except:
        return default_news

def get_weather(port):
    coords = {"Mundra": [22.8, 69.7], "JNPT": [18.9, 72.9], "Chennai": [13.0, 80.2], "Kolkata": [22.5, 88.3]}
    lat, lon = coords.get(port, [22.8, 69.7])
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        return requests.get(url, timeout=2).json()['current_weather']
    except:
        return None

def get_mandi_data(comm):
    # Simulated "Bloomberg" Level Data
    data = []
    states = ["Gujarat", "Maharashtra", "Punjab", "Haryana", "Madhya Pradesh"]
    base = 2200 if "Wheat" in comm else (6000 if "Cotton" in comm else 1500)
    
    for state in states:
        price = base + random.randint(-150, 300)
        dod = round(random.uniform(-2.5, 3.5), 2) # Day over Day change
        vol = random.randint(50, 600)
        
        data.append({
            "State": state,
            "Price (₹/Qtl)": price,
            "DoD Change %": dod,
            "Vol (MT)": vol,
            "Trend": "Bullish 🟢" if dod > 0 else "Bearish 🔴"
        })
    return pd.DataFrame(data)

# --- 4. LAYOUT BUILD ---

# TOP TICKER
st.markdown(f'<div class="news-ticker-container"><div class="news-ticker-text">{get_news_ticker()}</div></div>', unsafe_allow_html=True)

# SIDEBAR (With Safe Image Loader)
with st.sidebar:
    st.header("⚙️ Controls")
    currency_pair = st.selectbox("Currency Pair", ["USD/INR", "EUR/INR", "GBP/INR"])
    selected_port = st.selectbox("Logistics Hub", ["Mundra", "JNPT", "Kolkata", "Chennai"])
    st.divider()

    # PROFILE SECTION (SAFETY LOGIC)
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
        st.error("⚠️ Image not found. Check filename.")
        st.write("**Sangeet Bihani**")
        st.caption("MBA-IB (IIFT) | Ex-Zomato")

# MAIN DASHBOARD
st.title("🚢 EximPulse")
st.caption(f"Real-Time Trade Intelligence • {datetime.now().strftime('%d %b %Y | %H:%M IST')}")

# METRICS
c1, c2, c3 = st.columns(3)
p, c = get_market_data(currency_pair)
w = get_weather(selected_port)

c1.metric(currency_pair, f"₹{p:.2f}", f"{c:.2f}%")
if w:
    c2.metric(f"{selected_port} Weather", f"{w['temperature']}°C", f"Wind: {w['windspeed']}km/h")
else:
    c2.metric(f"{selected_port}", "N/A", "Offline")
c3.metric("System Status", "Online 🟢", "Secure")

st.markdown("---")

# SCANNER
st.subheader("📊 Domestic Market Scanner")
comm_list = ["Wheat", "Rice Basmati", "Cotton S-6", "Soybean", "Turmeric"]
selected_comm = st.selectbox("Select Asset Class:", comm_list)

if selected_comm:
    df = get_mandi_data(selected_comm)
    
    col_table, col_chart = st.columns([4, 6])
    
    with col_table:
        st.markdown("##### 📋 Regional Spot Rates")
        
        # ERROR HANDLING FOR GRADIENT:
        # If matplotlib is missing, it will fallback to a plain table instead of crashing
        try:
            st.dataframe(
                df.style.background_gradient(subset=["Price (₹/Qtl)"], cmap="Greens"),
                use_container_width=True,
                hide_index=True
            )
        except ImportError:
            # Fallback if pip install matplotlib wasn't run
            st.warning("⚠️ For premium coloring: run 'pip install matplotlib' in terminal.")
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.dataframe(df, use_container_width=True, hide_index=True)
        
    with col_chart:
        st.markdown(f"##### 📈 Price vs Volume ({selected_comm})")
        fig = px.bar(
            df, x="State", y="Price (₹/Qtl)",
            color="Vol (MT)", color_continuous_scale="Tealgrn",
            text="Price (₹/Qtl)"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="white", margin=dict(l=0,r=0,t=0,b=0),
            yaxis=dict(showgrid=True, gridcolor="#333")
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("<center style='color:#666'>EximPulse Terminal v2.1 • Built by Sangeet Bihani</center>", unsafe_allow_html=True)
