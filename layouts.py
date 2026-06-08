import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime, timedelta
import pytz

# =============================================================================
# BLOCO 1: CONFIGURAÇÃO E CSS
# =============================================================================
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL K97", initial_sidebar_state="collapsed")
st.markdown("""<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; }
    .main-title { margin: 0px; line-height: 1.2; font-size: 28px; font-family: monospace; }
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-top: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table td, th { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 12px; }
</style>""", unsafe_allow_html=True)

# =============================================================================
# BLOCO 2: PERSISTÊNCIA (BLINDAGEM)
# =============================================================================
def get_arq(nome):
    data = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
    return f"{nome}_{data}.txt"

def salvar_estado(nome, valor):
    with open(get_arq(nome), "w") as f: f.write(str(valor))

def carregar_estado(nome):
    path = get_arq(nome)
    if os.path.exists(path):
        try:
            with open(path, "r") as f: return float(f.read())
        except: pass
    return None

if 'market_data' not in st.session_state: st.session_state.market_data = {}
if 'last_p' not in st.session_state: st.session_state.last_p = {}

# =============================================================================
# BLOCO 3: FETCH (MANTIDO)
# =============================================================================
def fetch(s):
    fallback = {"at": 0.0, "cl": 1.0, "op": 0.0, "mx": 0.0, "mn": 0.0}
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return st.session_state.market_data.get(s, fallback)
        m = 1000 if s == "USDBRL=X" else 1
        data = {"at": float(d['Close'].iloc[-1] * m), "cl": float(d['Close'].iloc[0] * m), "op": float(d['Open'].iloc[0] * m), "mx": float(d['High'].max() * m), "mn": float(d['Low'].min() * m)}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s, fallback)

# =============================================================================
# BLOCO 4: NÚCLEO MATEMÁTICO BLINDADO
# =============================================================================
def calcular_k97_total(spot_data):
    preco_spot = spot_data['at'] if spot_data['at'] > 100 else spot_data['at'] * 1000
    
    # Carrega estado do dia
    base = carregar_estado("base")
    delta = carregar_estado("delta")
    
    # Inicialização (se for o primeiro acesso do dia)
    if base is None:
        base = preco_spot
        delta = 0.0
        salvar_estado("base", base)
        salvar_estado("delta", delta)

    # Cálculo do Delta contínuo
    fracao_4s = (preco_spot - base) / 1000
    delta_atual = delta + fracao_4s
    
    # Persistência imediata
    salvar_estado("delta", delta_atual)
    
    return {
        "delta_spot_forca": delta_atual,
        "preco_base_atual": base / 1000,
        "vivo": preco_spot / 1000
    }

# =============================================================================
# BLOCO 6: LOOP PRINCIPAL
# =============================================================================
placeholder = st.empty()
while True:
    spot = fetch("USDBRL=X")
    res = calcular_k97_total(spot)
    
    with placeholder.container():
        st.markdown("### K97 TERMINAL")
        cor_delta = "#00ff88" if res['delta_spot_forca'] >= 0 else "#ff4d4d"
        
        st.markdown(f'''
        <div class="calc-panel">
            <div class="calc-row"><span>PREÇO BASE (FIXO)</span> <span>{res['preco_base_atual']:.4f}</span></div>
            <div class="calc-row"><span>𝚫 SPOT (FORÇA)</span> 
                <span style="color:{cor_delta}; font-weight:bold;">{res['delta_spot_forca']:+.4f}</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    time.sleep(4)
