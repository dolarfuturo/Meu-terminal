import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="BLOOMBERG LIVE | EWZ PRE-MARKET", layout="wide")

# 2. Memória da Sessão
if 'history' not in st.session_state: st.session_state.history = []
if 'spot_ref_locked' not in st.session_state: st.session_state.spot_ref_locked = None

# 3. Estilo Visual Bloomberg
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #FFB900 !important; font-family: 'Courier New', monospace; font-size: 28px !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase; }
    .frp-box { border: 1px solid #333333; padding: 15px; background-color: #000000; text-align: center; }
    .spread-box { border: 1px dashed #555555; padding: 10px; background-color: #111111; text-align: center; margin-bottom: 10px; margin-top: 10px; }
    .price-text { font-size: 26px; font-family: 'Courier New'; font-weight: bold; }
    .history-table { width: 100%; border-collapse: collapse; font-family: 'Courier New'; font-size: 14px; color: white; }
    .history-table td { border-bottom: 1px solid #222; padding: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 4. Menu Lateral
with st.sidebar:
    st.title("Configurações")
    v_min = st.number_input("Mínima FRP", value=22.0)
    v_justo = st.number_input("Justo FRP", value=31.0)
    v_max = st.number_input("Máxima FRP", value=42.0)
    if st.button("Resetar Trava 16h"):
        st.session_state.spot_ref_locked = None

# 5. Função de Coleta com Pre-market ativo
def get_live_data(ticker):
    try:
        # Busca dados com prepost=True para capturar o Pre-market
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data if not data.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

# 6. Renderização Principal
placeholder = st.empty()
with placeholder.container():
    full_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    now_br = datetime.now() - timedelta(hours=3)
    hora_br_str = now_br.strftime("%H:%M:%S")

    if not full_df.empty:
        spot_at = float(full_df['Close'].iloc[-1])
        
        # Trava Automática 16h
        try:
            lock_data = full_df.between_time('15:58', '16:02')
            if not lock_data.empty and st.session_state.spot_ref_locked is None:
                st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
        except:
            pass
        
        ref_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else float(full_df['Open'].iloc[0])

        # Grid de Métricas
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("SPOT 16:00 (REF)", f"{ref_val:.4f}")
        
        var_vs_ref = ((spot_at - ref_val) / ref_val) * 100
        seta = "▲" if var_vs_ref >= 0 else "▼"
        c2.metric("SPOT ATUAL", f"{spot_at:.4f}", f"{seta} {var_vs_ref:.2f}%")
        
        v_dxy = 0.0
        if not dxy_df.empty:
            d_at = float(dxy_df['Close'].iloc[-1])
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0])) * 100
            c3.metric("DXY INDEX", f"{d_at:.2f}", f"{v_dxy:.2f}%")
            
        v_ewz = 0.0
        label_ewz = "EWZ"
        if not ewz_df.empty:
            ewz_at = float(ewz_df['Close'].iloc[-1])
            is_pre = now_br.time() < datetime.strptime("11:30", "%H:%M").time()
            label_ewz = "EWZ PRE-MARKET" if is_pre else "EWZ REGULAR"
            
            # No pre-market compara com o fechamento anterior; no regular com a abertura
            ref_ewz = float(ewz_df['Close'].iloc[-2]) if is_pre else float(ewz_df['Open'].
