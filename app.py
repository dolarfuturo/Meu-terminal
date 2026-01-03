import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout Bloomberg (Fundo Totalmente Preto)
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
        border-top: 1px solid #333; padding: 15px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Roboto Mono', monospace; font-size: 22px; color: #FF9900;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item { display: inline-block; margin-right: 60px; font-weight: bold; }

    /* Estilo dos Cards Centrais */
    [data-testid="metric-container"] {
        background-color: #000000;
        border: 1px solid #262626;
        padding: 20px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] { font-size: 36px !important; font-weight: 700 !important; color: #FFFFFF !important; }
    div[data-testid="stMetricLabel"] { font-size: 16px !important; color: #888888 !important; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

with st.expander("⚙️ CONFIGURAÇÕES"):
    frp_manual = st.number_input("Ajuste FRP", value=0.0150, format="%.4f")

# Função Robusta para buscar Preço e Variação
def get_data(ticker):
    try:
        df = yf.download(ticker, period="10d", interval="1d", progress=False)
        if not df.empty and len(df) >= 2:
            df_clean = df['Close'].dropna()
            price = float(df_clean.iloc[-1])
            prev = float(df_clean.iloc[-2])
            var = ((price - prev) / prev) * 100
            return price, var
    except:
        return 0.0, 0.0
    return 0.0, 0.0

# --- CENTRO DA TELA: CÂMBIO & ATIVOS ---
st.markdown("<h2 style='text-align: center; color: #444; font-size: 24px;'>🏦 CÂMBIO & ATIVOS</h2>", unsafe_allow_html=True)

_, col_center, _ = st.columns([0.02, 0.96, 0.02])

with col_center:
    # Linha 1: Moedas
    c1, c2, c3 = st.columns(3)
    spot, spot_v = get_data("USDBRL=X")
    usdt, usdt_v = get_data("USDT-BRL")
    
    if spot > 0:
        c1.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
        c2.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    if usdt > 0:
        c3.metric("USDT / BRL", f"{usdt:.3f}", f"{usdt_v:+.2f}%")

    st.markdown("<div style='margin: 25px;'></div>", unsafe_allow_html=True)

    # Linha 2: Ativos (DXY e EWZ)
    c4, c5, c6 = st.columns(3)
    dxy, dxy_v = get_data("DX-Y.NYB")
    ewz, ewz_v = get_data("EWZ")
    
    if dxy > 0: c4.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
    if ewz > 0: c5.metric("EWZ (IBOV USD)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")

# --- RODAPÉ LED (JUROS DIs) ---
di27, di27_v = get_data("DI1F27.SA")
di29, di29_v = get_data("DI1F29.SA")
di31, di31_v = get_data("DI1F31.SA")

def fmt_led(val, var):
    return f"{val:.2f}% ({var:+.2f}%)" if val > 0 else "OFFLINE"

led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span class="ticker-item">● DI 2027: {fmt_led(di27, di27_v)}</span>
            <span class="ticker-item">● DI 2029: {fmt_led(di29, di29_v)}</span>
            <span class="ticker-item">● DI 2031: {fmt_led(di31, di31_v)}</span>
            <span class="ticker-item">● TERMINAL EM OPERAÇÃO ●</span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)

