import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
if "ajuste" not in st.session_state:
    st.session_state.ajuste = 5.4000
    st.session_state.ref = 5.4000
    st.session_state.fraldao = 15.0
    st.session_state.notas_mural = "AGUARDANDO ATUALIZAÇÃO..."

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:150px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("CHAVE DE ACESSO", type="password")
        if st.button("ENTRAR"):
            if senha == "admin123":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# 4. CSS DO TERMINAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .v-fut-discreto { font-size: 17px; color: #444; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .sub-grid { display: flex; gap: 30px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; display: flex; flex-direction: column; min-width: 80px; }
    .v-peq { font-size: 16px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .v-extra { font-size: 13px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; opacity: 0.4; margin-top: 2px; }

    .micro-container { text-align: right; padding: 0 15px 15px 0; font-family: 'Chakra Petch'; font-size: 10px; font-weight: 700; }
    @keyframes blinker { 50% { opacity: 0; } }
    .blink-text { animation: blinker 0.8s linear infinite; }
    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; min-height: 100px; }
</style>
""", unsafe_allow_html=True)

def get_data(ticker):
    try:
        d = yf.download(ticker, period="1d", interval="1m", progress=False)
        return float(d['Close'].iloc[-1]) if not d.empty else 0.0
    except: return 0.0

# 5. LOOP
ui_area = st.empty()
while True:
    spot = get_data("BRL=X")
    
    if spot > 0:
