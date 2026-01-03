import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configuração de Tela e Estilo Bloomberg (Fundo Escuro)
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');
    
    .main { background-color: #000000; color: #FFFFFF; font-family: 'Roboto Mono', monospace; }
    [data-testid="stHeader"] { background-color: #000000; }
    
    /* Estilo dos Cards (Negrito e Fundo Escuro) */
    [data-testid="metric-container"] {
        background-color: #000000;
        border: 1px solid #333333;
        padding: 20px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] { font-size: 38px !important; font-weight: 800 !important; color: #FFFFFF !important; }
    div[data-testid="stMetricLabel"] { font-size: 18px !important; font-weight: 700 !important; color: #AAAAAA !important; }
    
    /* Ticker LED Inferior */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-top: 1px solid #444; padding: 15px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Roboto Mono', monospace; font-size: 22px; color: #FF9900; font-weight: bold;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item { display: inline-block; margin-right: 60px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Função de Dados Robusta (Pega sempre o último fechamento disponível)
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="10d", interval="1d", progress=False)
        if not df.empty:
            df_clean = df['Close'].dropna()
            if len(df_clean) >= 2:
                price = float(df_clean.iloc[-1])
                prev = float(df_clean.iloc[-2])
                var = ((price - prev) / prev) * 100
                return price, var
    except:
        return 0.0, 0.0
    return 0.0, 0.0

# --- SEÇÃO CENTRAL: CÂMBIO ---
st.markdown("<h1 style='text-align: center; color: white; font-weight: 900; letter-spacing: 2px;'>CÂMBIO</h1>", unsafe_allow_html=True)

# Configuração do FRP
with st.expander("⌨️ AJUSTE FRP"):
    frp_manual = st.number_input("FRP", value=0.0150, format="%.4f")

_, col_center, _ = st.columns([0.05, 0.9, 0.05])

with col_center:
    # Primeira Linha: Moedas Principais
    c1, c2, c3 = st.columns(3)
    spot, spot_v = get_market_data("USDBRL=X")
    usdt, usdt_v = get_market_data("USDT-BRL")
    
    if spot > 0:
        c1.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
        c2.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    if usdt > 0:
        c3.metric("USDT / BRL", f"{usdt:.3f}", f"{usdt_v:+.2f}%")

    st.markdown("<div style='margin: 30px;'></div>", unsafe_allow_html=True)

    # Segunda Linha: Índices (DXY e EWZ)
    c4, c5, c6 = st.columns(3)
    dxy, dxy_v = get_market_data("DX-Y.NYB")
    ewz, ewz_v = get_market_data("EWZ")
    
    if dxy > 0:
        c4.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
    if ewz > 0:
        c5.metric("EWZ (IBOV USD)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")

# --- RODAPÉ: LED PASSANDO (JUROS) ---
di27, di27_v = get_market_data("DI1F27.SA")
di29, di29_v = get_market_data("DI1F29.SA")
di31, di31_v = get_market_data("DI1F31.SA")

def fmt(v, var): return f"{v:.2f}% ({var:+.2f}%)" if v > 0 else "---"

led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span class="ticker-item">● DI 2027: {fmt(di27, di27_v)}</span>
            <span class="ticker-item">● DI 2029: {fmt(di29, di29_v)}</span>
            <span class="ticker-item">● DI 2031: {fmt(di31, di31_v)}</span>
            <span class="ticker-item">● TERMINAL OPERACIONAL ●</span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)

