import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="BLOOMBERG LIVE | EWZ PRE-MARKET", layout="wide")

# 2. Memória da Sessão
if 'history' not in st.session_state: st.session_state.history = []
if 'spot_ref_locked' not in st.session_state: st.session_state.spot_ref_locked = None

refresh_interval = 2 

# 3. Estilo Visual Bloomberg
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #FFB900 !important; font-family: 'Courier New', monospace; font-size: 28px !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase; }
    .frp-box { border: 1px solid #333333; padding: 15px; background-color: #000000; text-align: center; }
    .spread-box { border: 1px dashed #555555; padding: 10px; background-color: #111111; text-align: center; margin-bottom: 10px; margin-top: 10px; }
    .price-text { font-size: 26px; font-family: 'Courier New'; font-weight: bold; }
    .pre-market-card { border: 2px solid #0080FF !important; border-radius: 5px; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 4. Menu Lateral
with st.sidebar.expander("⚙️ AJUSTAR PONTOS FRP", expanded=True):
    v_min = st.number_input("Mínima FRP", value=22.0)
    v_justo = st.number_input("Justo FRP", value=31.0)
    v_max = st.number_input("Máxima FRP", value=42.0)

def get_live_data(ticker):
    try:
        # Buscamos dados do dia anterior para o fechamento e pre-market
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data if not data.empty else pd.DataFrame()
    except: return pd.DataFrame()

placeholder = st.empty()

with placeholder.container():
    full_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    # Ajuste de Hora para Brasília
    now_br = datetime.now() - timedelta(hours=3)
    hora_br_str = now_br.strftime("%H:%M:%S")

    if not full_df.empty:
        spot_at = float(full_df['Close'].iloc[-1])
        
        # Trava 16h (original Yahoo)
        try:
            lock_data = full_df.between_time('15:58', '16:02')
