import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Configuração da Página - Estilo Terminal Bloomberg
st.set_page_config(page_title="BLOOMBERG TERMINAL | MACRO", layout="wide")

# CSS para Estilo Bloomberg (Fundo Preto, Texto Verde/Âmbar)
st.markdown("""
    <style>
    .main { background-color: #000000; }
    [data-testid="stHeader"] { background-color: #000000; }
    .stApp { background-color: #000000; color: #00FF00; }
    
    /* Estilização das métricas */
    [data-testid="stMetricValue"] { color: #FFB900 !important; font-family: 'Courier New', monospace; font-size: 32px !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-family: 'Arial'; font-weight: bold; }
    
    /* Blocos de Projeção */
    .bloomberg-box {
        border: 1px solid #333333;
        padding: 15px;
        background-color: #111111;
        border-radius: 2px;
        text-align: center;
    }
    .label-min { color: #FF4B4B; font-weight: bold; }
    .label-justo { color: #00FF00; font-weight: bold; }
    .label-max { color: #0080FF; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (CONFIGURAÇÕES) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Bloomberg_logo.svg/1280px-Bloomberg_logo.svg.png", width=150)
st.sidebar.markdown("---")
st.sidebar.subheader("PARÂMETROS DE AJUSTE")

v_min = st.sidebar.number_input("Var Mínima (Pts)", value=22.0, step=0.5)
v_justo = st.sidebar.number_input("Var Preço Justo (Pts)", value=31.0, step=0.5)
v_max = st.sidebar.number_input("Var Máxima (Pts)", value=42.0, step=0.5)

def get_data(ticker, interval="1m"):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="2d", interval=interval)
        return df
    except:
        return pd.DataFrame()

# --- COLETA DE DADOS ---
with st.spinner('CONECTANDO AO SERVIDOR...'):
    spot_df = get_data("BRL=X")
    dxy_df = get_data("DX-Y.NYB")
    ewz_df = get_data("EWZ")

if not spot_df.empty:
    # 1. Dados Dólar Spot
    spot_at = spot_df['Close'].iloc[-1]
    spot_16h = spot_df['Close'].iloc[0] # Ref 16h anterior
    var_spot = ((spot_at - spot_16h) / spot_16h) * 100

    # 2. Cabeçalho Bloomberg
    t_now = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"**BRL CURRENCY** | <span style='color:#FFB900'>TIME: {t_now}</span> | **MARKET: OPEN**", unsafe_allow_html=True)
    st.divider()

    # --- LINHA 1: MERCADO GLOBAL ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("DÓLAR SPOT", f"{spot_at:.4f}", f"{var_spot:.2f}%")
        st.caption(f"Ref. 16h: {spot_16h:.4f}")

    with c2:
        if not dxy_df.empty:
            dxy_at = dxy_df['Close'].iloc[-1]
            dxy_16h = dxy_df['Close'].iloc[0]
            var_dxy = ((dxy_at - dxy_16h) / dxy_16h) * 100
            st.metric("DXY INDEX", f"{dxy_at:.2f}", f"{var_dxy:.2f}%")
            st.caption(f"Ref. 16h: {dxy_16h:.2f}")

    with c3:
        if not ewz_df.empty:
            ewz_at = ewz_df['Close'].iloc[-1]
            ewz_ant = ewz_df['Close'].iloc[0]
            var_ewz = ((ewz_at - ewz_ant) / ewz_ant) * 10
