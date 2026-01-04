import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Terminal Pro", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    .stApp { background-color: #000000 !important; }
    .block-container { padding-top: 1rem !important; }
    
    .header-box {
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF; font-size: 18px; text-align: center;
        border-bottom: 1px solid #333; padding-bottom: 8px; margin-bottom: 15px;
        display: flex; justify-content: center; align-items: center; gap: 10px;
    }

    /* Coluna 1: Preços (Estilo Bloomberg) */
    .col-precos [data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        color: #ffffff !important; font-size: 28px !important;
    }

    /* Coluna 2: Máximas e Mínimas (Estilo Alerta) */
    .col-limites [data-testid="stMetricValue"] {
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 32px !important; font-weight: bold !important;
    }
    
    /* Destaque Cores Coluna 2 */
    .max-box [data-testid="stMetricValue"] { color: #00FF66 !important; } /* Verde Neon */
    .min-box [data-testid="stMetricValue"] { color: #FF0033 !important; } /* Vermelho Rubi */

    /* Destaque Dólar Futuro */
    div[data-testid="stMetric"]:has(p:contains("DÓLAR FUTURO")) div[data-testid="stMetricValue"] {
        color: #FFFF00 !important;
    }

    [data-testid="stMetricLabel"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important; color: #ff9900 !important; 
    }

    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-top: 1px solid #444; padding: 10px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #ffb400;
    }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .ticker-item { margin-right: 40px; }
    </style>
    """, unsafe_allow_html=True)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d")
        if not df.empty:
            return df['Close'].iloc[-1], ((df['Close'].iloc[-1] - t.info.get('previousClose', df['Close'].iloc[-1])) / t.info.get('previousClose', df['Close'].iloc[-1])) * 100, df['High'].iloc[-1], df['Low'].iloc[-1]
    except: return 0.0, 0.0, 0.0, 0.0
    return 0.0, 0.0, 0.0, 0.0

# --- INTERFACE ---
st.markdown("<div class='header-box'><span>🏛️</span><span>CÂMBIO</span></div>", unsafe_allow_html=True)

with st.expander("SET"):
    frp = st.number_input("FRP", value=0.0150, format="%.4f")
    ajuste = st.number_input("AJU", value=5.4500, format="%.4f")

spot, spot_v, s_high, s_low = get_data("USDBRL=X")
usdt, usdt_v, _, _ = get_data("USDT-BRL")
dxy, dxy_v, _, _ = get_data("DX-Y.NYB")
ewz, ewz_v, _, _ = get_data("EWZ")
di27, di27_v, _, _ = get_data("DI1F27.SA")
di29, di29_v, _, _ = get_data("DI1F29.SA")
di31, di31_v, _, _ = get_data("DI1F31.SA")

c1, c2 = st.columns([1, 1])

with c1: # Coluna de Preços
    st.markdown("<div class='col-precos'>", unsafe_allow_html=True)
    st.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
    st.metric("DÓLAR FUTURO", f"{spot + frp:.4f}", f"FRP {frp:.4f}", delta_color="off")
    st.metric("PREÇO DE AJUSTE", f"{ajuste:.4f}", "B3", delta_color="off")
    st.metric("USDT / BRL", f"{usdt if usdt > 0 else spot*1.002:.3f}")
    st.metric("DXY INDEX", f"{dxy:.2f}")
    st.metric("EWZ (BRL)", f"{ewz:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

with c2: # Coluna de Limites
    st.markdown("<div class='col-limites'>", unsafe_allow_html=True)
    st.markdown("<div class='max-box'>", unsafe_allow_html=True)
    st.metric("MÁXIMA FUT", f"{s_high + frp:.4f}")
    st.markdown("</div><div class='min-box'>", unsafe_allow_html=True)
    st.metric("MÍNIMA FUT", f"{s_low + frp:.4f}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- RODAPÉ ---
def fmt(v, var): return f"{v:.2f}% ({var:+.2f}%)" if v > 0 else "---"
led = f"""
    <div class="ticker-wrap"><div class="ticker">
        <span class="ticker-item">● DI 27: {fmt(di27, di27_v)}</span>
        <span class="ticker-item">● DI 29: {fmt(di29, di29_v)}</span>
        <span class="ticker-item">● DI 31: {fmt(di31, di31_v)}</span>
        <span class="ticker-item">● MONITOR OPERACIONAL ATIVO ●</span>
    </div></div>
"""
st.markdown(led, unsafe_allow_html=True)
