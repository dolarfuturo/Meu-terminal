import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO E ACESSO
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

# SENHAS (Ajusta conforme preferires)
SENHA_ADMIN = "admin123"
SENHA_CLIENTE = "cliente123"

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.perfil = None

if not st.session_state.autenticado:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    st.title("🔒 ACESSO AO TERMINAL")
    senha = st.text_input("INSIRA SUA CHAVE:", type="password")
    if st.button("ENTRAR"):
        if senha == SENHA_ADMIN:
            st.session_state.autenticado = True
            st.session_state.perfil = "admin"
            st.rerun()
        elif senha == SENHA_CLIENTE:
            st.session_state.autenticado = True
            st.session_state.perfil = "cliente"
            st.rerun()
        else:
            st.error("CHAVE INVÁLIDA")
    st.stop()

if 'v_ajuste' not in st.session_state: st.session_state.v_ajuste = 5.4000
if 'ref_base' not in st.session_state: st.session_state.ref_base = 5.4000

# 2. ESTILO CSS (ENGRENAGEM TRANSPARENTE NO TOPO)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700;800&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 0.5rem !important; max-width: 850px !important; margin: auto; padding-bottom: 80px; }
    
    /* CONFIGURAÇÃO DA ENGRENAGEM FANTASMA NO TOPO DIREITO */
    [data-testid="stPopover"] { 
        position: fixed; 
        top: 10px; 
        right: 10px; 
        opacity: 0; /* Totalmente transparente */
        transition: opacity 0.3s; 
        z-index: 10000; 
    }
    /* Torna-se levemente visível ao passar o rato (para tu te orientares) */
    [data-testid="stPopover"]:hover { 
        opacity: 0.2; 
    }
    
    .terminal-header { text-align: center; font-size: 14px; letter-spacing: 8px; color: #333; border-bottom: 1px solid #111; padding-bottom: 10px; margin-bottom: 20px; }
    .dolar-strong { color: #FFFFFF; font-weight: 800; }
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 0; border-bottom: 1px solid #111; }
    .data-label { font-size: 11px; color: #FFFFFF; font-weight: 700; letter-spacing: 2px; width: 35%; }
    .data-value { font-size: 32px; font-weight: 700; width: 65%; text-align: right; }
    .sub-grid { display: flex; gap: 25px; justify-content: flex-end; width: 65%; }
    .sub-item { text-align: right; min-width: 105px; }
    .sub-label { font-size: 9px; color: #444; display: block; margin-bottom: 4px; font-weight: 700; }
    .sub-val { font-size: 24px; font-weight: 700; }
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    .footer-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 40px; background: #080808; border-top: 1px solid #222; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; font-size: 11px; z-index: 9999; }
    .ticker-wrap { flex-grow: 1; overflow: hidden; white-space: nowrap; margin: 0 30px; }
    .ticker { display: inline-block; animation: marquee 35s linear infinite; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-250%); } }
    .up { color: #00FF80; } .down { color: #FF4B4B
