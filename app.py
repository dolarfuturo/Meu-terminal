import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Tela e Estilo Bloomberg
st.set_page_config(page_title="Câmbio Pro", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    .stApp { background-color: #000000 !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* Cabeçalho */
    .header-box {
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF;
        font-size: 18px;
        text-align: center;
        border-bottom: 1px solid #333;
        padding-bottom: 8px;
        margin-bottom: 15px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
    }

    /* Blocos Verticais Compactos */
    [data-testid="stMetric"] {
        background-color: #000000;
        border-bottom: 1px solid #1a1a1a;
        padding: 5px 0 !important;
        margin-bottom: -22px !important;
    }

    /* Nomes dos Ativos (Laranja Bloomberg) */
    [data-testid="stMetricLabel"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: bold !important;
        font-size: 11px !important;
        text-transform: uppercase;
        color: #ff9900 !important; 
    }

    /* Números Digitais Quadrados */
    div[data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        color: #ffffff !important;
        font-size: 30px !important;
    }

    /* Cores Customizadas para Máxima e Mínima */
    .metric-max div[data-testid="stMetricValue"] { color: #00FF00 !important; }
    .metric-min div[data-testid="stMetricValue"] { color: #FF3333 !important; }

    .st-expanderHeader { background-color: #000 !important; color: #444 !important; font-size: 9px !important; border: none !important; }

    /* LED Inferior com Juros DI */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-top: 1px solid #444; padding: 10px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 16px; color: #ffb400;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item { margin-right: 50px; }
    </style>
    """, unsafe_allow_html=True)

def get_market_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d")
        if not df.empty:
            price = df['Close'].iloc[-1]
            high = df['High'].iloc[-1]
            low = df['Low'].iloc[-1]
            prev = t.info.get('previousClose', price)
            var = ((price - prev) / prev) * 100
            return price, var, high, low
    except:
        return 0.0, 0.0, 0.0, 0.0
    return 0.0, 0.0, 0.0, 0.0

# --- TOPO ---
st.markdown("<div class='header-box'><span>🏛️</span><span>CÂMBIO</span></div>", unsafe_allow_html=True)

with st.expander("SET"):
    frp_manual = st.number_input("FRP", value=0.0150, format="%.4f")
    ajuste_fixo = st.number_input("AJUSTE", value=5.4500, format="%.4f")

# --- COLETA DE DADOS ---
spot, spot_v, s_high, s_low = get_market_data("USDBRL=X")
usdt, usdt_v, _, _ = get_market_data("USDT-BRL")
dxy, dxy_v, _, _ = get_market_data("DX-Y.NYB")
ewz, ewz_v, _, _ = get_market_data("EWZ")
di27, di27_v, _, _ = get_market_data("DI1F27.SA")
di29, di29_v, _, _ = get_market_data("DI1F29.SA")

if spot > 0:
    # Preços Principais
    st.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
    st.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    st.metric("PREÇO DE AJUSTE", f"{ajuste_fixo:.4f}", "B3", delta_color="off")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bloco de Máxima e Mínima com Cores Diferentes
    st.markdown("<div class='metric-max'>", unsafe_allow_html=True)
    st.metric("MÁXIMA FUT (DIA)", f"{s_high + frp_manual:.4f}", "HIGH")
    st.markdown("</div><div class='metric-min'>", unsafe_allow_html=True)
    st.metric("MÍNIMA FUT (DIA)", f"{s_low + frp_manual:.4f}", "LOW")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Outros Ativos
    st.metric("USDT / BRL", f"{usdt if usdt > 0 else spot*1.002:.3f}", f"{usdt_v:+.2f}%")
    st.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
    st.metric("EWZ (BRL)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")

st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

# --- RODAPÉ LED COM DI ---
def fmt_di(val, var): return f"{val:.2f}% ({var:+.2f}%)" if val > 0 else "---"

led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span class="ticker-item">● DI 2027: {fmt_di(di27, di27_v)}</span>
            <span class="ticker-item">● DI 2029: {fmt_di(di29, di29_v)}</span>
            <span class="ticker-item">● TAXAS DE JUROS (DI) EM TEMPO REAL ● FONTE: B3 / YAHOO ●</span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)
