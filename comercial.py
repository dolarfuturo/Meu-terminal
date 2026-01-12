import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# 1. CONFIGURAÇÃO BÁSICA
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_global_params():
    return {"ajuste": 5.4000, "ref": 5.4000}

params = get_global_params()

# 2. LOGIN SIMPLES
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.perfil = None

if not st.session_state.autenticado:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        senha = st.text_input("CHAVE DE ACESSO:", type="password")
        if st.button("ACESSAR TERMINAL"):
            if senha == "admin123":
                st.session_state.autenticado = True
                st.session_state.perfil = "admin"
                st.rerun()
            elif senha == "trader123":
                st.session_state.autenticado = True
                st.session_state.perfil = "cliente"
                st.rerun()
    st.stop()

# 3. CSS "LIMPO" (SEM ERROS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton {
        display: none !important;
    }
    
    .stApp { background-color: #000; color: #fff; font-family: 'Share Tech Mono', monospace !important; }
    
    .terminal-header { text-align: center; padding: 20px 0; border-bottom: 1px solid #222; }
    .bold-white { color: #fff; font-weight: 900; font-size: 18px; letter-spacing: 5px; }
    
    .status-badge { font-size: 12px; font-weight: bold; margin-top: 10px; letter-spacing: 2px; }
    
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 30px 15px; border-bottom: 1px solid #111; }
    .data-label { font-size: 11px; color: #888; width: 45%; }
    .data-value { font-size: 32px; width: 55%; text-align: right; font-weight: bold; }
    
    .sub-grid { display: flex; gap: 10px; justify-content: flex-end; width: 55%; }
    .sub-item { text-align: right; }
    .sub-label { font-size: 8px; color: #555; display: block; }
    .sub-val { font-size: 18px; font-weight: bold; }

    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    
    .footer-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 70px; 
        background: #050505; border-top: 1px solid #222; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
