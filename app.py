import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout e Auto-Refresh (30 segundos)
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=30000, key="datarefresh")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; }
    [data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Painel de Controle
with st.sidebar:
    st.header("⚙️ Ajustes")
    frp_manual = st.number_input("Ajuste FRP", value=0.0150, format="%.4f", step=0.0001)

st.title("🏦 TERMINAL PROFISSIONAL")

# 2. FUNÇÃO PARA BUSCAR ÚLTIMO PREÇO REAL
def buscar_dados(ticker, period="5d"):
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        if not df.empty:
            atual = float(df['Close'].iloc[-1])
            anterior = float(df['Close'].iloc[-2])
            var = ((atual - anterior) / anterior) * 100
            return atual, var
    except:
        return None, None
    return None, None

# 3. CÂMBIO E USDT
st.subheader("💹 Câmbio & Stablecoin")
c1, c2, c3 = st.columns(3)

# Dólar Spot
spot_p, spot_v = buscar_dados("USDBRL=X")
# USDT (Dólar Cripto)
usdt_p, usdt_v = buscar_dados("USDT-BRL")

if spot_p:
    c1.metric("DÓLAR SPOT", f"R$ {spot_p:.4f}", f"{spot_v:+.2f}%")
    c2.metric("DÓLAR FUTURO", f"R$ {spot_p + frp_manual:.4f}", f"FRP: {frp_manual:.4f}")
else:
    c1.error("Spot: Offline")

if usdt_p:
    c3.metric("USDT / BRL", f"R$ {usdt_p:.2f}", f"{usdt_v:+.2f}%")

st.divider()

# 4. JUROS E ATIVOS GLOBAIS
st.subheader("📊 Juros (DI) e Globais")
g1, g2, g3, g4 = st.columns(4)

ativos = [
    ("DI 2027", "DI1F27.SA", g1, "%"),
    ("DI 2029", "DI1F29.SA", g2, "%"),
    ("EWZ (Bolsa BR)", "EWZ", g3, ""),
    ("DXY (Dólar Global)", "DX-Y.NYB", g4, "")
]

for nome, ticker, col, suf in ativos:
    p, v = buscar_dados(ticker, period="7d")
    if p:
        col.metric(nome, f"{p:.2f}{suf}", f"{v:+.2f}%")
    else:
        col.info(f"{nome}: Offline")

st.caption("🔄 Atualização automática ativa (30s). Dados de fim de semana refletem o último fechamento útil.")

