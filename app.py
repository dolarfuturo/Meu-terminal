import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configuração para Split-Screen Lateral
st.set_page_config(page_title="Slim Side", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    /* Forçar fundo preto e remover todas as margens laterais */
    .stApp { background-color: #000000 !important; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }
    
    /* Cabeçalho Minimalista */
    .header-box {
        font-family: 'JetBrains Mono', monospace; color: #FFFFFF; font-size: 12px;
        text-align: center; border-bottom: 1px solid #333; padding: 2px 0; margin-bottom: 8px;
    }

    /* Valores Numéricos Slim */
    [data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        color: #ffffff !important; font-size: 19px !important; line-height: 1 !important;
    }
    
    /* Nomes dos Ativos (Laranja) */
    [data-testid="stMetricLabel"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 9px !important; color: #ff9900 !important; margin-bottom: -10px !important;
        white-space: nowrap;
    }

    [data-testid="stMetricDelta"] { font-size: 10px !important; }

    /* Cores de Destaque */
    div[data-testid="stMetric"]:has(p:contains("FUTURO")) div[data-testid="stMetricValue"] { color: #FFFF00 !important; }
    .max-box div[data-testid="stMetricValue"] { color: #00FF66 !important; }
    .min-box div[data-testid="stMetricValue"] { color: #FF0033 !important; }

    /* Redução radical de espaço entre linhas para caber na vertical */
    [data-testid="stMetric"] { 
        border-bottom: 1px solid #111; padding: 0px 0 !important; margin-bottom: -22px !important; 
    }
    
    /* Rodapé Largo e Visível */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; border-top: 2px solid #ff9900;
        position: fixed; bottom: 0; left: 0; padding: 10px 0; height: 45px; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #ffb400; font-weight: bold;
    }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    /* Esconder elementos desnecessários */
    #MainMenu, footer, header {visibility: hidden;}
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

# --- ESTRUTURA ---
st.markdown("<div class='header-box'>🏛️ CÂMBIO</div>", unsafe_allow_html=True)

# Captura de Dados
s, sv, sh, sl = get_data("USDBRL=X")
u, uv, _, _ = get_data("USDT-BRL")
dx, dxv, _, _ = get_data("DX-Y.NYB")
ew, ewv, _, _ = get_data("EWZ")
d27, d27v, _, _ = get_data("DI1F27.SA")
d29, d29v, _, _ = get_data("DI1F29.SA")
d31, d31v, _, _ = get_data("DI1F31.SA")

# Configurações (FRP automático ou manual)
with st.expander("SET"):
    frp = st.number_input("FRP", value=0.0150, format="%.4f")
    aju = st.number_input("AJU", value=5.4500, format="%.4f")

# Layout de Colunas Estreitas
c1, c2 = st.columns([1, 1])

with c1:
    st.metric("SPOT", f"{s:.4f}", f"{sv:+.2f}%")
    st.metric("FUTURO", f"{s + frp:.4f}", f"{sv:+.2f}%")
    st.metric("AJUSTE", f"{aju:.4f}")
    st.metric("USDT", f"{u:.3f}", f"{uv:+.2f}%")

with c2:
    st.markdown("<div class='max-box'>", unsafe_allow_html=True)
    st.metric("MÁXIMA", f"{sh + frp:.4f}")
    st.markdown("</div><div class='min-box'>", unsafe_allow_html=True)
    st.metric("MÍNIMA", f"{sl + frp:.4f}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.metric("DXY", f"{dx:.2f}", f"{dxv:+.2f}%")
    st.metric("EWZ", f"{ew:.2f}", f"{ewv:+.2f}%")

# Rodapé DI Grande
def fdi(v, vr): return f"{v:.2f}%({vr:+.2f}%)" if v > 0 else "---"
led = f"""
    <div class="ticker-wrap"><div class="ticker">
        DI27: {fdi(d27, d27v)} | DI29: {fdi(d29, d29v)} | DI31: {fdi(d31, d31v)} ● MONITOR ATIVO
    </div></div>
"""
st.markdown(led, unsafe_allow_html=True)
