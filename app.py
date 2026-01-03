import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Tela para caber sem scroll
st.set_page_config(page_title="Terminal Slim", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    /* Fundo Preto e remoção de margens do Streamlit */
    .stApp { background-color: #000000 !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* Título Minimalista */
    .titulo-cambio {
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF;
        font-size: 14px;
        text-align: center;
        border-bottom: 1px solid #222;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }

    /* Blocos Verticais Compactos */
    [data-testid="stMetric"] {
        background-color: #000000;
        border-bottom: 1px solid #111;
        padding: 2px 0 !important;
        margin-bottom: -20px !important;
    }

    /* Nomes dos Ativos (Laranja Bloomberg) */
    [data-testid="stMetricLabel"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        text-transform: uppercase;
        color: #ff9900 !important; 
    }

    /* Números Digitais Quadrados (Tamanho otimizado) */
    div[data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        color: #ffffff !important;
        font-size: 28px !important;
    }

    /* Ajuste do Expander para não ocupar espaço */
    .st-expanderHeader { background-color: #000 !important; color: #333 !important; font-size: 9px !important; border: none !important; }

    /* LED Inferior Slim */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-top: 1px solid #333; padding: 5px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #00FFCC;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    </style>
    """, unsafe_allow_html=True)

def get_data(ticker):
    try:
        df = yf.download(ticker, period="5d", interval="1d", progress=False)
        if not df.empty:
            df_clean = df['Close'].dropna()
            price = float(df_clean.iloc[-1])
            prev = float(df_clean.iloc[-2])
            var = ((price - prev) / prev) * 100
            return price, var
    except: return 0.0, 0.0
    return 0.0, 0.0

# --- TÍTULO ---
st.markdown("<div class='titulo-cambio'>TERMINAL > CÂMBIO</div>", unsafe_allow_html=True)

# CONFIGURAÇÕES ESCONDIDAS
with st.expander("SET"):
    frp_manual = st.number_input("FRP", value=0.0150, format="%.4f")
    ajuste_val = st.number_input("AJU", value=5.4500, format="%.4f")

# --- CONTEÚDO ---
spot, spot_v = get_data("USDBRL=X")
usdt, usdt_v = get_data("USDT-BRL")
dxy, dxy_v = get_data("DX-Y.NYB")
ewz, ewz_v = get_data("EWZ")

if spot > 0:
    st.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
    st.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    st.metric("AJUSTE B3", f"{ajuste_val:.4f}", "FIXO", delta_color="off")
    st.metric("USDT / BRL", f"{usdt if usdt > 0 else spot*1.002:.3f}", f"{usdt_v:+.2f}%")
    st.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
    st.metric("EWZ (BRL)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")

# --- LED ---
led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span>MERCADO AO VIVO ● TERMINAL VERTICAL SLIM ● DATA FEED ACTIVE </span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)

