import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL", layout="wide")

if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 2. CSS - ESTILO TERMINAL
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 850px !important; margin: auto; }
    
    .main-title { font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 15px; }
    
    .asset-row { display: flex; gap: 20px; margin-bottom: 4px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 130px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    
    /* Estilo para a linha do Pré-Mercado */
    .pre-row { display: flex; gap: 20px; margin-bottom: 12px; align-items: center; margin-left: 10px; }
    .pre-name { width: 150px; font-size: 12px; color: #FFB900; font-weight: bold; }
    .pre-price { width: 130px; font-size: 14px; color: #EEE; }
    .pre-var { font-size: 14px; font-weight: bold; }

    .price-paridade { color: #FFB900 !important; }
    .price-ptax { color: #00FFFF !important; }
    
    .frp-box { margin-left: 180px; margin-top: -5px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 2px; }
    .frp-item { display: flex; gap: 25px; font-size: 13px; font-weight: 400 !important; }
    
    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
    .stPopover button { background-color: #111 !important; color: #666 !important; border: 1px solid #222 !important; font-size: 10px !important; height: 25px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFACE
st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

with st.popover("⚙️ AJUSTAR PARÂMETROS"):
    val_aj_manual = st.number_input("AJUSTE MANUAL", value=5.3900, format="%.4f", step=0.0001)
    val_ptax_manual = st.number_input("VALOR PTAX", value=5.3850, format="%.4f", step=0.0001)
    st.divider()
    v_max = st.number_input("PTS MÁXIMA", value=42.0)
    v_jus = st.number_input("PTS JUSTO", value=31.0)
    v_min = st.number_input("PTS MÍNIMA", value=22.0)

def get_market_data(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        return {
            "last": info.last_price,
            "prev": info.previous_close,
            "change": ((info.last
