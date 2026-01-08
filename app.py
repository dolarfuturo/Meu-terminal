import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Configuração da Página - Estilo Terminal Bloomberg
st.set_page_config(page_title="BLOOMBERG TERMINAL | MACRO BRL", layout="wide")

# CSS para Estilo Bloomberg (Fundo Preto Médio, Texto Verde/Âmbar)
st.markdown("""
    <style>
    .main { background-color: #0A0A0A; }
    [data-testid="stHeader"] { background-color: #0A0A0A; }
    .stApp { background-color: #0A0A0A; color: #00FF00; }
    
    /* Estilização das métricas */
    [data-testid="stMetricValue"] { color: #FFB900 !important; font-family: 'Courier New', monospace; font-size: 32px !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-family: 'Arial'; font-weight: bold; }
    
    /* Blocos de Projeção de Futuro */
    .bloomberg-box {
        border: 1px solid #333333;
        padding: 20px;
        background-color: #111111;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 10px;
    }
    .label-min { color: #FF4B4B; font-weight: bold; font-size: 14px; }
    .label-justo { color: #00FF00; font-weight: bold; font-size: 14px; }
    .label-max { color: #0080FF; font-weight: bold; font-size: 14px; }
    .price-future { color: #FFFFFF; font-size: 28px; font-family: 'Courier New'; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ENTRADA DE VARIÁVEIS (NÚMEROS INPUT) ---
st.sidebar.markdown("### ⚙️ CONFIGURAÇÃO DE SPREAD")
v_min = st.sidebar.number_input("Variável Mínima (Pts)", value=22.0, step=0.5)
v_justo = st.sidebar.number_input("Variável Preço Justo (Pts)", value=31.0, step=0.5)
v_max = st.sidebar.number_input("Variável Máxima (Pts)", value=42.0, step=0.5)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="2d", interval="1m")
        return df
    except:
        return pd.DataFrame()

# --- COLETA DE DADOS ---
spot_df = get_data("BRL=X")
dxy_df = get_data("DX-Y.NYB")
ewz_df = get_data("EWZ")

if not spot_df.empty:
    # 1. Dados Dólar Spot
    spot_at = spot_df['Close'].iloc[-1]
    spot_16h = spot_df['Close'].iloc[0] # Referência do fechamento anterior
    var_spot = ((spot_at - spot_16h) / spot_16h) * 100

    # Cabeçalho do Terminal
    st.markdown(f"**USD/BRL SPOT** | <span style='color:#FFB900'>REF 16H: {spot_16h:.4f}</span>", unsafe_allow_html=True)
    st.divider()

    # --- LINHA 1: MERCADO GLOBAL (SPOT, DXY, EWZ) ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("DÓLAR SPOT", f"{spot_at:.4f}", f"{var_spot:.2f}%")

    with c2:
        if not dxy_df.empty:
            dxy_at = dxy_df['Close'].iloc[-1]
            dxy_16h = dxy_df['Close'].iloc[0]
            var_dxy = ((dxy_at - dxy_16h) / dxy_16h) * 100
            st.metric("DXY INDEX", f"{dxy_at:.2f}", f"{var_dxy:.2f}%")

    with c3:
        if not ewz_df.empty:
            ewz_at = ewz_df['Close'].iloc[-1]
            ewz_ant = ewz_df['Close'].iloc[0] # Fechamento anterior NY
            var_ewz = ((ewz_at - ewz_ant) / ewz_ant) * 100
            st.metric("EWZ (MSCI BRAZIL)", f"{ewz_at:.2f}", f"{var_ewz:.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # --- LINHA 2: PROJEÇÕES DE FUTURO (SPOT + VARIÁVEIS) ---
    st.markdown("### 🟢 PROJEÇÕES DE DÓLAR FUTURO")
    
    # Cálculo: Spot + (Variável / 1000)
    f_min = spot_at + (v_min / 1000)
    f_justo = spot_at + (v_justo / 1000)
    f_max = spot_at + (v_max / 1000)

    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown(f"""
            <div class="bloomberg-box">
                <p class="label-min">FUTURO MÍNIMA (Spot + {v_min})</p>
                <p class="price-future">{f_min:.4f}</p>
            </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown(f"""
            <div class="bloomberg-box">
                <p class="label-justo">PREÇO JUSTO (Spot + {v_justo})</p>
                <p class="price-future" style="color:#00FF00;">{f_justo:.4f}</p>
            </div>
        """, unsafe_allow_html=True)

    with p3:
        st.markdown(f"""
            <div class="bloomberg-box">
                <p class="label-max">FUTURO MÁXIMA (Spot + {v_max})</p>
                <p class="price-future">{f_max:.4f}</p>
            </div>
        """, unsafe_allow_html=True)

    # Gráfico Rápido Intradiário (Opcional)
    st.line_chart(spot_df['Close'], height=200)

else:
    st.error("SINAL INTERROMPIDO: VERIFIQUE A CONEXÃO COM O YAHOO FINANCE.")

# Refresh na Sidebar
if st.sidebar.button('🔄 ACTUALIZAR AGORA'):
    st.rerun()
