import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configuração de Tela Cheia e Estilo Bloomberg
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    
    .main { background-color: #000000; color: #FFFFFF; font-family: 'Roboto Mono', monospace; }
    [data-testid="stHeader"] { background-color: #000000; }
    
    /* Customização dos Cards */
    [data-testid="metric-container"] {
        background-color: #111111;
        border: 1px solid #333333;
        padding: 8px 12px;
        border-radius: 4px;
        text-align: center;
    }
    
    div[data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700; color: #FFFFFF; }
    div[data-testid="stMetricLabel"] { font-size: 14px !important; color: #BBBBBB; text-transform: uppercase; }
    
    /* Cores de Variação Bloomberg */
    div[data-testid="stMetricDelta"] > div { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Cabeçalho Compacto (FRP Oculto)
with st.expander("⌨️ TERMINAL CONFIG"):
    c_config1, c_config2 = st.columns(2)
    frp_manual = c_config1.number_input("FRP", value=0.0150, format="%.4f", step=0.0001)
    st.caption("Ajuste o FRP para recalcular o Dólar Futuro instantaneamente.")

# 3. Função de Dados com Lógica TradingView
def get_market_data(ticker):
    try:
        # Puxamos dados de 7 dias com intervalo de 1 dia para pegar o fechamento anterior real
        df = yf.download(ticker, period="7d", interval="1d", progress=False)
        if not df.empty and len(df) >= 2:
            price = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            change = ((price - prev_close) / prev_close) * 100
            return price, change
    except:
        return None, None
    return None, None

# --- SEÇÃO 1: CÂMBIO ---
st.markdown("### 🏦 CÂMBIO")
row1_1, row1_2, row1_3, row1_4 = st.columns(4)

spot, spot_v = get_market_data("USDBRL=X")
usdt, usdt_v = get_market_data("USDT-BRL")

if spot:
    row1_1.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
    row1_2.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    # USDT Variação corrigida (Close vs Prev Close)
    if usdt:
        row1_3.metric("USDT / BRL", f"{usdt:.3f}", f"{usdt_v:+.2f}%")
    else:
        row1_3.metric("USDT / BRL", f"{spot * 1.001:.3f}", "BUSCANDO", delta_color="off")
    row1_4.metric("DXY INDEX", f"{get_market_data('DX-Y.NYB')[0]:.2f}", f"{get_market_data('DX-Y.NYB')[1]:+.2f}%")

st.markdown("---")

# --- SEÇÃO 2: TAXAS DE JUROS (Compacto para Tablet) ---
st.markdown("### 📉 TAXAS DE JUROS (DI)")
row2_1, row2_2, row2_3 = st.columns(3)

def di_card(col, label, ticker):
    val, var = get_market_data(ticker)
    if val:
        col.metric(label, f"{val:.2f}%", f"{var:+.2f}%")
    else:
        col.write(f"OFFLINE {label}")

di_card(row2_1, "DI 2027", "DI1F27.SA")
di_card(row2_2, "DI 2029", "DI1F29.SA")
di_card(row2_3, "DI 2031", "DI1F31.SA")

# --- SEÇÃO 3: B3 / BRASIL ---
st.markdown("---")
st.markdown("### 🇧🇷 BRASIL")
row3_1, row3_2 = st.columns(2)

ewz, ewz_v = get_market_data("EWZ")
if ewz:
    row3_1.metric("EWZ (IBOV USD)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")
row3_2.write("⏱️ FEED: 5s | ESTILO TERMINAL BLOOMBERG")

