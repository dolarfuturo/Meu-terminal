import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

# CSS FORÇADO PARA NÚMEROS QUADRADOS E FUNDO GRAFITE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Roboto:wght@900&display=swap');
    
    /* Fundo Grafite Escuro */
    .stApp { background-color: #121212 !important; }
    
    /* Forçar números quadrados (Digital) */
    [data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 45px !important;
        color: #FFFFFF !important;
        font-weight: 400 !important;
    }

    /* Forçar nomes em Negrito */
    [data-testid="stMetricLabel"] p {
        font-family: 'Roboto', sans-serif !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        text-transform: uppercase !important;
    }

    /* Cores Específicas nos Títulos */
    /* Dólar Spot - Azul */
    div[data-testid="column"]:nth-of-type(1) [data-testid="stMetricLabel"] p { color: #00BFFF !important; }
    /* USDT - Verde */
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricLabel"] p { color: #00FF99 !important; }
    /* DXY - Cinza */
    div[data-testid="column"]:nth-of-type(4) [data-testid="stMetricLabel"] p { color: #AAAAAA !important; }
    /* EWZ - Lima */
    div[data-testid="column"]:nth-of-type(5) [data-testid="stMetricLabel"] p { color: #CCFF00 !important; }

    /* LED Inferior */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-top: 2px solid #FF9900; padding: 15px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 24px; color: #FF9900;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    </style>
    """, unsafe_allow_html=True)

def get_data(ticker):
    try:
        df = yf.download(ticker, period="10d", interval="1d", progress=False)
        if not df.empty:
            df_clean = df['Close'].dropna()
            price = float(df_clean.iloc[-1])
            prev = float(df_clean.iloc[-2])
            var = ((price - prev) / prev) * 100
            return price, var
    except: return 0.0, 0.0
    return 0.0, 0.0

# --- TOPO ---
st.markdown("<h1 style='text-align: center; font-size: 60px; margin:0;'>🏛️</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: white; font-family: Roboto; font-weight: 900; margin-top:-20px;'>CÂMBIO</h1>", unsafe_allow_html=True)

with st.expander("⌨️ AJUSTE FRP"):
    frp_manual = st.number_input("FRP", value=0.0150, format="%.4f")

# --- BLOCO CENTRAL ---
c1, c2, c3 = st.columns(3)
spot, spot_v = get_data("USDBRL=X")
usdt, usdt_v = get_data("USDT-BRL")

if spot > 0:
    c1.metric("Dólar Spot", f"{spot:.4f}", f"{spot_v:+.2f}%")
    c2.metric("Dólar Futuro", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    c3.metric("USDT / BRL", f"{usdt if usdt > 0 else spot*1.002:.3f}", f"{usdt_v:+.2f}%")

st.markdown("<br>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)
dxy, dxy_v = get_data("DX-Y.NYB")
ewz, ewz_v = get_data("EWZ")

if dxy > 0: c4.metric("DXY Index", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
if ewz > 0: c5.metric("EWZ (Bolsa BR)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")

# --- LED ---
di27, di27_v = get_data("DI1F27.SA")
di29, di29_v = get_data("DI1F29.SA")

led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span>● DI 2027: {di27:.2f}% ● DI 2029: {di29:.2f}% ● MONITOR DIGITAL ATIVO ●</span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)

