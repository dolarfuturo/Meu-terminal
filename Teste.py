import streamlit as st
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import hashlib

# 1. SETUP ALPHA & TRAVA DE SEGURANÇA 
st.set_page_config(page_title="SHARK VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

# CSS MANTIDO INTEGRALMENTE
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }

    /* TRAVA O CABEÇALHO NO TOPO */
    [data-testid="stVerticalBlock"] > div:first-child {
        position: sticky;
        top: 0;
        z-index: 999999;
        background-color: #000000;
        border-bottom: 2px solid #D4AF37;
    }

    /* PONTO VERDE PISCANDO (GLOW) CORRIGIDO */
    .dot { 
        height: 12px !important; 
        width: 12px !important; 
        background-color: #00FF00 !important; 
        border-radius: 50% !important; 
        display: inline-block !important;
        box-shadow: 0 0 10px #00FF00 !important;
        animation: pulse-glow 1s infinite alternate !important;
        margin-right: 8px !important;
    }
    @keyframes pulse-glow {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0.2; transform: scale(0.8); }
    }

    .title-gold { color: #D4AF37; font-size: 26px; font-weight: 900; text-align: center; margin: 5px 0; }
    .header-grid { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; background: #080808; padding: 10px 0; }
    .h-col { font-size: 9px; color: #FFF; text-align: center; font-weight: bold; }
    .row-container { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; align-items: center; padding: 12px 0; border-bottom: 1px solid #222; }
    .w-col { text-align: center; font-family: monospace; font-size: 15px; font-weight: bold; color: #FFF; }
    .vision-block { display: flex; justify-content: center; gap: 30px; padding: 5px 0; background: #050505; border-bottom: 2px solid #333; }
    
    /* BOTÃO CUSTOMIZADO */
    div.stButton > button {
        background-color: #D4AF37;
        color: black;
        font-weight: bold;
        width: 100%;
        border-radius: 5px;
        border: none;
    }
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
            btn = st.button("ACESSAR TERMINAL CRYPTO")
        
        if btn and chave:
            if chave == CHAVE_MESTRA_ADM:
                st.session_state["autenticado"], st.session_state["usuario"], st.session_state["role"] = True, "ADMINISTRADOR", "admin"
                st.rerun()
            try:
                df = pd.read_csv(URL_SISTEMA)
                hash_t = hashlib.sha256(chave.encode()).hexdigest()
                df.columns = df.columns.str.strip()
                valido = df[(df['HASH_SENHA'].astype(str).str.strip() == hash_t) & (df['STATUS'].str.strip() == 'ATIVO')]
                
                if not valido.empty:
                    st.session_state["autenticado"], st.session_state["usuario"], st.session_state["role"] = True, valido.iloc[0]['CLIENTE'], "user"
                    st.rerun()
                else:
                    st.error("❌ Chave Inválida ou Expirada.")
            except:
                st.error("Aguarde conexão... CLIC acessar.")
        st.stop()

verificar_acesso()

COINS_CONFIG = {
    "BTC-USD": {"label": "BTC/USDT", "dec": 0}, "ETH-USD": {"label": "ETH/USDT", "dec": 0},
    "SOL-USD": {"label": "SOL/USDT", "dec": 3}, "XRP-USD": {"label": "XRP/USDT", "dec": 3},
    "BNB-USD": {"label": "BNB/USDT", "dec": 3}, "DOGE-USD": {"label": "DOGE/USDT", "dec": 3},
    "LINK-USD": {"label": "LINK/USDT", "dec": 3}, "ADA-USD": {"label": "ADA/USDT", "dec": 3},
    "AVAX-USD": {"label": "AVAX/USDT", "dec": 3}, "DOT-USD": {"label": "DOT/USDT", "dec": 3},
    "MATIC-USD": {"label": "MATIC/USDT", "dec": 3}, "PEPE-USD": {"label": "PEPE/USDT", "dec": 3},
    "SUI-USD": {"label": "SUI/USDT", "dec": 3}, "NEAR-USD": {"label": "NEAR/USDT", "dec": 3},
    "APT-USD": {"label": "APT/USDT", "dec": 3}, "OP-USD": {"label": "OP/USDT", "dec": 3},
    "ARB-USD": {"label": "ARB/USDT", "dec": 3}, "INJ-USD": {"label": "INJ/USDT", "dec": 3},
    "RNDR-USD": {"label": "RNDR/USDT", "dec": 3}, "HYPE-USD": {"label": "HYPE/USDT", "dec": 2}
}

def get_calculation_date():
    br_tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(br_tz)
    if now.weekday() == 5: return now - timedelta(days=1)
    if now.weekday() == 6: return now - timedelta(days=2)
    if now.weekday() == 0 and now.hour < 18: return now - timedelta(days=3)
    if now.hour < 18: return now - timedelta(days=1)
    return now

def get_alpha_midpoint(ticker):
    try:
        br_tz = pytz.timezone('America/Sao_Paulo')
        target_date = get_calculation_date()
        df = yf.download(ticker, start=target_date.strftime('%Y-%m-%d'), interval="1m", progress=False)
        if df.empty: return yf.Ticker(ticker).fast_info['last_price']
        df.index = df.index.tz_convert(br_tz)
        df_window = df.between_time('11:30', '18:00')
        if not df_window.empty:
            return (float(df_window['High'].max()) + float(df_window['Low'].min())) / 2
        return yf.Ticker(ticker).fast_info['last_price']
    except: return 0

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .top-header-fixed { position: sticky; top: 0; background: #
