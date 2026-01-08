import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="BLOOMBERG LIVE | SINC TV", layout="wide")

# 2. Inicialização da Memória
if 'history' not in st.session_state: st.session_state.history = []
if 'manual_lock' not in st.session_state: st.session_state.manual_lock = 5.3927

refresh_interval = 2 

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
    st.title("Sincronismo TV")
    st.session_state.manual_lock = st.number_input("Fechamento 16h (TV)", value=st.session_state.manual_lock, format="%.4f")
    st.divider()
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
    spot_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    if not spot_df.empty:
        spot_at = float(spot_df['Close'].iloc[-1])
        ref_val = st.session_state.manual_lock
        
        # AJUSTE DE HORÁRIO (UTC para Brasília -3h)
        # Se estiver no horário de verão, mude para -2
        hora_br = (datetime.now() - timedelta(hours=3)).strftime("%H:%M:%S")

        # Dashboard 4 Colunas
        c1, c2, c3, c4 = st.columns(4)
        
        c1.metric("FECHAMENTO 16H", f"{ref_val:.4f}")
        
        var_vs_ref = ((spot_at - ref_val) / ref_val) * 100
        seta = "▲" if var_vs_ref >= 0 else "▼"
        c2.metric("SPOT ATUAL", f"{spot_at:.4f}", f"{seta} {var_vs_ref:.2f}%")
        
        # DXY e EWZ com Cálculos de Variação
        v_dxy = 0.0
        if not dxy_df.empty:
            d_at = float(dxy_df['Close'].iloc[-1])
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0])) * 100
            c3.metric("DXY INDEX", f"{d_at:.2f}", f"{v_dxy:.2f}%")
        
        v_ewz = 0.0
        if not ewz_df.empty:
            e_at = float(ewz_df['Close'].iloc[-1])
            v_ewz = ((e_at - float(ewz_df['Open'].iloc[0])) / float(ewz_df['Open'].iloc[0])) * 100
            c4.metric("EWZ", f"{e_at:.2f}", f"{v_ewz:.2f}%")

        # SPREAD DXY-EWZ (O que faltava)
        spread = v_dxy - v_ewz
        cor_spread = "#00FF00" if spread >= 0 else "#FF0000"
        st.markdown(f'<div class="spread-box">SPREAD VARIÇÃO (DXY-EWZ): <span style="color:{cor_spread}; font-size:22px; font-weight:bold;">{spread:.2f}%</span></div>', unsafe_allow_html=True)

        # Projeções FRP
        p1, p2, p3 = st.columns(3)
        p1.markdown(f'<div class="frp-box"><span style="color:#FF0000;">MÍN (+{v_min})</span><br><span class="price-text" style="color:#FF0000;">{spot_at + (v_min/1000):.4f}</span></div>', unsafe_allow_html=True)
        p2.markdown(f'<div class="frp-box"><span style="color:#0080FF;">JUSTO (+{v_justo})</span><br><span class="price-text" style="color:#0080FF;">{spot_at + (v_justo/1000):.4f}</span></div>', unsafe_allow_html=True)
        p3.markdown(f'<div class="frp-box"><span style="color:#00FF00;">MÁX (+{v_max})</span><br><span class="price-text" style="color:#00FF00;">{spot_at + (v_max/1000):.4f}</span></div>', unsafe_allow_html=True)

        # Histórico com Hora de Brasília
        if not st.session_state.history or st.session_state.history[0]['Preço'] != spot_at:
            st.session_state.history.insert(0, {'Hora': hora_br, 'Preço': spot_at})
            st.session_state.history = st.session_state.history[:5]

        st.markdown("### 📜 ÚLTIMAS VARIAÇÕES SPOT (BR)")
        hist_html = "<table class='history-table'><tr><th>Hora (BR)</th><th>Preço</th><th>Sentido</th></tr>"
        for i, row in enumerate(st.session_state.history):
            s_seta = ""
            if i < len(st.session_state.history) - 1:
                if row['Preço'] > st.session_state.history[i+1]['Preço']: s_seta = "<span style='color:#00FF00;'>▲</span>"
                elif row['Preço'] < st.session_state.history[i+1]['Preço']: s_seta = "<span style='color:#FF0000;'>▼</span>"
            hist_html += f"<tr><td>{row['Hora']}</td><td>{row['Preço']:.4f}</td><td>{s_seta}</td></tr>"
        st.markdown(hist_html + "</table>", unsafe_allow_html=True)

time.sleep(refresh_interval)
st.rerun()
