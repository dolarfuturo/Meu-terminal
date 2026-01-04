import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Terminal Side Pro", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    .stApp { background-color: #000000 !important; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }
    
    /* Monitor de FRP no Topo */
    .frp-monitor {
        font-family: 'JetBrains Mono', monospace;
        background-color: #1a1a1a;
        color: #00FF66;
        font-size: 11px;
        text-align: center;
        padding: 2px;
        border-radius: 4px;
        margin-bottom: 10px;
        border: 1px solid #333;
    }

    .row {
        display: flex; justify-content: space-between; align-items: baseline;
        border-bottom: 1px solid #1a1a1a; padding: 4px 0; margin-bottom: 2px;
    }
    .label {
        font-family: 'JetBrains Mono', monospace; font-size: 13px;
        color: #ff9900; text-transform: uppercase; font-weight: bold;
    }
    .value {
        font-family: 'Share Tech Mono', monospace; font-size: 21px; color: #ffffff;
    }
    .delta { font-size: 12px; margin-left: 6px; font-weight: bold; }
    
    .futuro { color: #FFFF00 !important; }
    .max { color: #00FF66 !important; }
    .min { color: #FF0033 !important; }
    .pos { color: #00FF66; }
    .neg { color: #FF0033; }

    .header-box {
        font-family: 'JetBrains Mono', monospace; color: #FFFFFF; font-size: 13px;
        text-align: center; border-bottom: 1px solid #333; padding: 4px 0; margin-bottom: 5px;
    }

    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; border-top: 2px solid #FFFFFF;
        position: fixed; bottom: 0; left: 0; padding: 10px 0; height: 55px; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 15s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 15px; color: #FFFFFF; font-weight: bold;
    }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
    """, unsafe_allow_html=True)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d")
        if not df.empty:
            p = df['Close'].iloc[-1]
            h = df['High'].iloc[-1]
            l = df['Low'].iloc[-1]
            prev = t.info.get('previousClose', p)
            v = ((p - prev) / prev) * 100
            return p, v, h, l
    except: return 0.0, 0.0, 0.0, 0.0
    return 0.0, 0.0, 0.0, 0.0

# --- INTERFACE ---
st.markdown("<div class='header-box'>🏛️ CÂMBIO</div>", unsafe_allow_html=True)

# Configurações
with st.expander("SET"):
    frp_input = st.number_input("FRP (Pontos)", value=0.0150, step=0.0001, format="%.4f")
    aju_input = st.number_input("AJUSTE B3", value
