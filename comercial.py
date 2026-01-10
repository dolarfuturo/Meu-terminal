import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL ARBITRAGEM PRO", layout="wide")

if 'spot_10h' not in st.session_state:
    st.session_state.spot_10h = 0.0

# 2. ESTILO CSS COM ALERTAS PISCANTES
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 500px !important; margin: auto; }
    
    .section-title { font-size: 12px; color: #555; border-bottom: 1px solid #222; padding-bottom: 5px; margin: 15px 0 10px 0; letter-spacing: 1px; }
    
    /* ALERTAS */
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .alerta-max { background: #FF0000; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; animation: blink 0.8s infinite; margin-bottom: 10px; }
    .alerta-min { background: #00FF00; color: black; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; animation: blink 0.8s infinite; margin-bottom: 10px; }
    
    .spot-box { text-align: center; padding: 15px; border: 1px solid #333; border-radius: 8px; margin-bottom: 20px; background: #080808; }
    .box-container { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 10px; }
    .box { background:
