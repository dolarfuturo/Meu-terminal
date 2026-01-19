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
    
    /* VARIÁVEIS COM NÚMEROS PRETOS */
    input { color: #000000 !important; font-weight: bold !important; background-color: #FFFFFF !important; }
    
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

# --- PAINEL DE CONTROLE (INPUTS) ---
with st.sidebar:
    st.header("⚙️ VARIÁVEIS")
    v_equi = st.number_input("Var Equilíbrio (1.004)", value=1.004, format="%.3f")
    v_r1 = st.number_input("Var Ref 1 (1.002)", value=1.002, format="%.3f")
    v_r2 = st.number_input("Var Ref 2 (1.006)", value=1.006, format="%.3f")
    v_r3 = st.number_input("Var Ref 3 (1.010)", value=1.010, format="%.3f")
    v_alvo = st.number_input("Var Alvo (0.0041)", value=0.0041, format="%.4f")
    
    st.write("---")
    st.header("📊 PREÇOS")
    ptax_in = st.number_input("PTAX", value=5.345, format="%.3f")
    price_in = st.number_input("PRICE", value=5.335, format="%.3f")
    fech_in = st.number_input("FECHAMENTO", value=5.360, format="%.3f")
    spot_in = st.number_input("SPOT", value=5.342, format="%.3f")

# --- LÓGICA CORRIGIDA (PLANO DE VOO) ---
# 1. Gatilho: Perda da PTAX em 2 pontos
gatilho_on = spot_in <= (ptax_in - 0.002)

# 2. Alvo Principal: Troca automática para PTAX - 0,41%
alvo_principal = ptax_in * (1 - v_alvo) if gatilho_on else ptax_in

# 3. EQUILÍBRIO CORRIGIDO: Diferença das âncoras ajustadas
# Cálculo: (PTAX * 1.004) - (PRICE * 1.004)
calc_equilibrio = (ptax_in * v_equi) - (price_in * v_equi)

# 4. Referências de Defesa
r_vermelho = ptax_in * v_r1
r_azul = ptax_in * v_r2
r_verde = ptax_in * v_r3

# Variação %
var_pct = ((spot_in / fech_in) - 1) * 100

# --- TERMINAL ---
st.markdown('<div class="header">TERMINAL DOLAR</div>', unsafe_allow_html=True)

# Bloco SPOT e Variação
cor_v = "#00FF00" if var_pct >= 0 else "#FF0000"
st.markdown(f"""
    <div style="margin-top: 20px;">
        <span class="spot-big">{spot_in:.3f}</span>
        <span style="font-size: 28px; color: {cor_v};"> {var_pct:+.2f}%</span><br>
        <span class="p-yellow">FECH. ANT: {fech_in:.3f}</span><br>
        <span class="p-blue" style="font-size: 16px;">PRICE: {price_in:.3f}</span>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# Informações de Alvo e Equilíbrio (Nomes em Branco Negrito)
st.markdown(f"""
    <div style="line-height: 2.6;">
        <span class="label-white-bold">ALVO PRINCIPAL:</span> <span class="p-orange">{alvo_principal:.3f}</span><br>
        <span class="label-white-bold">EQUILÍBRIO:</span> <span class="p-green-light">{calc_equilibrio:.3f}</span><br>
        <span class="label-white-bold">PREÇO JUSTO:</span> <span class="p-blue">{(ptax_in + price_in)/2:.3f}</span><br>
        <span class="label-white-bold">REF INSTITUCIONAL:</span> 
        <span class="p-red">{r_vermelho:.3f}</span> &nbsp;
        <span class="p-blue">{r_azul:.3f}</span> &nbsp;
        <span class="p-green-light">{r_verde:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# Rodapé Ticker
st.markdown(f"""
    <div style="margin-top: 40px; border-top: 1px solid #333; padding-top: 10px; font-size: 13px; color: #555;">
        DXY | EWZ | HORA: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)

# Auto-Refresh
time.sleep(1)
st.rerun()
