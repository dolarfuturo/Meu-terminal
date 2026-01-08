import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuração da Página (Deve ser a primeira linha)
st.set_page_config(page_title="TERMINAL BLOOMBERG", layout="wide")

# 2. Estilo CSS
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] { background-color: #000000; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-size: 16px !important; font-weight: 800 !important; }
    [data-testid="stMetricValue"] { color: #FFB900 !important; font-family: 'Courier New', monospace; font-size: 30px !important; }
    .frp-box { border: 1px solid #333333; padding: 15px; background-color: #000000; border-radius: 5px; text-align: center; }
    .spread-box { border: 1px dashed #555555; padding: 10px; background-color: #111111; text-align: center; margin: 10px 0; }
    .price-text { font-size: 28px; font-family: 'Courier New'; font-weight: bold; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("⌨️ COMANDOS")
with st.sidebar.expander("⚙️ AJUSTAR PONTOS FRP", expanded=False):
    v_min = st.number_input("Mínima FRP", value=22.0)
    v_justo = st.number_input("Justo FRP", value=31.0)
    v_max = st.number_input("Máxima FRP", value=42.0)

# Função de busca com tratamento de erro
def get_market_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="15m", progress=False)
        if data.empty:
            return None
        return data
    except:
        return None

# --- PROCESSAMENTO ---
spot_data = get_market_data("USDBRL=X") # Usando USDBRL para maior estabilidade
dxy_data = get_market_data("DX-Y.NYB")
ewz_data = get_market_data("EWZ")

# Verificação de segurança para não dar tela preta
if spot_data is not None and not spot_data.empty:
    spot_at = float(spot_data['Close'].iloc[-1])
    spot_ref = float(spot_data['Close'].iloc[0])
    var_spot = ((spot_at - spot_ref) / spot_ref) * 100

    # DASHBOARD
    st.markdown("### 📊 DASHBOARD")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("DOLAR SPOT", f"{spot_at:.4f}", f"{var_spot:.2f}%")
    
    var_dxy = 0.0
    with c2:
        if dxy_data is not None:
            dxy_at = float(dxy_data['Close'].iloc[-1])
            dxy_ref = float(dxy_data['Close'].iloc[0])
            var_dxy = ((dxy_at - dxy_ref) / dxy_ref) * 100
            st.metric("DXY INDEX", f"{dxy_at:.2f}", f"{var_dxy:.2f}%")

    var_ewz = 0.0
    with c3:
        if ewz_data is not None:
            ewz_at = float(ewz_data['Close'].iloc[-1])
            ewz_ref = float(ewz_data['Close'].iloc[0])
            var_ewz =
