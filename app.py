import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="BLOOMBERG LIVE | DUAL SPOT", layout="wide")

# 2. Memória da Sessão para Histórico e Trava de Fechamento
if 'history' not in st.session_state: st.session_state.history = []
if 'spot_ref_locked' not in st.session_state: st.session_state.spot_ref_locked = None

refresh_interval = 2 

# 3. Estilo Visual Bloomberg (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] { background-color: #000000; }
    [data-testid="stMetricValue"] { color: #FFB900 !important; font-family: 'Courier New', monospace; font-size: 28px !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase; }
    .frp-box { border: 1px solid #333333; padding: 15px; background-color: #000000; text-align: center; }
    .spread-box { border: 1px dashed #555555; padding: 10px; background-color: #111111; text-align: center; margin-bottom: 10px; }
    .price-text { font-size: 26px; font-family: 'Courier New'; font-weight: bold; }
    .history-table { width: 100%; border-collapse: collapse; font-family: 'Courier New'; font-size: 14px; margin-top: 10px; color: white; }
    .history-table td, .history-table th { border-bottom: 1px solid #222; padding: 8px; text-align: left; }
    </style>
    """, unsafe_allow_html=True)

# 4. Menu Lateral
with st.sidebar.expander("⚙️ AJUSTAR PONTOS FRP", expanded=False):
    v_min = st.number_input("Mínima FRP", value=22.0)
    v_justo = st.number_input("Justo FRP", value=31.0)
    v_max = st.number_input("Máxima FRP", value=42.0)

# 5. Função de Coleta de Dados
def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        return data if not data.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

# 6. Execução Principal
placeholder = st.empty()

with placeholder.container():
    full_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    if not full_df.empty:
        # Preço Atual Spot
        spot_at = float(full_df['Close'].iloc[-1])
        
        # Lógica de Captura das 15:59 (Lock)
        try:
            # Busca o preço próximo ao fechamento das 16h (horário de mercado)
            lock_data = full_df.between_time('15:58', '16:05')
            if not lock_data.empty and st.session_state.spot_ref_locked is None:
                st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[0])
        except:
            pass
        
        # Definição da Referência (Lock das 16h ou Abertura)
        ref_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else float(full_df['Open'].iloc[0])
        label_ref = "SPOT 15:59 (LOCK)" if st.session_state.spot_ref_locked else "SPOT OPEN (REF)"

        # DASHBOARD DE MÉTRICAS (4 Colunas)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(label_ref, f"{ref_val:.4f}")
        
        var_vs_ref = ((spot_at - ref_val) / ref_val) * 100
        c2.metric("SPOT ATUAL", f"{spot_at:.4f}", f"{var_vs_ref:.2f}%")
        
        if not dxy_df.empty:
            c3.metric("DXY INDEX", f"{float(dxy_df['Close'].iloc[-1]):.2f}")
        if not ewz_df.empty:
            c4.metric("EWZ (BRAZIL)", f"{float(ewz_df['Close'].iloc[-1]):.2f}")

        # SPREAD DXY-EWZ
        v_dxy = ((float(dxy_df['Close
