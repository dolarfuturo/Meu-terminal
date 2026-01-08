import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="BLOOMBERG LIVE | DUAL SPOT", layout="wide")

# 2. Memória da Sessão
if 'history' not in st.session_state: st.session_state.history = []
if 'spot_ref_locked' not in st.session_state: st.session_state.spot_ref_locked = None

refresh_interval = 2 

# 3. Estilo Visual Bloomberg
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

# 5. Função de Coleta
def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        return data if not data.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

# 6. Renderização
placeholder = st.empty()

with placeholder.container():
    full_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    if not full_df.empty:
        spot_at = float(full_df['Close'].iloc[-1])
        
        # Lógica de Trava das 16:00
        try:
            # Filtra o horário de fechamento (16h Brasília costuma ser 19h/21h UTC no Yahoo)
            # Buscamos o último registro disponível que se aproxime do fechamento
            lock_data = full_df.between_time('15:55', '16:05')
            if not lock_data.empty and st.session_state.spot_ref_locked is None:
                st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
        except:
            pass
        
        ref_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else float(full_df['Open'].iloc[0])
        label_ref = "SPOT 16:00 (LOCKED)" if st.session_state.spot_ref_locked else "SPOT OPEN (REF)"

        # Dashboard 4 Colunas
        c1, c2, c3, c4 = st.columns(4)
        
        # Coluna 1: Trava
        c1.metric(label_ref, f"{ref_val:.4f}")
        
        # Coluna 2: Atual com Direção
        var_vs_ref = ((spot_at - ref_val) / ref_val) * 100
        seta_dir = "▲" if var_vs_ref >= 0 else "▼"
        c2.metric("SPOT ATUAL", f"{spot_at:.4f}", f"{seta_dir} {var_vs_ref:.2f}%")
        
        # Coluna 3: DXY com variação
        if not dxy_df.empty:
            dxy_at = float(dxy_df['Close'].iloc[-1])
            dxy_var = ((dxy_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0])) * 100
            c3.metric("DXY INDEX", f"{dxy_at:.2f}", f"{dxy_var:.2f}%")
            
        # Coluna 4: EWZ com variação
        if not ewz_df.empty:
            ewz_at = float(ewz_df['Close'].iloc[-1])
            ewz_var = ((ewz_at - float(ewz_df['Open'].iloc[0])) / float(ewz_df['Open'].iloc[0])) * 100
            c4.metric("EWZ (BRAZIL)", f"{ewz_at:.2f}", f"{ewz_var:.2f}%")

        # Spread
        spread_val = (dxy_var if not dxy_df.empty else 0) - (ewz_var if not ewz_df.empty else 0)
        cor_spread = "#00FF00" if spread_val >= 0 else "#FF0000"
        st.markdown(f'<div class="spread-box">SPREAD DXY-EWZ: <span style="color:{cor_spread}; font-size:22px; font-weight:bold;">{spread_val:.2f}%</span></div>', unsafe_allow_html=True)

        # Projeções
        p1, p2, p3 = st.columns(3)
        p1.markdown(f'<div class="frp-box"><span style="color:#FF0000;">MÍN (+{v_min})</span><div class="price-text" style="color:#FF0000;">{spot_at + (v_
