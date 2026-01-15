import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DO TERMINAL
st.set_page_config(page_title="QUANT TERMINAL PRO", layout="wide")

# 2. ESTILO CSS (DARK INSTITUCIONAL)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 600px !important; margin: auto; }
    .main-title { font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 15px; }
    .asset-row { display: flex; gap: 20px; margin-bottom: 4px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 130px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    
    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .ora { color: #FF8C00 !important; }
    
    .ref-box { background: #0A0A0A; border: 1px solid #222; padding: 12px; border-radius: 5px; margin-top: 15px; }
    .label-ref { font-size: 12px; color: #444; margin-bottom: 5px; }
    .frp-box { margin-top: 10px; display: flex; flex-direction: column; gap: 4px; border-left: 2px solid #333; padding-left: 15px; }
    .frp-item { display: flex; gap: 25px; font-size: 14px; color: #BBB; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">TERMINAL DE PARIDADE & REF INSTITUCIONAL</div>', unsafe_allow_html=True)

# 3. INPUTS NO POPOVER
with st.popover("⚙️ AJUSTAR PARÂMETROS"):
    v_aj = st.number_input("AJUSTE ANTERIOR", value=5.3900, format="%.4f")
    v_ptax_m = st.number_input("PTAX OFICIAL", value=5.3850, format="%.4f")
    v_ibov_f = st.number_input("FECH. IBOV", value=130000, step=10)
    ancora_escolhida = st.radio("ÂNCORA DÓLAR:", ["AJUSTE", "PTAX"], horizontal=True)

# 4. BUSCA DE DADOS (DXY, EWZ, SPOT)
@st.cache_data(ttl=5)
def get_market_data():
    try:
        dolar = yf.Ticker("USDBRL=X").history(period="2d")
        dxy = yf.Ticker("DX-Y.NYB").history(period="2d")
        ewz = yf.Ticker("EWZ").history(period="2d")
        
        spot_p = dolar['Close'].iloc[-1]
        dxy_p = dxy['Close'].iloc[-1]
        dxy_v = ((dxy['Close'].iloc[-1] / dxy['Close'].iloc[-2]) - 1) * 100
        ewz_v = ((ewz['Close'].iloc[-1] / ewz['Close'].iloc[-2]) - 1) * 100
        
        return spot_p, dxy_p, dxy_v, ewz_v
    except:
        return 5.3900, 105.00, 0.0, 0.0

p_spot, p_dxy, v_dxy, v_ewz = get_market_data()
ref_atual = v_aj if ancora_escolhida == "AJUSTE" else v_ptax_m

# 5. CÁLCULO PREÇO JUSTO (PARIDADE MUNDO)
# DXY sobe -> Dólar sobe | EWZ cai (Bolsa cai) -> Dólar sobe
paridade_mundo = v_dxy - v_ewz
preco_justo = ref_atual * (1 + (paridade_mundo / 100))

# 6. EXIBIÇÃO RADAR MUNDO
st.markdown(f"""
<div class="asset-row">
    <div class="name">DXY (MUNDO)</div>
    <div class="price">{p_dxy:.2f}</div>
    <div class="var {'pos' if v_dxy >= 0 else 'neg'}">{v_dxy:.2f}%</div>
</div>
<div class="asset-row">
    <div class="name">EWZ (IBOV NY)</div>
    <div class="price">--</div>
    <div class="var {'pos' if v_ewz >= 0 else 'neg'}">{v_ewz:.2f}%</div>
</div>
""", unsafe_allow_html=True)

# 7. PREÇO JUSTO E SPOT
st.markdown(f"""
<div class="ref-box">
    <div class="label-ref">PREÇO JUSTO (PARIDADE)</div>
    <div style="font-size: 22px; font-weight: bold; color: #0080FF;">{preco_justo:.4f}</div>
</div>
<div class="asset-row" style="margin-top:15px;">
    <div class="name">DÓLAR SPOT</div>
    <div class="price" style="color:#FFF; font-size:24px;">{p_spot:.4f}</div>
    <div class="var {'pos' if p_spot >= preco_justo else 'neg'}" style="font-size:24px;">
        {(p_spot - preco_justo)*1000:.1f} PTS
    </div>
</div>
""", unsafe_allow_html=True)

# 8. REGIÕES DE CORREÇÃO (ESCADA +22, +31, +42)
st.markdown(f'<div style="color: #444; font-size: 12px; margin-top: 25px;">REGIÕES DE EXAUSTÃO / REF INSTITUCIONAL</div>', unsafe_allow_html=True)
st.markdown('<div class="frp-box">', unsafe_allow_html=True)

for pts in [22, 31, 42]:
    v_alta = ref_atual + (pts / 1000)
    v_baixa = ref_atual - (pts / 1000)
    
    cor_alta = "color: #FF8C00;" if p_spot >= v_alta else ""
    cor_baixa = "color: #0080FF;" if p_spot <= v_baixa else ""
    
    st.markdown(f"""
    <div class="frp-item">
        <span style="{cor_alta}">+{pts} PTS: {v_alta:.4f}</span>
        <span style="color: #222">|</span>
        <span style="{cor_baixa}">-{pts} PTS: {p_baixa:.4f}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# AUTO-REFRESH
time.sleep(5)
st.rerun()
