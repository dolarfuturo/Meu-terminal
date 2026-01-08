import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página - Bloomberg Total Black
st.set_page_config(page_title="BLOOMBERG TERMINAL", layout="wide")

# CSS para remover partes brancas e ajustar cores FRP
st.markdown("""
    <style>
    /* Fundo Total Preto */
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #111111; }
    
    /* Ajuste de Métricas */
    [data-testid="stMetricValue"] { color: #FFB900 !important; font-family: 'Courier New', monospace; }
    
    /* Blocos de Projeção Customizados */
    .frp-box {
        border: 1px solid #333333;
        padding: 15px;
        background-color: #000000;
        border-radius: 5px;
        text-align: center;
        min-height: 120px;
    }
    .frp-min { color: #FF0000; font-weight: bold; font-size: 16px; }
    .frp-justo { color: #0080FF; font-weight: bold; font-size: 16px; }
    .frp-max { color: #00FF00; font-weight: bold; font-size: 16px; }
    .price-text { font-size: 24px; font-family: 'Courier New'; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("⌨️ CONFIG SPREAD")
v_min = st.sidebar.number_input("Mínima FRP (Pts)", value=22.0)
v_justo = st.sidebar.number_input("Justo FRP (Pts)", value=31.0)
v_max = st.sidebar.number_input("Máxima FRP (Pts)", value=42.0)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="2d", interval="1m")
        return df
    except: return pd.DataFrame()

# --- DADOS ---
spot_df = get_data("BRL=X")
dxy_df = get_data("DX-Y.NYB")
ewz_df = get_data("EWZ")

if not spot_df.empty:
    spot_at = spot_df['Close'].iloc[-1]
    spot_16h = spot_df['Close'].iloc[0]
    var_spot = ((spot_at - spot_16h) / spot_16h) * 100

    # Linha 1: Mercado
    c1, c2, c3 = st.columns(3)
    c1.metric("DOLAR SPOT", f"{spot_at:.4f}", f"{var_spot:.2f}%")
    
    if not dxy_df.empty:
        dxy_at = dxy_df['Close'].iloc[-1]
        c2.metric("DXY INDEX", f"{dxy_at:.2f}")
    
    if not ewz_df.empty:
        ewz_at = ewz_df['Close'].iloc[-1]
        c3.metric("EWZ (MSCI BRAZIL)", f"{ewz_at:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🟢 PROJEÇÕES FRP (SPOT + VARIÁVEIS)")

    # Cálculos
    f_min = spot_at + (v_min / 1000)
    f_justo = spot_at + (v_justo / 1000)
    f_max = spot_at + (v_max / 1000)

    # Linha 2: Projeções Coloridas
    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown(f'<div class="frp-box"><p class="frp-min">MÍNIMA FRP (+{v_min})</p><p class="price-text" style="color:#FF0000;">{f_min:.4f}</p></div>', unsafe_allow_html=True)

    with p2:
        st.markdown(f'<div class="frp-box"><p class="frp-justo">PREÇO JUSTO FRP (+{v_justo})</p><p class="price-text" style="color:#0080FF;">{f_justo:.4f}</p></div>', unsafe_allow_html=True)

    with p3:
        st.markdown(f'<div class="frp-box"><p class="frp-max">MÁXIMA FRP (+{v_max})</p><p class="price-text" style="color:#00FF00;">{f_max:.4f}</p></div>', unsafe_allow_html=True)

# Removido st.line_chart para eliminar a parte branca

if st.sidebar.button('ACTUALIZAR AGORA'):
    st.rerun()
