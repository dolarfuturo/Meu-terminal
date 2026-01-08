import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página - Bloomberg Total Black
st.set_page_config(page_title="TERMINAL BLOOMBERG | SPREAD", layout="wide")

# CSS Bloomberg Style
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] { background-color: #000000; }
    
    [data-testid="stMetricLabel"] { 
        color: #FFFFFF !important; 
        font-size: 16px !important; 
        font-weight: 800 !important; 
        text-transform: uppercase;
    }
    
    [data-testid="stMetricValue"] { 
        color: #FFB900 !important; 
        font-family: 'Courier New', monospace; 
        font-size: 30px !important; 
    }
    
    .frp-box {
        border: 1px solid #333333;
        padding: 15px;
        background-color: #000000;
        border-radius: 5px;
        text-align: center;
    }
    
    .spread-box {
        border: 1px dashed #555555;
        padding: 10px;
        background-color: #111111;
        text-align: center;
        margin: 10px 0;
    }

    .price-text { font-size: 28px; font-family: 'Courier New'; font-weight: bold; margin-top: 5px; }
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: VARIÁVEIS ESCONDIDAS ---
st.sidebar.title("⌨️ COMANDOS")

with st.sidebar.expander("⚙️ AJUSTAR PONTOS FRP", expanded=False):
    v_min = st.number_input("Mínima FRP (Pts)", value=22.0)
    v_justo = st.number_input("Justo FRP (Pts)", value=31.0)
    v_max = st.number_input("Máxima FRP (Pts)", value=42.0)

if st.sidebar.button('🔄 REFRESH'):
    st.rerun()

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="2d", interval="1m")
        return df
    except: return pd.DataFrame()

# --- COLETA DE DADOS ---
spot_df = get_data("BRL=X")
dxy_df = get_data("DX-Y.NYB")
ewz_df = get_data("EWZ")

if not spot_df.empty:
    spot_at = spot_df['Close'].iloc[-1]
    spot_ref = spot_df['Close'].iloc[0]
    var_spot = ((spot_at - spot_ref) / spot_ref) * 100
    
    # --- LINHA 1: MERCADO ---
    st.markdown("### 📊 DASHBOARD")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("DOLAR SPOT", f"{spot_at:.4f}", f"{var_spot:.2f}%")
    
    var_dxy = 0.0
    with c2:
        if not dxy_df.empty:
            dxy_at = dxy_df['Close'].iloc[-1]
            dxy_ref = dxy_df['Close'].iloc[0]
            var_dxy = ((dxy_at - dxy_ref) / dxy_ref) * 100
            st.metric("DXY INDEX", f"{dxy_at:.2f}", f"{var_dxy:.2f}%")

    var_ewz = 0.0
    with c3:
        if not ewz_df.empty:
            ewz_at
