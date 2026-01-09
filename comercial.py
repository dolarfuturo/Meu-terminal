import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="TERMINAL DECISÃO", layout="wide")

# CSS PARA FOCO EM TOMADA DE DECISÃO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #050505; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 2rem !important; max-width: 600px !important; margin: auto; }
    
    .status-box { padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 1px solid #333; }
    .status-caro { background-color: rgba(255, 0, 0, 0.1); border: 2px solid #FF0000; color: #FF0000; }
    .status-barato { background-color: rgba(0, 255, 0, 0.1); border: 2px solid #00FF00; color: #00FF00; }
    .status-neutro { background-color: rgba(0, 128, 255, 0.1); border: 2px solid #0080FF; color: #0080FF; }

    .label { color: #888; font-size: 14px; margin-bottom: 5px; }
    .value-big { font-size: 42px; font-weight: bold; margin-bottom: 10px; }
    .equil-box { background: #111; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center; border: 1px solid #222; }
    
    .grid-info { display: flex; justify-content: space-between; gap: 10px; margin-top: 20px; }
    .grid-item { background: #111; padding: 10px; width: 32%; text-align: center; border-radius: 4px; border: 1px solid #222; }
    .pos { color: #00FF00; }
    .neg { color: #FF0000; }
</style>
""", unsafe_allow_html=True)

def get_market_info():
    try:
        s_df = yf.download("BRL=X", period="1d", interval="1m", progress=False)
        d_df = yf.download("DX-Y.NYB", period="1d", interval="1m", progress=False)
        e_df = yf.download("EWZ", period="1d", interval="1m", progress=False, prepost=True)
        s_at = float(s_df['Close'].iloc[-1])
        d_v = ((float(d_df['Close'].iloc[-1]) - float(yf.Ticker("DX-Y.NYB").fast_info.previous_close)) / float(yf.Ticker("DX-Y.NYB").fast_info.previous_close) * 100)
        e_v = ((float(e_df['Close'].iloc[-1]) - float(yf.Ticker("EWZ").fast_info.previous_close)) / float(yf.Ticker("EWZ").fast_info.previous_close) * 100)
        return s_at, (d_v - e_v)
    except:
        return 0, 0

with st.expander("⚙️ CONFIGURAR REFERÊNCIA"):
    ref_ajuste = st.number_input("REFERÊNCIA DO DIA", value=5.4000, format="%.4f")

placeholder = st.empty()

while True:
    spot, spread = get_market_info()
    justo = ref_ajuste * (1 + (spread/100))
    distancia = (spot - justo) * 1000 

    with placeholder.container():
        if distancia > 15:
            st.markdown('<div class="status-box status-caro"><div style="font-size:12px">STATUS ATUAL</div><div style="font-size:24px; font-weight:bold">DÓLAR CARO (VENDA)</div></div>', unsafe_allow_html=True)
        elif distancia < -15:
            st.markdown('<div class="status-box status-barato"><div style="font-size:12px">STATUS ATUAL</div><div style="font-size:24px; font-weight:bold">DÓLAR BARATO (COMPRA)</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box status-neutro"><div style="font-size:12px">STATUS ATUAL</div><div style="font-size:24px; font-weight:bold">ZONA DE EQUILÍBRIO</div></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="equil-box"><div class="label">PREÇO SPOT AGORA</div><div class="value-big">{spot:.4f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="equil-box" style="border-color:#FFB900"><div class="label" style="color:#FFB900">MÉDIA DE EQUILÍBRIO (JUSTO)</div><div class="value-big" style="color:#FFB900">{justo:.4f}</div></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="grid-info">
            <div class="grid-item"><div class="label">DISTÂNCIA</div><div class="{"neg" if distancia > 0 else "pos"}" style="font-size:18px; font-weight:bold">{distancia:+.1f} PTS</div></div>
            <div class="grid-item"><div class="label">GLOBAL (SPR)</div><div class="{"pos" if spread > 0 else "neg"}" style="font-size:18px; font-weight:bold">{spread:+.2f}%</div></div>
            <div class="grid-item"><div class="label">TENDÊNCIA</div><div style="font-size:18px; font-weight:bold">{"ALTA" if spread > 0 else "BAIXA"}</div></div>
        </div>
        """, unsafe_allow_html=True)
    time.sleep(2)

