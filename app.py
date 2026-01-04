import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# Configuração para ocupar o mínimo de espaço possível
st.set_page_config(page_title="Câmbio Slim", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    /* Fundo e Margens Zero */
    .stApp { background-color: #000000 !important; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; max-width: 400px !important; }
    
    /* Cabeçalho Minimalista */
    .header-box {
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF; font-size: 14px; text-align: center;
        border-bottom: 1px solid #333; padding-bottom: 4px; margin-bottom: 10px;
        display: flex; justify-content: center; align-items: center; gap: 8px;
    }

    /* Coluna de Preços */
    [data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        color: #ffffff !important; font-size: 24px !important;
    }

    /* Cores Específicas */
    div[data-testid="stMetric"]:has(p:contains("DÓLAR FUTURO")) div[data-testid="stMetricValue"] { color: #FFFF00 !important; }
    .max-val div[data-testid="stMetricValue"] { color: #00FF66 !important; font-size: 26px !important; }
    .min-val div[data-testid="stMetricValue"] { color: #FF0033 !important; font-size: 26px !important; }

    [data-testid="stMetricLabel"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important; color: #ff9900 !important; margin-bottom: -5px !important;
    }

    /* Remover espaçamentos extras do Streamlit */
    [data-testid="stMetric"] { border-bottom: 1px solid #111; padding: 2px 0 !important; margin-bottom: -15px !important; }
    .st-expanderHeader { background-color: #000 !important; color: #333 !important; font-size: 8px !important; }

    /* Rodapé Slim */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; border-top: 1px solid #333;
        position: fixed; bottom: 0; left: 0; padding: 4px 0;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #ffb400;
    }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
    """, unsafe_allow_html=True)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d")
        if not df.empty:
            p = df['Close'].iloc[-1]
            h = df['High'].iloc[-1]
            l = df['Low'].iloc[-1]
            prev = t.info.get('previousClose', p)
            v = ((p - prev) / prev) * 100
            return p, v, h, l
    except: return 0.0, 0.0, 0.0, 0.0
    return 0.0, 0.0, 0.0, 0.0

# --- TELA ---
st.markdown("<div class='header-box'>🏛️ CÂMBIO</div>", unsafe_allow_html=True)

with st.expander("SET"):
    frp = st.number_input("FRP", value=0.0150, format="%.4f")
    aju = st.number_input("AJU", value=5.4500, format="%.4f")

# Dados
s, sv, sh, sl = get_data("USDBRL=X")
u, uv, _, _ = get_data("USDT-BRL")
dx, dxv, _, _ = get_data("DX-Y.NYB")
ew, ewv, _, _ = get_data("EWZ")
d27, d27v, _, _ = get_data("DI1F27.SA")
d29, d29v, _, _ = get_data("DI1F29.SA")
d31, d31v, _, _ = get_data("DI1F31.SA")

c1, c2 = st.columns([1.2, 1])

with c1:
    st.metric("DÓLAR SPOT", f"{s:.4f}", f"{sv:+.2f}%")
    st.metric("DÓLAR FUTURO", f"{s + frp:.4f}", f"FRP {frp:.4f}", delta_color="off")
    st.metric("AJUSTE B3", f"{aju:.4f}", "FIXO", delta_color="off")
    st.metric("USDT / BRL", f"{u if u > 0 else s*1.002:.3f}")

with c2:
    st.markdown("<div class='max-val'>", unsafe_allow_html=True)
    st.metric("MÁXIMA FUT", f"{sh + frp:.4f}")
    st.markdown("</div><div class='min-val'>", unsafe_allow_html=True)
    st.metric("MÍNIMA FUT", f"{sl + frp:.4f}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.metric("DXY", f"{dx:.2f}")
    st.metric("EWZ", f"{ew:.2f}")

# Rodapé
def fdi(v, vr): return f"{v:.2f}% ({vr:+.2f}%)" if v > 0 else "---"
led = f"""
    <div class="ticker-wrap"><div class="ticker">
        ● DI 27: {fdi(d27, d27v)}  ● DI 29: {fdi(d29, d29v)}  ● DI 31: {fdi(d31, d31v)}  ● MONITOR ATIVO ●
    </div></div>
"""
st.markdown(led, unsafe_allow_html=True)
