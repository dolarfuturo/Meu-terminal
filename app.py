import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout (Tela Total)
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; }
    [data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Configurações no Topo
with st.expander("⚙️ CONFIGURAÇÕES (FRP e Ajuste)"):
    c_adj1, c_adj2 = st.columns(2)
    frp_manual = c_adj1.number_input("Ajuste FRP", value=0.0150, format="%.4f", step=0.0001)
    ajuste_anterior = c_adj2.number_input("Ajuste Ref. (Dólar)", value=5.4100, format="%.4f")

st.title("🏦 TERMINAL DE MERCADO")

# Função Mestre para buscar Preço, Ajuste e Variação
def buscar_estavel(ticker):
    try:
        # Puxamos os últimos dias para garantir que pegamos o fechamento
        df = yf.download(ticker, period="7d", interval="1d", progress=False)
        if not df.empty and len(df) >= 2:
            atual = float(df['Close'].iloc[-1])
            ajuste_ref = float(df['Close'].iloc[-2]) # Fechamento anterior como base de ajuste
            variacao = ((atual - ajuste_ref) / ajuste_ref) * 100
            return atual, ajuste_ref, variacao
    except:
        return None, None, None
    return None, None, None

# --- BLOCO 1: CÂMBIO ---
st.subheader("💹 Câmbio & Stablecoin")
c1, c2, c3, c4 = st.columns(4)

spot_p, spot_a, spot_v = buscar_estavel("USDBRL=X")
usdt_p, _, usdt_v = buscar_estavel("USDT-BRL")

if spot_p:
    c1.metric("DÓLAR SPOT", f"R$ {spot_p:.4f}", f"{spot_v:+.2f}%")
    c2.metric("AJUSTE REF", f"R$ {spot_a:.4f}", "Liquidação")
    c3.metric("DÓLAR FUTURO", f"R$ {spot_p + frp_manual:.4f}", f"FRP: {frp_manual:.4f}", delta_color="off")
    
    # Se o USDT-BRL do Yahoo falhar, calculamos via Spot
    p_usdt = usdt_p if usdt_p else spot_p * 1.002
    v_usdt = usdt_v if usdt_v else spot_v
    c4.metric("USDT / BRL", f"R$ {p_usdt:.2f}", f"{v_usdt:+.2f}%")

st.divider()

# --- BLOCO 2: TAXAS DE JUROS (DIs) ---
st.subheader("📉 Taxas de Juros (DIs)")
d1, d2, d3 = st.columns(3)

def exibir_di(col, nome, ticker):
    p, a, v = buscar_estavel(ticker)
    if p:
        col.metric(nome, f"{p:.2f}%", f"Ref: {a:.2f}%")
    else:
        col.info(f"⏳ {nome}")

exibir_di(d1, "DI 2027", "DI1F27.SA")
exibir_di(d2, "DI 2029", "DI1F29.SA")
exibir_di(d3, "DI 2031", "DI1F31.SA")

st.divider()

# --- BLOCO 3: GLOBAL ---
st.subheader("🌎 Mercado Global")
g1, g2 = st.columns(2)

ewz_p, _, ewz_v = buscar_estavel("EWZ")
dxy_p, _, dxy_v = buscar_estavel("DX-Y.NYB")

if ewz_p: g1.metric("EWZ (Bolsa BR)", f"{ewz_p:.2f}", f"{ewz_v:+.2f}%")
if dxy_p: g2.metric("DXY (Dólar Global)", f"{dxy_p:.2f}", f"{dxy_v:+.2f}%")

st.caption("⚡ Dados atualizados a cada 5s. Mostrando último fechamento disponível.")

