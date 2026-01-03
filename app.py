
import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout Bloomberg
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    .main { background-color: #000000; color: #FFFFFF; font-family: 'Roboto Mono', monospace; }
    [data-testid="stHeader"] { background-color: #000000; }
    
    /* Ticker LED */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-top: 1px solid #333; padding: 12px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Roboto Mono', monospace; font-size: 20px; color: #FF9900;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item { display: inline-block; margin-right: 60px; font-weight: bold; }

    /* Estilo dos Cards */
    [data-testid="metric-container"] {
        background-color: #000000;
        border: 1px solid #262626;
        padding: 15px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #FFFFFF !important; }
    div[data-testid="stMetricLabel"] { font-size: 14px !important; color: #888888 !important; }
    </style>
    """, unsafe_allow_html=True)

with st.expander("⚙️ CONFIGURAÇÕES"):
    frp_manual = st.number_input("Ajuste FRP", value=0.0150, format="%.4f")

# Função Robusta para Garantir que o Preço Apareça
def get_data(ticker):
    try:
        # Puxamos um histórico maior para garantir que o preço de sexta esteja lá
        df = yf.download(ticker, period="10d", interval="1d", progress=False)
        if not df.empty and len(df) >= 2:
            # Pegamos o último valor não nulo disponível
            price = float(df['Close'].dropna().iloc[-1])
            prev = float(df['Close'].dropna().iloc[-2])
            var = ((price - prev) / prev) * 100
            return price, var
    except:
        return 0.0, 0.0
    return 0.0, 0.0

# --- CENTRO DA TELA ---
st.markdown("<h2 style='text-align: center; color: #666; font-size: 20px;'>🏦 CÂMBIO & ATIVOS</h2>", unsafe_allow_html=True)

_, col_center, _ = st.columns([0.05, 0.9, 0.05])

with col_center:
    # Linha 1: Moedas
    c1, c2, c3 = st.columns(3)
    spot, spot_v = get_data("USDBRL=X")
    usdt, usdt_v = get_data("USDT-BRL")
    
    if spot > 0:
        c1.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
        c2.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4
