import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO E ESTADO
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_global_vars():
    return {"ajuste": 5.4000, "ref": 5.4000, "v_min": 1.0020, "v_jus": 1.0041, "v_max": 1.0060, "notas": "OPERACIONAL ATIVO"}

v_global = get_global_vars()

# 2. LOGIN SIMPLIFICADO (PARA EVITAR ERROS DE INDENTAÇÃO)
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    senha = st.text_input("CHAVE", type="password")
    if st.button("ENTRAR"):
        if senha == "admin123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. MOTOR DE DADOS
def get_clean_data(ticker):
    try:
        t = yf.Ticker(ticker)
        return {"last": t.fast_info.last_price, "prev": t.fast_info.previous_close, "var": ((t.fast_info.last_price - t.fast_info.previous_close) / t.fast_info.previous_close * 100)}
    except: return {"last": 0.0, "prev": 0.0, "var": 0.0}

# 4. INTERFACE PRINCIPAL
@st.fragment(run_every=2)
def monitor_terminal():
    d_m, e_m, s_m = get_clean_data("DX-Y.NYB"), get_clean_data("EWZ"), get_clean_data("BRL=X")
    
    # LÓGICA DE PROTEÇÃO (MATAR O 5.1604)
    agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
    prev_close = s_m["prev"]
    raw_spot = s_m["last"]
    
    # Se divergir mais de 0.15 do ajuste, usa o fechamento (5.1956)
    if (agora.hour >= 18) or (abs(raw_spot - v_global["ajuste"]) > 0.15):
        spot = prev_close
    else:
        spot = raw_spot

    v_spot = ((spot - prev_close) / prev_close * 100) if prev_close != 0 else 0
    cor = "#00ff00" if v_spot >= 0 else "#ff4b4b"
    
    # CÁLCULOS
    spr = d_m["var"] - e_m["var"]
    paridade = v_global["ajuste"] * (
