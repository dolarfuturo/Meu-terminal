import streamlit as st
import time
from datetime import datetime

# --- CONFIGURAÇÃO DE INTERFACE (ESTILO TERMUX) ---
st.set_page_config(page_title="TERMINAL DOLAR", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #000000; }
    * { font-family: 'JetBrains Mono', monospace !important; color: white; }
    
    /* AJUSTE: Números dos inputs em PRETO */
    input { color: #000000 !important; font-weight: bold !important; }
    
    .header { font-size: 26px; font-weight: bold; text-align: center; color: #FFFFFF; }
    .spot-big { font-size: 55px; font-weight: bold; color: #FFFFFF; }
    .label-white-bold { font-weight: bold; color: #FFFFFF; font-size: 22px; }
    .p-orange { color: #FFA500; font-size: 26px; font-weight: bold; }
    .p-green-light { color: #90EE90; font-size: 26px; font-weight: bold; }
    .p-blue { color: #00BFFF; font-size: 26px; font-weight: bold; }
    .p-red { color: #FF4B4B; font-size: 26px; font-weight: bold; }
    .p-yellow { color: #FFFF00; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- ÁREA DE INPUTS DE VARIÁVEIS ---
with st.sidebar:
    st.header("⚙️ VARIÁVEIS")
    # Multiplicadores
    v_1002 = st.number_input("Multiplicador 1.002", value=1.002, format="%.3f")
    v_1004 = st.number_input("Multiplicador 1.004 (Equi)", value=1.004, format="%.3f")
    v_1008 = st.number_input("Multiplicador 1.008", value=1.008, format="%.3f")
    v_1010 = st.number_input("Multiplicador 1.010", value=1.010, format="%.3f")
    v_trava = st.number_input("Alvo Trava (0.41%)", value=0.0041, format="%.4f")
    
    st.write("---")
    st.header("📊 PREÇOS")
    ptax_base = st.number_input("PTAX", value=5.345, format="%.3f")
    price_azul = st.number_input("PRICE", value=5.335, format="%.3f")
    fech_ant = st.number_input("FECHAMENTO", value=5.360, format="%.3f")
    spot_live = st.number_input("SPOT", value=5.342, format="%.3f")

# --- LÓGICA DE CÁLCULO ---
# Gatilho: Perda da PTAX - 2 pontos
gatilho = spot_live <= (ptax_base - 0.002)

# Alvo Principal: Troca automática
alvo_principal = ptax_base * (1 - v_trava) if gatilho else ptax_base

# EQUILÍBRIO: Diferença esticada entre as duas âncoras
calc_equilibrio = (ptax_base * v_1004) - (price_azul * v_1004)

# Referências
r_red = ptax_base * v_1002
r_blue = ptax_base * v_1008
r_green = ptax_base * v_1010

# Variação %
var_pct = ((spot_live / fech_ant) - 1) * 100

# --- DISPLAY ---
st.markdown('<div class="header">TERMINAL DOLAR</div>', unsafe_allow_html=True)

# SPOT e PRICE
cor_v = "#00FF00" if var_pct >= 0 else "#FF0000"
st.markdown(f"""
    <div style="margin-top: 20px;">
        <span class="spot-big">{spot_live:.3f}</span>
        <span style="font-size: 28px; color: {cor_v};"> {var_pct:+.2f}%</span><br>
        <span class="p-yellow">FECH. ANT: {fech_ant:.3f}</span><br>
        <span class="p-blue" style="font-size: 16px;">PRICE: {price_azul:.3f}</span>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# Dados Operacionais
st.markdown(f"""
    <div style="line-height: 2.6;">
        <span class="label-white-bold">ALVO PRINCIPAL:</span> <span class="p-orange">{alvo_principal:.3f}</span><br>
        <span class="label-white-bold">EQUILÍBRIO:</span> <span class="p-green-light">{calc_equilibrio:.3f}</span><br>
        <span class="label-white-bold">PREÇO JUSTO:</span> <span class="p-blue">{(ptax_base + price_azul)/2:.3f}</span><br>
        <span class="label-white-bold">REF INSTITUCIONAL:</span> 
        <span class="p-red">{r_red:.3f}</span> &nbsp;
        <span class="p-blue">{r_blue:.3f}</span> &nbsp;
        <span class="p-green-light">{r_green:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# Ticker inferior
st.markdown(f"""
    <div style="margin-top: 40px; border-top: 1px solid #333; padding-top: 10px; font-size: 13px; color: #555;">
        DXY | EWZ | HORA BR: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)

# Loop de atualização
time.sleep(1)
st.rerun()
