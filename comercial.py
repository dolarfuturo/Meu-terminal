import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

# SENHAS
SENHA_ADMIN = "admin123"
SENHA_CLIENTE = "cliente123"

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.perfil = None
if 'v_ajuste' not in st.session_state: st.session_state.v_ajuste = 5.4000
if 'ref_base' not in st.session_state: st.session_state.ref_base = 5.4000
if 'aviso_mercado' not in st.session_state: st.session_state.aviso_mercado = "SEM NOTÍCIAS DE IMPACTO NO MOMENTO"

if not st.session_state.autenticado:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    senha = st.text_input("CHAVE:", type="password")
    if st.button("ACESSAR"):
        if senha == SENHA_ADMIN:
            st.session_state.autenticado = True
            st.session_state.perfil = "admin"
            st.rerun()
        elif senha == SENHA_CLIENTE:
            st.session_state.autenticado = True
            st.session_state.perfil = "cliente"
            st.rerun()
    st.stop()

# 2. ESTILO CSS
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700;800&display=swap'); * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; } .stApp { background-color: #000000; color: #FFFFFF; } header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; } .block-container { padding-top: 0.5rem !important; max-width: 850px !important; margin: auto; padding-bottom: 80px; } [data-testid="stPopover"] { position: fixed; top: 10px; right: 10px; opacity: 0; z-index: 10000; } .status-badge { font-size: 10px; padding: 2px 8px; border-radius: 3px; font-weight: 800; margin-left: 10px; } .status-caro { background-color: #FF4B4B; color: white; } .status-barato { background-color: #00FF80; color: black; } .status-neutro { background-color: #333; color: white; } .pressure-bg { width: 100%; height: 4px; background: #111; margin-top: 5px; border-radius: 2px; overflow: hidden; } .pressure-fill { height: 100%; transition: width 0.5s ease; } .terminal-header { text-align: center; font-size: 14px; letter-spacing: 8px; color: #333; border-bottom: 1px solid #111; padding-bottom: 10px; margin-bottom: 20px; } .dolar-strong { color: #FFFFFF; font-weight: 800; } .data-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 0; border-bottom: 1px solid #111; } .data-label { font-size: 11px; color: #FFFFFF; font-weight: 700; letter-spacing: 2px; width: 35%; } .data-value { font-size: 32px; font-weight: 700; width: 65%; text-align: right; } .sub-grid { display: flex; gap: 25px; justify-content: flex-end; width: 65%; } .sub-item { text-align: right; min-width: 105px; } .sub-label { font-size: 10px; color: #FFFFFF !important; display: block; margin-bottom: 4px; font-weight: 800; } .sub-val
