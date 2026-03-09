import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL K97", layout="wide")

# --- MOTOR DE CÁLCULOS (SINTÉTICOS K97) ---
def get_eixo(max_val, min_val):
    return (max_val + min_val) / 2

def get_variacao_eixo(preco_atual, eixo_ref):
    if eixo_ref == 0: return "0,00%"
    var = ((preco_atual / eixo_ref) - 1) * 100
    return f"{var:+.2f}%".replace(".", ",")

def calcular_sintetico_k97(eixo_base, eixo_ewz, price_ewz_atual):
    """
    Motor do SPOT/DOLFUT: Criado sinteticamente conforme sua regra.
    Price = eixo * (eixo_EWZ / price_ewz - 1) * 100 / 2
    """
    try:
        desvio_ewz = (eixo_ewz / price_ewz_atual) - 1
        ajuste = (eixo_base * desvio_ewz * 100 / 2)
        return eixo_base + ajuste
    except:
        return eixo_base

@st.cache_data(ttl=30)
def fetch_real_time_market():
    # Apenas ativos reais para alimentar os sintéticos
    tickers = {"DXY": "DX-Y.NYB", "EWZ": "EWZ", "XAUUSD": "GC=F", "BRENT": "BZ=F"}
    res = {}
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1d")
            if not df.empty:
                res[name] = {"price": df['Close'].iloc[-1], "max": df['High'].iloc[-1], "min": df['Low'].iloc[-1], "open": df['Open'].iloc[-1]}
        except: res[name] = {"price": 0, "max": 0, "min": 0, "open": 0}
    return res

# CSS MANTIDO (BORDAS, CORES E PONTO)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .header-container { display: flex; align-items: center; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black'; font-size: 30px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black'; font-size: 30px; font-weight: 900; margin-left: 5px; }
    .status-dot { height: 12px; width: 12px; background-color: #00ff88; border-radius: 50%; box-shadow: 0 0 8px #00ff88; animation: pulse 1.5s infinite; margin-left: 10px;}
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .frame-box { border: 2px solid #3d444d; border-top: 4px solid #00f2ff; padding: 10px; background: #0b0e11; margin-bottom: 15px; }
    table { width: 100%; border-collapse: collapse; border: 1px solid #3d444d; }
    th { color: #00f2ff !important; font-size: 11px !important; border: 1px solid #3d444d !important; text-align: left; padding: 8px !important; background: #161b22; }
    td { font-size: 18px !important; font-family: 'Arial Black'; font-weight: 900; border: 1px solid #3d444d !important; padding: 8px !important; }
    .calc-row { display: flex; justify-content: space-between; font-size: 13.5px; font-weight: 900; padding: 2px 0; border-bottom: 1px solid #1c2127; }
    .perc-green { color: #00ff88; } .perc-red { color: #ff4d4d; }
    .eixo-frame { border: 2px dashed #00f2ff; color: #ffcc00; font-weight: 900; text-align: center; padding: 6px; margin: 10px 0; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

def fmt_v(val, prec=4): return f"{val:.{prec}f}".replace(".", ",")

# --- DATA FETCH ---
market = fetch_real_time_market()

# --- HEADER (Relógios) ---
c_logo, c_br, c_ny, c_ldn = st.columns([2.5, 1, 1, 1])
with c_logo: st.markdown('<div class="header-container"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL K97</span><div class="status-dot"></div></div>', unsafe_allow_html=True)

# --- PAINEL ADM (ÂNCORAS DO EIXO) ---
with st.expander("⚙️ CONFIGURAR EIXOS SINTÉTICOS"):
    c1, c2 = st.columns(2)
    with c1:
        eixo_spot_manual = st.number_input("EIXO SPOT SINTÉTICO:", value=5.4130, format="%.4f")
        eixo_dolfut_manual = st.number_input("EIXO DOLFUT SINTÉTICO:", value=5.4250, format="%.4f")
    with c2:
        # Pega o eixo do EWZ real para basear o cálculo do sintético
        eixo_ewz_ref = get_eixo(market["EWZ"]["max"], market["EWZ"]["min"])
        st.write(f"Eixo EWZ (Atualizado): {fmt_v(eixo_ewz_ref, 2)}")

# --- CÁLCULO DOS ATIVOS SINTÉTICOS ---
price_spot_k97 = calcular_sintetico_k97(eixo_spot_manual, eixo_ewz_ref, market["EWZ"]["price"])
price_dolfut_k97 = calcular_sintetico_k97(eixo_dolfut_manual, eixo_ewz_ref, market["EWZ"]["price"])

# --- GRADE ---
m_col
