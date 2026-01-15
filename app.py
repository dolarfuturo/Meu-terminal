import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL DO DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
if 'ajuste' not in st.session_state:
    st.session_state.ajuste = 5.4000
    st.session_state.ref = 5.4000
    st.session_state.mural = ""

# ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'], label { display: none !important; } .stButton button { width: 100%; background-color: #222; color: white; border: 1px solid #444; margin-top: 20px; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:150px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="CHAVE DE ACESSO")
        if st.button("ENTRAR"):
            if senha == "admin123": st.session_state.auth, st.session_state.user_type = True, "ADM"; st.rerun()
            elif senha == "trader123": st.session_state.auth, st.session_state.user_type = True, "USER"; st.rerun()
    st.stop()

# 3. CSS - FOCO NO TÍTULO CENTRAL E TERMÔMETRO VISÍVEL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    /* HEADER CENTRALIZADO */
    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid #111; position: relative; }
    .t-title { color: #fff; font-size: 24px; letter-spacing: 6px; font-weight: 900; margin-bottom: 5px; }
    .spot-topo { font-family: 'Chakra Petch'; font-size: 20px; color: #888; margin-top: 5px; }

    /* TERMÔMETRO NEON CENTRAL */
    .thermo-box { width: 100%; display: flex; justify-content: center; margin-top: 10px; }
    .thermo-bg { width: 60%; height: 4px; background: #111; border-radius: 10px; position: relative; overflow: hidden; border: 1px solid #222; }
    .thermo-bar { height: 100%; transition: all 0.6s ease; border-radius: 10px; box-shadow: 0 0 15px currentColor; }
    
    .s-container { text-align: center; padding: 10px 0; border-bottom: 1px solid #111; }
    .s-text { font-size: 11px; font-weight: 700; letter-spacing: 2px; }
    
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; display: flex; flex-direction: column; }
    .sub-l { font-size: 8px; color: #888; margin-bottom: 2px; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .d-value { font-size: 24px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 50px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; }
    .tk-move { display: inline-block; animation: slide 45s linear infinite; white-space: nowrap; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_clean_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d", interval="1m")
        last = df['Close'].iloc[-1]
        var = ((last - t.fast_info.previous_close) / t.fast_info.previous_close * 100)
