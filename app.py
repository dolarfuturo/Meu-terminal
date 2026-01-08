import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="BLOOMBERG LIVE | TAPE READING", layout="wide")

# Inicializa o histórico na memória da sessão
if 'history' not in st.session_state:
    st.session_state.history = []

refresh_interval = 1 

# CSS Estilo Bloomberg
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #FFB900 !important; font-family: 'Courier New', monospace; font-size: 30px !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: 800 !important; text-transform: uppercase; }
    .frp-box { border: 1px solid #333333; padding: 15px; background-color: #000000; text-align: center; }
    .spread-box { border: 1px dashed #555555; padding: 10px; background-color: #111111; text-align: center; margin-bottom: 10px; }
    .price-text { font-size: 26px; font-family: 'Courier New'; font-weight: bold; }
    .history-table { width: 100%; border-collapse: collapse; font-family: 'Courier New'; font-size: 14px; margin-top: 10px; }
    .history-table td, .history-table th { border-bottom: 1px solid #222; padding: 8px; text-align: left; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar.expander("⚙️ AJUSTAR PONTOS FRP", expanded=False):
    v_min = st.number_input("Mínima FRP (Pts)", value=22.0)
    v_justo = st.number_input("Justo FRP (Pts)", value=31.0)
    v_max = st.number_input("Máxima FRP (Pts)", value=42.0)

def get_live_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        return df
    except: return pd.DataFrame()

placeholder = st.empty()

with placeholder.container():
    spot_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    if not spot_df.empty:
        spot_at = spot_df['Close'].iloc[-1].item()
        time_now = datetime.now().strftime("%H:%M:%S")
        
        if not st.session_state.history or st.session_state.history[0]['Preço'] != spot_at:
            st.session_state.history.insert(0, {'Hora': time_now, 'Preço': spot_at})
            st.session_state.history = st.session_state.history[:5]

        c1, c2, c3 = st.columns(3)
        var_spot = ((spot_at - spot_df['Open'].iloc[0]) / spot_df['Open'].iloc[0]) * 100
        c1.metric("DOLAR SPOT", f"{spot_at:.4f}", f"{var_spot:.2f}%")
        
        v_dxy = ((dxy_df['Close'].iloc[-1] - dxy_df['Open'].iloc[0]) / dxy_df['Open'].iloc[0]) * 100 if not dxy_df.empty else 0
        v_ewz = ((ewz_df['Close'].iloc[-1] - ewz_df['Open'].iloc[0]) / ewz_df['Open'].iloc[0]) * 100 if not ewz_df.empty else 0
        
        c2.metric("DXY INDEX", f"{dxy_df['Close'].iloc[-1].item():.2f}", f"{v_dxy:.2f}%")
        c3.metric("EWZ (BRAZIL)", f"{ewz_df['Close'].iloc[-1].item():.2f}", f"{v_ewz:.2f}%")

        spread = v_dxy - v_ewz
        cor_s = "#00FF00" if spread >= 0 else "#FF0000"
        st.markdown(f'<div class="spread-box">SPREAD DXY-EWZ: <span style="color:{cor_s}; font-size:22px; font-weight:bold;">{spread:.2f}%</span></div>', unsafe_allow_html=True)

        p1, p2, p3 = st.columns(3)
        p1.markdown(f'<div class="frp-box"><span style="color:#FF0000;">MÍN (+{v_min})</span><div class="price-text" style="color:#FF0000;">{spot_at + (v_min/1000):.4f}</div></div>', unsafe_allow_html=True)
        p2.markdown(f'<div class="frp-box"><span style="color:#0080FF;">JUSTO (+{v_justo})</span><div class="price-text" style="color:#0080FF;">{spot_at + (v_justo/1000):.4f}</div></div>', unsafe_allow_html=True)
        p3.markdown(f'<div class="frp-box"><span style="color:#00FF00;">MÁX (+{v_max})</span><div class="price-text" style="color:#00FF00;">{spot_at + (v_max/1000):.4f}</div></div>', unsafe_allow_html=True)

        st.markdown("### 📜 ÚLTIMAS VARIAÇÕES SPOT")
        hist_html = "<table class='history-table'><thead><tr><th>Hora</th><th>Preço</th><th>Sentido</th></tr></thead><tbody>"
        for i in range(len(st.session_state.history)):
            row = st.session_state.history[i]
            sentido = ""
            if i < len(st.session_state.history) - 1:
                if row['Preço'] > st.session_state.history[i+1]['Preço']: sentido = "<span style='color:#00FF00;'>▲</span>"
                elif row['Preço'] < st.session_state.history[i+1]['Preço']: sentido = "<span style='color:#FF0000;'>▼</span>"
            hist_html += f"<tr><td>{row['Hora']}</td><td>{row['Preço']:.4f}</td><td>{sentido}</td></tr>"
        st.markdown(hist_html + "</tbody></table>", unsafe_allow_html=True)

time.sleep(refresh_interval)
st.rerun()
