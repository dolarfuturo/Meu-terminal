import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# Configuração Ultra-Slim para Split-Screen
st.set_page_config(page_title="Monitor Side Pro", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    .stApp { background-color: #000000 !important; }
    .block-container { padding: 0.1rem !important; }
    
    .frp-monitor {
        font-family: 'JetBrains Mono', monospace; background-color: #1a1a1a;
        color: #00FF66; font-size: 11px; text-align: center;
        padding: 4px; border-radius: 4px; border: 1px solid #333; margin-bottom: 5px;
    }
    .custom-row { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid #1a1a1a; padding: 4px 0; }
    .c-label { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #ff9900; font-weight: bold; }
    .c-value { font-family: 'Share Tech Mono', monospace; font-size: 21px; color: #ffffff; }
    .c-delta { font-size: 12px; margin-left: 5px; font-weight: bold; }
    
    .fut { color: #FFFF00 !important; }
    .max { color: #00FF66 !important; }
    .min { color: #FF0033 !important; }
    .pos { color: #00FF66; }
    .neg { color: #FF0033; }
    
    .header-box { font-family: 'JetBrains Mono', monospace; color: #FFFFFF; font-size: 12px; text-align: center; border-bottom: 1px solid #333; padding: 3px 0; margin-top: 5px;}
    
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; border-top: 2px solid #FFFFFF; position: fixed; bottom: 0; left: 0; padding: 10px 0; height: 50px; z-index: 999; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 15s linear infinite; font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #FFFFFF; font-weight: bold; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style
