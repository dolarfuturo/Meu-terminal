import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Tela
st.set_page_config(page_title="Câmbio Pro", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    .stApp { background-color: #000000 !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* Cabeçalho Compacto com Banco */
    .header-box {
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF;
        font-size: 16px;
        text-align: center;
        border-bottom: 1px solid #222;
        padding-bottom: 8px;
        margin-bottom: 10px;
    }

    /* Blocos Verticais Ultra Slim */
    [data-testid="stMetric"] {
        background-color: #000000;
        border-bottom: 1px solid #111;
        padding: 2px 0 !important;
        margin-bottom: -22px !important;
    }

    /* Nomes dos Ativos (Laranja Bloomberg) */
    [data-testid="stMetricLabel"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        text-transform: uppercase;
        color: #ff9900 !important; 
    }

    /* Números Digitais Quadrados */
    div[data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        color: #ffffff !important;
        font-size: 26px !important;
    }

    /* Cores especiais para Máxima (Verde) e Mínima (Vermelho) */
    div[data-testid="stMetricValue"]:has(span:contains("MAX")) { color: #00FF00 !important; }

    .st-expanderHeader { background-color: #000 !important; color: #222 !important; font-size: 8px !important; border: none !important; }

    /* LED Inferior */
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

def get_full_data(ticker):
    try:
        data = yf.Ticker(ticker)
        df = data.history(period="1d")
        if not df.empty:
            price = df['Close'].iloc[-1]
            high = df['High'].iloc[-1]
            low = df['Low'].iloc[-1]
            prev = data.info.get('previousClose', price)
            var = ((price - prev) / prev) * 100
            return price, var, high, low
    except: return 0.0, 0.0, 0.0, 0.0
    return 0.0, 0.0, 0.0, 0.0

# --- TOPO ---
st.markdown("<div class='header-box'>🏛️ CÂMBIO</div>", unsafe_allow_html=True)

with st.expander("SET"):
    frp_manual = st.number_input("FRP", value=0.0150, format="%.4f")
    ajuste_val = st.number_input("AJU", value=5.4500, format="%.4f")

# --- DADOS ---
spot, spot_v, s_high, s_low = get_full_data("USDBRL=X")
usdt, usdt_v, _, _ = get_full_data("USDT-BRL")
dxy, dxy_v, _, _ = get_full_data("DX-Y.NYB")
ewz, ewz_v, _, _ = get_full_data("EWZ")

if spot > 0:
    st.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
    st.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    
    # Máxima e Mínima do Futuro (Calculadas sobre o Spot + FRP)
    st.metric("MÁXIMA FUT (DIA)", f"{s_high + frp_manual:.4f}", "HIGH", delta_color="normal")
    st.metric("MÍNIMA FUT (DIA)", f"{s_low + frp_manual:.4f}", "LOW", delta_color="inverse")
    
    st.metric("AJUSTE B3", f"{ajuste_val:.4f}", "FIXO", delta_color="off")
    st.metric("USDT / BRL", f"{usdt if usdt > 0 else spot*1.002:.3f}", f"{usdt_v:+.2f}%")
    st.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
    st.metric("EWZ (BRL)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# --- LED ---
led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span>MERCADO ATIVO ● MÁX/MÍN AJUSTADAS AO FRP ● AGUARDANDO VOLATILIDADE </span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)
