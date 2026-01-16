import streamlit as st
import yfinance as yf
import time

# 1. SETUP
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. VARIÁVEIS
if 'ptax' not in st.session_state: st.session_state.ptax = 5.4000
if 'fech' not in st.session_state: st.session_state.fech = 5.4000
if 'ref' not in st.session_state: st.session_state.ref = 5.4000
if 'ajuste' not in st.session_state: st.session_state.ajuste = 5.4000
if 'auth' not in st.session_state: st.session_state.auth = False

# 3. LOGIN
if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'] { display: none; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:120px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("CHAVE", type="password")
        if st.button("ENTRAR"):
            if senha == "admin123": st.session_state.auth = True; st.rerun()
    st.stop()

# 4. SIDEBAR (ENGRENAGEM PARA VARIÁVEIS)
with st.sidebar:
    st.header("⚙️ VARIÁVEIS")
    st.session_state.ptax = st.number_input("PTAX", value=st.session_state.ptax, format="%.4f")
    st.session_state.fech = st.number_input("FECHAMENTO", value=st.session_state.fech, format="%.4f")
    st.session_state.ref = st.number_input("REF. INST", value=st.session_state.ref, format="%.4f")
    st.session_state.ajuste = st.number_input("PARIDADE", value=st.session_state.ajuste, format="%.4f")
    if st.button("SALVAR"): st.rerun()

# 5. CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; overflow: hidden; }
    
    .t-header { text-align: center; padding-top: 10px; }
    .t-title { font-size: 22px; letter-spacing: 5px; font-weight: 300; text-transform: uppercase; }
    .t-bold { font-weight: 900; }
    .t-line { width: 60%; height: 1px; background: #333; margin: 5px auto 15px auto; }
    
    /* VELOCÍMETRO */
    .gauge-container { position: relative; width: 160px; height: 80px; margin: 0 auto; overflow: hidden; }
    .gauge-bg { position: absolute; top: 0; left: 0; width: 160px; height: 160px; border-radius: 50%; background: conic-gradient(#ff3333 0deg 60deg, #ffff00 60deg 120deg, #00ff88 120deg 180deg, #000 180deg); transform: rotate(-90deg); }
