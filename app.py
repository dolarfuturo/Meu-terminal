import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout e Estética Profissional
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    /* Importando fontes: Roboto para textos e Share Tech Mono para números quadrados */
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&family=Share+Tech+Mono&display=swap');
    
    .stApp { background-color: #121212; }
    .main { background-color: #121212; color: #FFFFFF; }
    
    /* Estilo dos Cards */
    [data-testid="metric-container"] {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        padding: 20px;
        text-align: center;
        border-radius: 8px;
    }
    
    /* Números com fonte QUADRADA */
    div[data-testid="stMetricValue"] { 
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 42px !important; 
        font-weight: 400 !important; 
        color: #FFFFFF !important; 
    }
    
    /* Nomes dos Ativos em Negrito */
    div[data-testid="stMetricLabel"] { 
        font-family: 'Roboto Mono', monospace !important;
        font-size: 17px !important; 
        font-weight: 900 !important; 
        margin-bottom: 10px !important;
    }

    /* Ticker LED */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000000; 
        border-top: 2px solid #FF9900; padding: 12px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 22px; color: #FF9900;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item { display: inline-block; margin-right: 60px; }
    </style>
    """, unsafe_allow_html=True)

# Função para buscar dados (com suporte a fim de semana)
def get_data(ticker):
    try:
        df = yf.download(ticker, period="10d", interval="1d", progress=False)
        if not df.empty:
            df_clean = df['Close'].dropna()
            if len(df_clean) >= 2:
                price = float(df_clean.iloc[-1])
                prev = float(df_clean.iloc[-2])
                var = ((price - prev) / prev) * 100
                return price, var
    except: return 0.0, 0.0
    return 0.0, 0.0

# --- CABEÇALHO ---
st.markdown("<h1 style='text-align: center; font-size: 50px; margin-bottom: 0;'>🏛️</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: white; font-weight: 900; margin-top: -15px; font-family: Roboto Mono;'>CÂMBIO</h2>", unsafe_allow_html=True)

with st.expander("⌨️ AJUSTE FRP"):
    frp_manual = st.number_input("Valor FRP", value=0.0150, format="%.4f")

st.markdown("<br>", unsafe_allow_html=True)

# --- GRID CENTRAL ---
_, col_center, _ = st.columns([0.05, 0.9, 0.05])

with col_center:
    # Linha 1: Câmbio com Cores nos Nomes
    c1, c2, c3 = st.columns(3)
    spot, spot_v = get_data("USDBRL=X")
    usdt, usdt_v = get_data("USDT-BRL")
    
    if spot > 0:
        # Nome em AZUL
        st.markdown("<style>div[data-testid='column']:nth-of-type(1) label { color: #4DA6FF !important; }</style>", unsafe_allow_html=True)
        c1.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
        
        # Nome em BRANCO
        c2.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    
    # Nome em VERDE ÁGUA
    st.markdown("<style>div[data-testid='column']:nth-of-type(3) label { color: #00FFCC !important; }</style>", unsafe_allow_html=True)
    p_usdt = usdt if usdt > 0 else spot * 1.002
    c3.metric("USDT / BRL", f"{p_usdt:.3f}", f"{usdt_v if usdt_v != 0 else 0.05:+.2f}%")

    st.markdown("<div style='margin: 30px;'></div>", unsafe_allow_html=True)

    # Linha 2: Índices
    c4, c5, c6 = st.columns(3)
    dxy, dxy_v = get_data("DX-Y.NYB")
    ewz, ewz_v = get_data("EWZ")
    
    # Nome em CINZA CLARO
    if dxy > 0: 
        st.markdown("<style>div[data-testid='column']:nth-of-type(4) label { color: #CCCCCC !important; }</style>", unsafe_allow_html=True)
        c4.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
    
    # Nome em VERDE LIMA
    if ewz > 0: 
        st.markdown("<style>div[data-testid='column']:nth-of-type(5) label { color: #ADFF2F !important; }</style>", unsafe_allow_html=True)
        c5.metric("EWZ (Bolsa BR)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")

# --- RODAPÉ LED ---
di27, di27_v = get_data("DI1F27.SA")
di29, di29_v = get_data("DI1F29.SA")
di31, di31_v = get_data("DI1F31.SA")

def fmt_led(v, var): return f"{v:.2f}% ({var:+.2f}%)" if v > 0 else "OFFLINE"

led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span class="ticker-item">● DI 2027: {fmt_led(di27, di27_v)}</span>
            <span class="ticker-item">● DI 2029: {fmt_led(di29, di29_v)}</span>
            <span class="ticker-item">● DI 2031: {fmt_led(di31, di31_v)}</span>
            <span class="ticker-item">● TERMINAL EM ALTA PERFORMANCE ●</span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)

