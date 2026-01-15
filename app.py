import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DO TERMINAL
st.set_page_config(page_title="TERMINAL QUANT DÓLAR", layout="wide")

# 2. ESTILO CSS (DARK MODE FIEL AO SEU MODELO)
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
    
    .frp-box { margin-top: 15px; display: flex; flex-direction: column; gap: 4px; border-left: 2px solid #333; padding-left: 15px; }
    .frp-item { display: flex; gap: 25px; font-size: 14px; color: #BBB; }
    .stPopover button { background-color: #111 !important; color: #666 !important; border: 1px solid #222 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

# 3. INPUTS NO POPOVER (PARÂMETROS QUE VOCÊ USA)
with st.popover("⚙️ AJUSTAR PARÂMETROS"):
    v_aj = st.number_input("AJUSTE ANTERIOR", value=5.3900, format="%.4f")
    v_ptax_m = st.number_input("PTAX OFICIAL", value=5.3850, format="%.4f")
    ancora_escolhida = st.radio("USAR COMO ÂNCORA:", ["AJUSTE", "PTAX"], horizontal=True)

# 4. BUSCA DE DADOS (SPOT E DXY)
@st.cache_data(ttl=5)
def get_market_data():
    try:
        # Busca Dólar Spot e DXY
        dolar = yf.Ticker("USDBRL=X").history(period="2d")
        dxy = yf.Ticker("DX-Y.NYB").history(period="2d")
        
        spot_price = dolar['Close'].iloc[-1]
        dxy_price = dxy['Close'].iloc[-1]
        dxy_var = ((dxy['Close'].iloc[-1] / dxy['Close'].iloc[-2]) - 1) * 100
        
        return spot_price, dxy_price, dxy_var
    except:
        return 5.3900, 105.00, 0.0

p_spot, p_dxy, v_dxy = get_market_data()

# Definição da Âncora para o cálculo de distorção
ref_atual = v_aj if ancora_escolhida == "AJUSTE" else v_ptax_m

# 5. EXIBIÇÃO DXY E SPOT
st.markdown(f"""
<div class="asset-row">
    <div class="name">DXY (MUNDO)</div>
    <div class="price">{p_dxy:.2f}</div>
    <div class="var {'pos' if v_dxy >= 0 else 'neg'}">{v_dxy:.2f}%</div>
</div>
<div class="asset-row">
    <div class="name">DÓLAR SPOT</div>
    <div class="price">{p_spot:.4f}</div>
    <div class="var {'pos' if p_spot >= ref_atual else 'neg'}">
        {((p_spot/ref_atual)-1)*100:.2f}%
    </div>
</div>
""", unsafe_allow_html=True)

# 6. ESCADA DE DISTORÇÃO (O SEU +22, +31, +42)
st.markdown(f'<div style="color: #666; font-size: 12px; margin-top: 20px;">DISTORÇÕES SOBRE {ancora_escolhida}</div>', unsafe_allow_html=True)
st.markdown('<div class="frp-box">', unsafe_allow_html=True)

niveis = [22, 31, 42]
for pts in niveis:
    p_alta = ref_atual + (pts / 1000)
    p_baixa = ref_atual - (pts / 1000)
    
    # Verifica se o preço atual já atingiu o nível
    cor_alta = "color: #FF8C00;" if p_spot >= p_alta else ""
    cor_baixa = "color: #0080FF;" if p_spot <= p_baixa else ""
    
    st.markdown(f"""
    <div class="frp-item">
        <span style="{cor_alta}">+{pts} PTS: {p_alta:.4f}</span>
        <span style="color: #333">|</span>
        <span style="{cor_baixa}">-{pts} PTS: {p_baixa:.4f}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 7. AUTO-REFRESH (PARA RODAR NO CELULAR)
time.sleep(5)
st.rerun()
