import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DO TERMINAL
st.set_page_config(page_title="TERMINAL QUANT", layout="wide")

# 2. ESTILO CSS (DARK MODE COMPLETO)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin: auto; }
    .main-title { font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 15px; }
    .asset-row { display: flex; gap: 20px; margin-bottom: 4px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 130px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    
    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
    .frp-box { margin-top: 10px; display: flex; flex-direction: column; gap: 2px; border-left: 2px solid #222; padding-left: 15px; }
    .frp-item { display: flex; gap: 25px; font-size: 13px; color: #666; }
</style>
""", unsafe_allow_html=True)

# 3. INPUTS NO POPOVER
with st.popover("⚙️ AJUSTAR PARÂMETROS"):
    v_aj = st.number_input("AJUSTE DÓLAR", value=5.3900, format="%.4f")
    v_ptax_m = st.number_input("PTAX", value=5.3850, format="%.4f")
    v_aj_win = st.number_input("AJUSTE ÍNDICE", value=130500, step=5)
    ancora_ativa = st.radio("ÂNCORA DÓLAR:", ["AJUSTE", "PTAX"], horizontal=True)

# 4. FUNÇÃO BUSCA DADOS
@st.cache_data(ttl=5)
def get_data(ticker):
    try:
        data = yf.Ticker(ticker).history(period="2d")
        return data['Close'].iloc[-1], ((data['Close'].iloc[-1]/data['Close'].iloc[-2])-1)*100
    except: return 0, 0

# BUSCA DADOS
p_dxy, v_dxy = get_data("DX-Y.NYB")
p_spot, v_spot = get_data("USDBRL=X")
p_win, v_win = get_data("^BVSP")

# 5. EXIBIÇÃO TERMINAL
st.markdown('<div class="main-title">TERMINAL DE CÂMBIO & ÍNDICE</div>', unsafe_allow_html=True)

# DXY (MUNDO)
st.markdown(f'<div class="asset-row"><div class="name">DXY</div><div class="price">{p_dxy:.2f}</div><div class="var {"pos" if v_dxy >=0 else "neg"}">{v_dxy:.2f}%</div></div>', unsafe_allow_html=True)

# DÓLAR SPOT
ref_dolar = v_aj if ancora_ativa == "AJUSTE" else v_ptax_m
st.markdown(f'<div class="asset-row"><div class="name">DÓLAR SPOT</div><div class="price">{p_spot:.4f}</div><div class="var {"pos" if p_spot >= ref_dolar else "neg"}">{((p_spot/ref_dolar)-1)*100:.2f}%</div></div>', unsafe_allow_html=True)

# 6. CALCULADORA DE DISTORÇÃO (O SEU +22, +31, +42)
st.markdown('<div class="frp-box">', unsafe_allow_html=True)
for pts in [22, 31, 42]:
    alvo_alta = ref_dolar + (pts/1000)
    alvo_baixa = ref_dolar - (pts/1000)
    st.markdown(f'<div class="frp-item"><span>+{pts} PTS: {alvo_alta:.4f}</span> <span style="color:#444">|</span> <span>-{pts} PTS: {alvo_baixa:.4f}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 7. MINI ÍNDICE (LÓGICA IBOV + 300/600/1200)
st.markdown('<div class="trava-orange">SINAIS MINI ÍNDICE (WIN)</div>', unsafe_allow_html=True)
st.markdown(f'<div class="asset-row"><div class="name">WIN FUT</div><div class="price">{p_win:,.0f}</div><div class="var {"pos" if p_win >= v_aj_win else "neg"}">{((p_win/v_aj_win)-1)*100:.2f}%</div></div>', unsafe_allow_html=True)

st.markdown('<div class="frp-box">', unsafe_allow_html=True)
for pts_win in [300, 600, 1200]:
    st.markdown(f'<div class="frp-item"><span>DIST {pts_win} PTS: {v_aj_win+pts_win:,.0f} / {v_aj_win-pts_win:,.0f}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# AUTO-REFRESH
time.sleep(5)
st.rerun()
