import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout e Estética de Terminal (Preto Absoluto)
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    
    .main { background-color: #000000; color: #FFFFFF; font-family: 'Roboto Mono', monospace; }
    [data-testid="stHeader"] { background-color: #000000; }
    
    /* Ticker LED Estilo Bloomberg */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-top: 1px solid #333; padding: 10px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 30s linear infinite;
        font-family: 'Roboto Mono', monospace; font-size: 18px; color: #FF9900;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item { display: inline-block; margin-right: 50px; }

    /* Estilo dos Cards Centrais */
    [data-testid="metric-container"] {
        background-color: #000000;
        border: 1px solid #222222;
        padding: 15px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] { font-size: 34px !important; color: #FFFFFF !important; }
    div[data-testid="stMetricLabel"] { font-size: 14px !important; color: #888888 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Configurações (Escondidas)
with st.expander("⌨️ CONFIGS"):
    frp_manual = st.number_input("FRP", value=0.0150, format="%.4f")

def get_data(ticker):
    try:
        df = yf.download(ticker, period="7d", interval="1d", progress=False)
        if not df.empty and len(df) >= 2:
            price = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            var = ((price - prev) / prev) * 100
            return price, var
    except: return None, None
    return None, None

# --- CENTRO DA TELA: MOEDAS E ATIVOS ---
st.markdown("<h2 style='text-align: center; color: #444;'>🏦 CÂMBIO & ATIVOS</h2>", unsafe_allow_html=True)

# Centralizando os blocos
_, col_center, _ = st.columns([0.1, 0.8, 0.1])

with col_center:
    # Linha 1: Moedas
    c1, c2, c3 = st.columns(3)
    spot, spot_v = get_data("USDBRL=X")
    usdt, usdt_v = get_data("USDT-BRL")
    dxy, dxy_v = get_data("DX-Y.NYB")

    if spot:
        c1.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
        c2.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    if usdt:
        c3.metric("USDT / BRL", f"{usdt:.3f}", f"{usdt_v:+.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Linha 2: Ativos
    c4, c5, c6 = st.columns(3)
    ewz, ewz_v = get_data("EWZ")
    spx, spx_v = get_data("^GSPC")
    
    if dxy: c4.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
    if ewz: c5.metric("EWZ (IBOV USD)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")
    if spx: c6.metric("S&P 500", f"{int(spx)}", f"{spx_v:+.2f}%")

# --- RODAPÉ: LED PASSANDO (JUROS DIs) ---
di27, di27_v = get_data("DI1F27.SA")
di29, di29_v = get_data("DI1F29.SA")
di31, di31_v = get_data("DI1F31.SA")

led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span class="ticker-item">● DI 2027: {di27:.2f}% ({di27_v:+.2f}%)</span>
            <span class="ticker-item">● DI 2029: {di29:.2f}% ({di29_v:+.2f}%)</span>
            <span class="ticker-item">● DI 2031: {di31:.2f}% ({di31_v:+.2f}%)</span>
            <span class="ticker-item">● MERCADO OPERANDO EM TEMPO REAL ●</span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)

