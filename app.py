import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Configurações Iniciais
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="expanded")

# 2. Inicialização do Estado
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Estilo Terminal Puro
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header[data-testid="stHeader"] { visibility: hidden; display: none !important; }
    
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin-left: 20px; }

    /* Barra Lateral */
    [data-testid="stSidebar"] { background-color: #111111 !important; border-right: 1px solid #333; }

    .terminal-header {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 25px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }

    .asset-row { display: flex; gap: 20px; margin-bottom: 15px; align-items: center; }
    .name { width: 150px; font-size: 18px; color: #888; }
    .price { width: 110px; font-size: 18px; font-weight: bold; color: #FFFFFF; }
    .var { font-size: 18px; font-weight: bold; }
    .price-alvo { color: #FFB900 !important; }

    /* Bloco FRP Invertido */
    .frp-box {
        margin-left: 170px;
        margin-top: -5px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .frp-item { display: flex; gap: 25px; font-size: 18px; font-weight: bold; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    
    /* Trava em Laranja */
    .trava-text { color: #FF8C00 !important; font-size: 16px; margin-top: 15px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. VARIÁVEIS NA SIDEBAR (ESQUERDA)
with st.
