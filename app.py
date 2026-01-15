Import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DO TERMINAL
st.set_page_config(page_title="TERMINAL", layout="wide")

# 2. ESTILO CSS (DARK MODE)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin: auto; }
    .main-title { font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 15px; }
    .asset-row { display: flex; gap: 20px; margin-bottom: 4px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 130px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    
    /* LINHA EXCLUSIVA PRÉ-MERCADO */
    .pre-row { display: flex; gap: 20px; margin-bottom: 12px; align-items: center; margin-left: 20px; border-left: 2px solid #333; padding-left: 10px; }
    .pre-name { width: 140px; font-size: 12px; color: #FFB900; font-weight: bold; }
    .pre-price { width: 130px; font-size: 14px; color: #BBB; }
    .pre-var { font-size: 14px; font-weight: bold; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
    .frp-box { margin-left: 180px; margin-top: -5px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 2px; }
    .frp-item { display: flex; gap: 25px; font-size: 13px; }
    .stPopover button { background-color: #111 !important; color: #666 !important; border: 1px solid #222 !important; font-size: 10px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

# 3. INPUTS
with st.popover("⚙️ AJUSTAR PARÂMETROS"):
    v_aj = st.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_ptax_m = st.number_input("PTAX", value=5.3850, format="%.4f")
