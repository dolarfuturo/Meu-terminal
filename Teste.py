import streamlit as st
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import hashlib

st.set_page_config(page_title="SHARK VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

def verificar_acesso():
    URL_SISTEMA = "https://docs.google.com/spreadsheets/d/1m86_Lj5p7tV9U4sNIKudbU1DVWFgAfaSXSIRATo6G70/export?format=csv"
    CHAVE_MESTRA_ADM = "SHARK_ADM_2026" 
    
    if "autenticado" not in st.session_state:
        st.markdown("<h1 style='text-align:center; color:#D4AF37; font-family:monospace;'>SHAKE VISION LOGIN</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            chave = st.text_input("", type="password", placeholder="Digite a Chave...")
        
        if chave:
            if chave == CHAVE_MESTRA_ADM:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = "ADMINISTRADOR"
                st.session_state["role"] = "admin"
                st.rerun()
            try:
                df = pd.read_csv(URL_SISTEMA)
                hash_tentativa = hashlib.sha256(chave.encode()).hexdigest()
                df.columns = df.columns.str.strip()
                df['HASH_SENHA'] = df['HASH_SENHA'].astype(str).str.strip()
                df['STATUS'] = df['STATUS'].astype(str).str.strip()
                valido = df[(df['HASH_SENHA'] == hash_tentativa) & (df['STATUS'] == 'ATIVO')]
                if not valido.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = valido.iloc[0]['CLIENTE']
                    st.session_state["role"] = "user"
                    st.rerun()
                else: st.error("❌ Chave incorreta.")
            except: st.error("Validando...")
        st.stop()

verificar_acesso()

if st.session_state.get("role") == "admin":
    st.markdown("<style>#MainMenu {visibility: visible !important;} header {visibility: visible !important;}</style>", unsafe_allow_html=True)

COINS_CONFIG = {
    "BTC-USD": {"label": "BTC/USDT", "dec": 0}, 
    "ETH-USD": {"label": "ETH/USDT", "dec": 0},
    "SOL-USD": {"label": "SOL/USDT", "dec": 2}, 
    "XRP-USD": {"label": "XRP/USDT", "dec": 3},
    "BNB-USD": {"label": "BNB/USDT", "dec": 2}, 
    "DOGE-USD": {"label": "DOGE/USDT", "dec": 4},
    "LINK-USD": {"label": "LINK/USDT", "dec": 3}, 
    "ADA-USD": {"label": "ADA/USDT", "dec": 3},
    "AVAX-USD": {"label": "AVAX/USDT", "dec": 2}, 
    "DOT-USD": {"label": "DOT/USDT", "dec": 2},
    "MATIC-USD": {"label": "MATIC/USDT", "dec": 3}, 
    "PEPE-USD": {"label": "PEPE/USDT", "dec": 6},
    "SUI-USD": {"label": "SUI/USDT", "dec": 2}, 
    "NEAR-USD": {"label": "NEAR/USDT", "dec": 2},
    "APT-USD": {"label": "APT/USDT", "dec": 2}, 
    "OP-USD": {"label": "OP/USDT", "dec": 3},
    "ARB-USD": {"label": "ARB/USDT", "dec": 3}, 
    "INJ-USD": {"label": "INJ/USDT", "dec": 2},
    "RNDR-USD": {"label": "RNDR/USDT", "dec": 3}, 
    "HYPE-USD": {"label": "HYPE/USDT", "dec": 3}
}

def get_calculation_date():
    br_tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(br_tz)
    if now.weekday() == 5: return now - timedelta(days=1)
    if now.weekday() == 6
