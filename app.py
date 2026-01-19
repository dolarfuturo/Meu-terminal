import streamlit as st
import time
from datetime import datetime

# --- CONFIGURAÇÃO DE INTERFACE ---
st.set_page_config(page_title="TERMINAL DOLAR", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #000000; }
    * { font-family: 'JetBrains Mono', monospace !important; color: white; }
    .header { font-size: 26px; font-weight: bold; text-align: center; color: #FFFFFF; padding: 10px; }
    .spot-big { font-size: 55px; font-weight: bold; color: #FFFFFF; }
    .label-bold { font-weight: bold; color: #FFFFFF; font-size: 22px; }
    .p-orange { color: #FFA500; font-size: 26px; font-weight: bold; }
    .p-green { color: #90EE90; font-size: 26px; font-weight: bold; }
    .p-blue { color: #00BFFF; font-size: 26px; font-weight: bold; }
    .p-red { color: #FF4B4B; font-size: 26px; font-weight: bold; }
    .p-yellow { color: #FFFF00; font-size: 16px; }
    /* Esconde menu lateral e elementos desnecessários */
    [data-testid="stSidebar"] { background-color: #111; }
    </style>
    """, unsafe_allow_html=True)

# --- INPUTS ESCONDIDOS (SIDEBAR) ---
with st.sidebar:
    st.header("PAINEL ADM")
    ptax_base = st.number_input("PTAX BASE", value=5.340, format="%.3f", step=0.001)
    price_val = st.number_input("PRICE (AZUL)", value=5.335, format="%.3f", step=0.001)
    fech_ant = st.number_input("FECH. ANTERIOR", value=5.360, format="%.3f", step=0.001)
    spot_sim = st.number_input("SPOT ATUAL", value=5.362, format="%.3f", step=0.001)

# --- LÓGICA DE CÁLCULO (AS VARIÁVEIS QUE VOCÊ PASSOU) ---
# Reset VWAP/Lógica baseada em PTAX e PRICE
variacao = ((spot_sim / fech_ant) - 1) * 100

# Equilíbrio usando o multiplicador 1.004
equilibrio = (ptax_base * 1.004) - (price_val * 1.004)

# Preço Justo
p_justo = (ptax_base + price_val) / 2

# Referências Institucionais (1.002, 1.008, 1.01)
ref_vermelho = ptax_base * 1.002
ref_azul = ptax_base * 1.008
ref_verde = ptax_base * 1.01

# --- EXIBIÇÃO DO TERMINAL ---
st.markdown('<div class="header">TERMINAL DOLAR</div>', unsafe_allow_html=True)

# Bloco SPOT
cor_var = "#00FF00" if variacao >= 0 else "#FF0000"
st.markdown(f"""
    <div style="margin-bottom: 25px;">
        <span class="spot-big">{spot_sim:.3f}</span>
        <span style="font-size: 28px; color: {cor_var};"> {variacao:+.2f}%</span><br>
        <span class="p-yellow">FECH. ANT: {fech_ant:.3f}</span><br>
        <span class="p-blue" style="font-size: 16px;">PRICE: {price_val:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# Bloco de Variáveis
st.markdown(f"""
    <div style="line-height: 2.4;">
        <span class="label-bold">PARIDADE:</span> <span class="p-orange">{(spot_sim + 0.002):.3f}</span><br>
        <span class="label-bold">EQUILÍBRIO:</span> <span class="p-green">{equilibrio:.3f}</span><br>
        <span class="label-bold">PREÇO JUSTO:</span> <span class="p-blue">{p_justo:.3f}</span><br>
        <span class="label-bold">REF INSTITUCIONAL:</span> 
        <span class="p-red">{ref_vermelho:.3f}</span> &nbsp;
        <span class="p-blue">{ref_azul:.3f}</span> &nbsp;
        <span class="p-green">{ref_verde:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# Rodapé Ticker
st.markdown(f"""
    <div style="margin-top: 40px; border-top: 1px solid #333; padding-top: 10px; font-size: 13px; color: #666;">
        DXY: 103.450 | HORA: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)

# AUTO-REFRESH (1 Segundo)
time.sleep(1)
st.rerun()
