import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="BLOOMBERG LIVE | DUAL SPOT", layout="wide")

# Inicializa variáveis de memória
if 'history' not in st.session_state: st.session_state.history = []
if 'spot_ref_locked' not in st.session_state: st.session_state.spot_ref_locked = None

refresh_interval = 2 

# CSS Estilo Bloomberg
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] { background-color: #000000; }
    [data-testid="stMetricValue"] { color: #FFB900 !important; font-family: 'Courier New', monospace; font-size: 28px !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase; }
    .frp-box { border: 1px solid #333333; padding: 15px; background-color: #000000; text-align: center; }
    .spread-box { border: 1px dashed #555555; padding: 10px; background-color: #111111; text-align: center; margin-bottom: 10px; }
    .price-text { font-size: 26px; font-family: 'Courier New'; font-weight: bold; }
    .history-table { width: 100%; border-collapse: collapse; font-family: 'Courier New'; font-size: 14px; margin-top: 10px; }
    .history-table td, .history-table th { border-bottom: 1px solid #222; padding: 8px; text-align: left; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar.expander("⚙️ AJUSTAR PONTOS FRP", expanded=False):
    v_min = st.number_input("Mínima FRP", value=22.0)
    v_justo = st.number_input("Justo FRP", value=31.0)
    v_max = st.number_input("Máxima FRP", value=42.0)

def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        return data if not data.empty else pd.DataFrame()
    except: return pd.DataFrame()

placeholder = st.empty()

with placeholder.container():
    full_df = get_live_data("BRL=X")
    dxy_df = yf.download("DX-Y.NYB", period="1d", interval="1m", progress=False)
    ewz_df = yf.download("EWZ", period="1d", interval="1m", progress=False)

    if not full_df.empty:
        # Preço Atual Real-Time
        spot_at = float(full_df['Close'].iloc[-1])
        
        # Lógica de Captura das 15:59
        try:
            # Filtra o horário exato de fechamento do pregão regular
            lock_data = full_df.between_time('15:58', '16:05')
            if not lock_data.empty:
                st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[0])
        except:
            pass
        
        # Dashboard Principal - 4 COLUNAS
        c1, c2, c3, c4 = st.columns(4)
        
        # Coluna 1: O Spot Travado (Âncora)
        ref_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else float(full_df['Open'].iloc[0])
        label_ref = "SPOT 15:59 (LOCK)" if st.session_state.spot_ref_locked else "SPOT OPEN (REF)"
        c1.metric(label_ref, f"{ref_val:.4f}")

        # Coluna 2: O Spot Normal (Oscilando)
        var_vs_ref = ((spot_at - ref_val) / ref_val) * 100
        c2.metric("SPOT ATUAL", f"{spot_at:.4f}", f"{var_vs_ref:.2f}%")
        
        # Colunas 3 e 4: Macro
        if not dxy_df.empty:
            c3.metric("DXY INDEX", f"{float(dxy_df['Close'].iloc[-1]):.2f}")
        if not ewz_df.empty:
            c4.metric("EWZ (BRAZIL)", f"{float(ewz_df['Close'].iloc[-1]):.2f}")

        # Histórico de Tape Reading (Só adiciona se o preço ATUAL mudar)
        time_now = datetime.now().strftime("%H:%M:%S")
        if not st.session_state.history or st.session_state.history[0]['Preço'] != spot_at:
            st.session_state.history.insert(0, {'Hora': time_now, 'Preço': spot_at})
            st.session_state.history = st.session_state.history[:5]

        # Spread e Projeções (Mantendo a lógica anterior)
        v_dxy = ((float(dxy_df['Close'].iloc[-1]) - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0])) * 100 if not dxy_df.empty else 0
        v_ewz = ((float(ewz_df['Close'].iloc[-1]) - float(ewz_df['Open'].iloc[0])) / float(ewz_df['Open'].iloc[0])) * 100 if not ewz_df.empty else 0
        spread = v_dxy - v_ewz
        cor_s = "#00FF00" if spread >= 0 else "#FF0000"
        st.markdown(f'<div class="spread-box">SPREAD DXY-EWZ: <span style="color:{cor_s}; font-size:22px; font-weight:bold;">{spread:.2f}%</span></div>', unsafe_allow_html=True)

        p1, p2, p3 = st.columns(3)
        p1.markdown(f'<div class="frp-box"><span style="color:#FF0000;">MÍN (+{v_min})</span><div class="price-text" style="color:#FF0000;">{spot_at + (v_min/1000):.4f}</div></div>', unsafe_allow_html=True)
        p2.markdown(f'<div class="frp-box"><span style="color:#0080FF;">JUSTO (+{v_justo})</span><div class="price-text" style="color:#0080FF;">{spot_at + (v_justo/1000):.4f}</div></div>', unsafe_allow_html=True)
        p3.markdown(f'<div class="frp-box"><span style="color:#00FF00;">MÁX (+{v_max})</span><div class="price-text" style="color:#00FF00;">{spot_at + (v_max/1000):.4f}</div></div>', unsafe_allow_html=True)

        # Tabela de Histórico
        st.markdown("### 📜 ÚL
