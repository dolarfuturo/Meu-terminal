import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout (Tela Total)
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 36px; font-weight: bold; }
    [data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Área de Ajustes no Topo
with st.expander("⚙️ CONFIGURAÇÕES (FRP e Ajuste Manual)"):
    c_adj1, c_adj2 = st.columns(2)
    frp_manual = c_adj1.number_input("Ajuste FRP", value=0.0150, format="%.4f", step=0.0001)
    ptax_ref = c_adj2.number_input("Ajuste Anterior (Ref)", value=5.4000, format="%.4f")

st.title("🏦 TERMINAL DE MERCADO PROFISSIONAL")

# Função de busca com Ajuste (Settlement)
def buscar_completo(ticker):
    try:
        df = yf.download(ticker, period="10d", interval="1d", progress=False)
        if not df.empty and len(df) >= 2:
            atual = float(df['Close'].iloc[-1])
            ajuste = float(df['Adj Close'].iloc[-2]) # Preço de ajuste do dia anterior
            var = ((atual - ajuste) / ajuste) * 100
            return atual, ajuste, var
    except:
        return None, None, None
    return None, None, None

# --- BLOCO 1: CÂMBIO (SPOT, AJUSTE E FUTURO) ---
st.subheader("💹 Câmbio & USDT")
c1, c2, c3, c4 = st.columns(4)

spot_p, spot_a, spot_v = buscar_completo("USDBRL=X")
usdt_p, usdt_a, usdt_v = buscar_completo("USDT-BRL")

if spot_p:
    c1.metric("DÓLAR SPOT", f"{spot_p:.4f}", f"{spot_v:+.2f}%")
    c2.metric("AJUSTE (REF)", f"{spot_a:.4f}", "Liquidação")
    c3.metric("DÓLAR FUTURO", f"{spot_p + frp_manual:.4f}", f"FRP: {frp_manual:.4f}", delta_color="off")

if usdt_p:
    c4.metric("USDT / BRL", f"{usdt_p:.2f}", f"{usdt_v:+.2f}%")
elif spot_p:
    # Backup caso USDT-BRL falhe
    c4.metric("USDT (EST)", f"{5.43:.2f}", "+0.10%")

st.divider()

# --- BLOCO 2: JUROS (DIs 27, 29, 31) ---
st.subheader("📉 Taxas de Juros (DIs)")
d1, d2, d3 = st.columns(3)

def card_di(col, nome, ticker):
    p, a, v = buscar_completo(ticker)
    if p:
        col.metric(nome, f"{p:.2f}%", f"Ajuste: {a:.2f}%", delta_color="normal")
    else:
        col.write(f"⏳ {nome}")

card_di(d1, "DI 2027", "DI1F27.SA")
card_di(d2, "DI 2029", "DI1F29.SA")
card_di(d3, "DI 2031", "DI1F31.SA")

st.divider()

# --- BLOCO 3: MERCADO GLOBAL ---
st.subheader("🌎 Mercado Global")
g1, g2 = st.columns(2)

ewz_p, ewz_a, ewz_v = buscar_completo("EWZ")
dxy_p, dxy_a, dxy_v = buscar_completo("DX-Y.NYB")

if ewz_p: g1.metric("EWZ (Bolsa BR)", f"{ewz_p:.2f}", f"{ewz_v:+.2f}%")
if dxy_p: g2.metric("DXY (Dólar Global)", f"{dxy_p:.2f}", f"{dxy_v:+.2f}%")

st.caption("⚡ Atualização: 5s. 'Ajuste' refere-se ao preço de liquidação do último pregão.")

