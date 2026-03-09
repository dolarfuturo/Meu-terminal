import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - TERMINAL SINTÉTICO", layout="wide")

# --- MOTOR DE CÁLCULOS (SUA FÓRMULA EXATA) ---
def calcular_dolfut_k97(eixo_ewz, preco_ewz_atual, eixo_dolfut_manual):
    try:
        # 1. (EIXO / PREÇO - 1) * 100 / 2 = variação entre preço e eixo
        var_ewz = ((eixo_ewz / preco_ewz_atual) - 1) * 100 / 2
        # 2. DOLFUT = eixo do dol manual * (1 + variação)
        preco_sintetico = eixo_dolfut_manual * (1 + (var_ewz / 100))
        return preco_sintetico, var_ewz
    except:
        return eixo_dolfut_manual, 0.0

@st.cache_data(ttl=15)
def fetch_market_data():
    tickers = {"EWZ": "EWZ", "DXY": "DX-Y.NYB", "XAU": "GC=F"}
    res = {}
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1d")
            if not df.empty:
                res[name] = {
                    "price": df['Close'].iloc[-1],
                    "max": df['High'].iloc[-1],
                    "min": df['Low'].iloc[-1],
                    "open": df['Open'].iloc[-1]
                }
        except: res[name] = {"price": 0, "max": 0, "min": 0, "open": 0}
    return res

# --- ESTILIZAÇÃO K97 ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black'; font-size: 28px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black'; font-size: 28px; font-weight: 900; }
    .status-dot { height: 12px; width: 12px; background-color: #00ff88; border-radius: 50%; display: inline-block; margin-left: 10px; box-shadow: 0 0 8px #00ff88; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .frame-box { border: 2px solid #3d444d; border-top: 4px solid #00f2ff; padding: 15px; background: #0b0e11; margin-bottom: 20px; border-radius: 4px; }
    table { width: 100%; border-collapse: collapse; }
    th { color: #00f2ff; font-size: 12px; text-align: left; padding: 10px; border-bottom: 2px solid #3d444d; background: #161b22; }
    td { font-size: 20px !important; font-family: 'Arial Black'; font-weight: 900; padding: 12px 10px; border-bottom: 1px solid #1c2127; }
    .perc-green { color: #00ff88; } .perc-red { color: #ff4d4d; }
    .eixo-frame { border: 2px dashed #00f2ff; color: #ffcc00; text-align: center; padding: 10px; font-size: 20px; margin: 15px 0; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

def fmt_v(val, prec=2): return f"{val:.{prec}f}".replace(".", ",")

# --- HEADER ---
market = fetch_market_data()
st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL K97</span><div class="status-dot"></div></div>', unsafe_allow_html=True)

# --- PAINEL ADM ---
with st.expander("⚙️ CONFIGURAÇÃO DO EIXO SINTÉTICO"):
    col_adm1, col_adm2 = st.columns(2)
    with col_adm1:
        eixo_dol_manual = st.number_input("DIGITE O EIXO DOLFUT (S):", value=5295.50, format="%.2f")
    with col_adm2:
        e
