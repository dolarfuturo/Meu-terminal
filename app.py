import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout e Auto-Refresh (5 segundos)
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 30px; font-weight: bold; }
    [data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Painel de Controle
with st.sidebar:
    st.header("⚙️ Ajustes")
    frp_manual = st.number_input("Ajuste FRP", value=0.0150, format="%.4f", step=0.0001)

st.title("🏦 TERMINAL PROFISSIONAL")

# Função de busca robusta
def buscar_dados(ticker, period="7d"):
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        if not df.empty and len(df) >= 2:
            atual = float(df['Close'].iloc[-1])
            anterior = float(df['Close'].iloc[-2])
            var = ((atual - anterior) / anterior) * 100
            return atual, var
    except:
        return None, None
    return None, None

# --- BLOCO 1: CÂMBIO & USDT ---
st.subheader("💹 Câmbio & Stablecoin")
c1, c2, c3 = st.columns(3)

spot_p, spot_v = buscar_dados("USDBRL=X")
usdt_p, usdt_v = buscar_dados("USDT-BRL")

if spot_p:
    c1.metric("DÓLAR SPOT", f"R$ {spot_p:.4f}", f"{spot_v:+.2f}%")
    c2.metric("DÓLAR FUTURO", f"R$ {spot_p + frp_manual:.4f}", f"FRP: {frp_manual:.4f}")
else:
    c1.info("Spot: Carregando...")

if usdt_p:
    c3.metric("USDT / BRL (24h)", f"R$ {usdt_p:.2f}", f"{usdt_v:+.2f}%")

st.divider()

# --- BLOCO 2: JUROS (DIs) ---
st.subheader("📉 Taxas de Juros (DIs)")
d1, d2, d3 = st.columns(3)

# Buscando os 3 DIs solicitados
di27_p, di27_v = buscar_dados("DI1F27.SA")
di29_p, di29_v = buscar_dados("DI1F29.SA")
di31_p, di31_v = buscar_dados("DI1F31.SA")

if di27_p: d1.metric("DI 2027", f"{di27_p:.2f}%", f"{di27_v:+.2f}%")
if di29_p: d2.metric("DI 2029", f"{di29_p:.2f}%", f"{di29_v:+.2f}%")
if di31_p: d3.metric("DI 2031", f"{di31_p:.2f}%", f"{di31_v:+.2f}%")

st.divider()

# --- BLOCO 3: ATIVOS GLOBAIS ---
st.subheader("🌎 Mercado Global")
g1, g2 = st.columns(2)

ewz_p, ewz_v = buscar_dados("EWZ")
dxy_p, dxy_v = buscar_dados("DX-Y.NYB")

if ewz_p: g1.metric("EWZ (Bolsa BR)", f"{ewz_p:.2f}", f"{ewz_v:+.2f}%")
if dxy_p: g2.metric("DXY (Dólar Global)", f"{dxy_p:.2f}", f"{dxy_v:+.2f}%")

st.caption("⚡ Atualização em tempo real (5s). Dados refletem o último fechamento disponível no Yahoo Finance.")

