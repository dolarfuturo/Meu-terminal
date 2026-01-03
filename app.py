import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout e Estilo Injetado (Bloomberg Original)
st.set_page_config(page_title="Terminal Bloomberg Style", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    /* Importando fontes de terminal */
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    /* Fundo Preto Bloomberg */
    .stApp { background-color: #000000 !important; }
    
    /* Título Superior Estilo Faixa de Comando */
    .bloomberg-header {
        background-color: #3d0000; /* Vermelho escuro da barra superior */
        color: white;
        padding: 5px 15px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        border-bottom: 2px solid #ff0000;
        margin-bottom: 20px;
    }

    /* Estilo dos Blocos de Métrica */
    [data-testid="stMetric"] {
        background-color: #000000;
        border-left: 3px solid #ff9900; /* Detalhe laranja lateral */
        padding: 10px !important;
    }

    /* Nomes dos Ativos (Amarelo/Laranja Bloomberg) */
    [data-testid="stMetricLabel"] p {
        font-family: 'JetBrains Mono', monospace !important;
        color: #ff9900 !important; /* Cor exata da imagem */
        font-weight: bold !important;
        font-size: 16px !important;
        text-transform: uppercase;
    }

    /* Números (Branco/Âmbar Digital) */
    [data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        color: #ffffff !important;
        font-size: 40px !important;
    }

    /* Variação (Verde Bloomberg) */
    [data-testid="stMetricDelta"] div {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 18px !important;
    }

    /* Barra de LED Inferior (Âmbar Neon) */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-top: 1px solid #333; padding: 10px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 30s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 22px; color: #ffb400;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    </style>
    """, unsafe_allow_html=True)

# Função para buscar dados estáveis
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

# --- CABEÇALHO ESTILO BARRA BLOOMBERG ---
st.markdown('<div class="bloomberg-header">PRO TERMINAL > MERCADO > CÂMBIO </div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ff9900; font-family: JetBrains Mono; font-size: 50px;'>🏛️ CÂMBIO</h1>", unsafe_allow_html=True)

# --- GRID CENTRAL ---
c1, c2, c3 = st.columns(3)
spot, spot_v = get_data("USDBRL=X")
usdt, usdt_v = get_data("USDT-BRL")

with st.sidebar:
    st.markdown("### CONFIGURAÇÕES")
    frp_manual = st.number_input("AJUSTE FRP", value=0.0150, format="%.4f")

if spot > 0:
    c1.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
    c2.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    c3.metric("USDT / BRL", f"{usdt if usdt > 0 else spot*1.002:.3f}", f"{usdt_v:+.2f}%")

st.markdown("<br><br>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)
dxy, dxy_v = get_data("DX-Y.NYB")
ewz, ewz_v = get_data("EWZ")

if dxy > 0: c4.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
if ewz > 0: c5.metric("EWZ (BOLSA BR)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")

# --- RODAPÉ LED ---
di27, di27_v = get_data("DI1F27.SA")
di29, di29_v = get_data("DI1F29.SA")

led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span>● DI 2027: {di27:.2f}% ({di27_v:+.2f}%)  ●  DI 2029: {di29:.2f}% ({di29_v:+.2f}%)  ●  TERMINAL BLOOMBERG STYLE DATA... </span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)

