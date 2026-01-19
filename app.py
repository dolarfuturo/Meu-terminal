import streamlit as st
import time
import random
from datetime import datetime

# --- CONFIGURAÇÃO DE INTERFACE ---
st.set_page_config(page_title="TERMINAL DOLAR", layout="centered")

# CSS Estilo Termux/Bloomberg com foco em 3 casas decimais
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #000000; }
    * { font-family: 'JetBrains Mono', monospace !important; color: white; }
    .header { font-size: 26px; font-weight: bold; text-align: center; padding: 10px; border-bottom: 1px solid #222; margin-bottom: 20px;}
    .spot-big { font-size: 55px; font-weight: bold; line-height: 1; }
    .label-bold { font-weight: bold; color: #FFFFFF; font-size: 22px; }
    .p-orange { color: #FFA500; font-size: 26px; font-weight: bold; }
    .p-green { color: #90EE90; font-size: 26px; font-weight: bold; }
    .p-blue { color: #00BFFF; font-size: 26px; font-weight: bold; }
    .p-red { color: #FF4B4B; font-size: 26px; font-weight: bold; }
    .p-yellow { color: #FFFF00; font-size: 16px; }
    .p-fuchsia { color: #FF00FF; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- PAINEL ADMINISTRATIVO (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ CONFIGURAÇÃO ADM")
    ptax_base = st.number_input("PTAX Atual", value=5340.000, format="%.3f", step=0.001)
    price_val = st.number_input("PRICE (Azul)", value=5335.000, format="%.3f", step=0.001)
    fech_ant = st.number_input("Fechamento Anterior", value=5360.000, format="%.3f", step=0.001)

# --- MOTOR DE PREÇOS (Simulação Real-Time) ---
# Em produção, aqui entra a conexão direta com o Profit ou TradingView
spot_atual = 5362.500 + (random.uniform(-0.150, 0.150)) 

# --- CÁLCULOS TÉCNICOS ---
variacao = ((spot_atual / fech_ant) - 1) * 100
equilibrio = (ptax_base * 1.004) - (price_val * 1.004)
paridade = spot_atual + 1.350 # Lógica de Spread
p_justo = (ptax_base + price_val) / 2

# Referências Institucionais
r1 = ptax_base * 1.002
r2 = ptax_base * 1.006
r3 = ptax_base * 1.010

# --- EXIBIÇÃO DO TERMINAL ---
st.markdown('<div class="header">TERMINAL DOLAR</div>', unsafe_allow_html=True)

# Bloco Principal (Spot e Variação)
cor_var = "#00FF00" if variacao >= 0 else "#FF0000"
st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <span class="spot-big">{spot_atual:.3f}</span>
        <span style="font-size: 28px; color: {cor_var}; vertical-align: top;"> {variacao:+.2f}%</span><br>
        <span class="p-yellow">FECH. ANT: {fech_ant:.3f}</span><br>
        <span class="p-blue" style="font-size: 16px;">PRICE: {price_val:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# Lista de Dados Vertical
st.markdown(f"""
    <div style="line-height: 2.5;">
        <span class="label-bold">PARIDADE:</span> <span class="p-orange">{paridade:.3f}</span><br>
        <span class="label-bold">EQUILÍBRIO:</span> <span class="p-green">{equilibrio:.3f}</span><br>
        <span class="label-bold">PREÇO JUSTO:</span> <span class="p-blue">{p_justo:.3f}</span><br>
        <span class="label-bold">REF INSTITUCIONAL:</span> 
        <span class="p-red">{r1:.3f}</span> &nbsp;
        <span class="p-blue">{r2:.3f}</span> &nbsp;
        <span class="p-green">{r3:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# Rodapé Ticker
st.markdown(f"""
    <div style="margin-top: 50px; border-top: 1px solid #333; padding-top: 10px; font-size: 13px; color: #888;">
        DXY: 103.450 | EWZ: 32.110 | SPREAD: -4.500 | HORA: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)

# AUTO-REFRESH (Ativa o Terminal)
time.sleep(1)
st.rerun()
