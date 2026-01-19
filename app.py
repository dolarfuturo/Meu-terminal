import streamlit as st
import time
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL TERMINAL ---
st.set_page_config(page_title="TERMINAL DOLAR", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #000000; }
    * { font-family: 'JetBrains Mono', monospace !important; color: white; }
    .header { font-size: 26px; font-weight: bold; text-align: center; border-bottom: 1px solid #222; padding: 10px; }
    .spot-big { font-size: 55px; font-weight: bold; }
    .label-bold { font-weight: bold; font-size: 20px; }
    .p-orange { color: #FFA500; font-size: 24px; font-weight: bold; }
    .p-green { color: #90EE90; font-size: 24px; font-weight: bold; }
    .p-blue { color: #00BFFF; font-size: 24px; font-weight: bold; }
    .p-red { color: #FF4B4B; font-size: 24px; font-weight: bold; }
    .p-yellow { color: #FFFF00; font-size: 15px; }
    .status-box { padding: 5px; border-radius: 5px; font-weight: bold; text-align: center; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INPUTS ESCONDIDOS (SIDEBAR) ---
with st.sidebar:
    st.header("PAINEL DE CONTROLE")
    ptax_base = st.number_input("ÂNCORA PTAX", value=5.345, format="%.3f")
    price_val = st.number_input("PRICE (TRAVA)", value=5.335, format="%.3f")
    fech_ant = st.number_input("FECH. ANTERIOR", value=5.360, format="%.3f")
    spot_atual = st.number_input("SPOT ATUAL", value=5.342, format="%.3f")

# --- LÓGICA DO PLANO DE VOO [CITE: 1, 2] ---
# 1. Gatilho: Perda da PTAX - 2 pontos
gatilho_ptax = ptax_base - 0.002
status_gatilho = "PASSIVO"
cor_gatilho = "#333"

# 2. Troca de Alvo Automática (0,41% abaixo da PTAX)
alvo_principal = ptax_base * (1 - 0.0041)

if spot_atual <= gatilho_ptax:
    status_gatilho = "GATILHO ATIVO - TRAVA 0.41%"
    cor_gatilho = "#FF0000"
    target_display = alvo_principal
else:
    target_display = ptax_base # Alvo inicial é a própria PTAX

# 3. Referências Institucionais (1.002, 1.006, 1.010)
ref1 = ptax_base * 1.002
ref2 = ptax_base * 1.006
ref3 = ptax_base * 1.010

# Variação Spot
variacao = ((spot_atual / fech_ant) - 1) * 100

# --- EXIBIÇÃO ---
st.markdown('<div class="header">TERMINAL DOLAR</div>', unsafe_allow_html=True)

# Status de Execução (O Plano de Voo)
st.markdown(f'<div class="status-box" style="background-color: {cor_gatilho};">MODO: {status_gatilho}</div>', unsafe_allow_html=True)

# SPOT E PRICE
st.markdown(f"""
    <div style="margin-top: 20px;">
        <span class="spot-big">{spot_atual:.3f}</span>
        <span style="font-size: 25px; color: {'#00FF00' if variacao >= 0 else '#FF0000'};"> {variacao:+.2f}%</span><br>
        <span class="p-yellow">FECH. ANT: {fech_ant:.3f}</span><br>
        <span class="p-blue" style="font-size: 16px;">PRICE: {price_val:.3f}</span>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# BLOCO DE DADOS
st.markdown(f"""
    <div style="line-height: 2.2;">
        <span class="label-bold">ALVO PRINCIPAL:</span> <span class="p-orange">{target_display:.3f}</span><br>
        <span class="label-bold">EQUILÍBRIO (1.004):</span> <span class="p-green">{(ptax_base * 1.004 - price_val * 1.004):.3f}</span><br>
        <span class="label-bold">REF INSTITUCIONAL:</span> 
        <span class="p-red">{ref1:.3f}</span> &nbsp;
        <span class="p-blue">{ref2:.3f}</span> &nbsp;
        <span class="p-green">{ref3:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# RODAPÉ
st.markdown(f"""
    <div style="margin-top: 30px; border-top: 1px solid #333; padding-top: 10px; font-size: 12px; color: #666;">
        DXY | EWZ | SPREAD | HORA: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)

time.sleep(1)
st.rerun()
