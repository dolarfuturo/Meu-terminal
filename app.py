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
    
    /* Cores e Formatação */
    .label-white-bold { font-weight: bold; color: #FFFFFF; font-size: 20px; }
    .spot-big { font-size: 55px; font-weight: bold; color: #FFFFFF; }
    .p-orange { color: #FFA500; font-size: 26px; font-weight: bold; }
    .p-green-light { color: #90EE90; font-size: 26px; font-weight: bold; }
    .p-blue { color: #00BFFF; font-size: 26px; font-weight: bold; }
    .p-red { color: #FF4B4B; font-size: 26px; font-weight: bold; }
    .p-yellow { color: #FFFF00; font-size: 16px; }
    .p-fuchsia { color: #FF00FF; font-size: 16px; }
    
    /* Esconder elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- INPUTS DE VARIÁVEIS (ESCONDIDOS NO SIDEBAR) ---
with st.sidebar:
    st.header("CONTROLE ADM")
    ptax_base = st.number_input("ÂNCORA PTAX", value=5.345, format="%.3f")
    price_val = st.number_input("PRICE (TRAVA AZUL)", value=5.335, format="%.3f")
    fech_ant = st.number_input("FECH. ANTERIOR", value=5.360, format="%.3f")
    spot_live = st.number_input("SPOT ATUAL", value=5.342, format="%.3f")

# --- LÓGICA DE CÁLCULO (PLANO DE VOO) ---
# 1. Gatilho de simetria: Perda da PTAX - 2 pontos
perda_ptax = ptax_base - 0.002
gatilho_ativo = spot_live <= perda_ptax

# 2. Troca de Alvo Automática: PTAX - 0,41% se gatilho ativo
alvo_principal = ptax_base * (1 - 0.0041) if gatilho_ativo else ptax_base

# 3. Cálculo de Equilíbrio: (PTAX * 1.004) - (PRICE * 1.004)
calc_equilibrio = (ptax_base * 1.004) - (price_val * 1.004)

# 4. Referências Institucionais (1.002, 1.006, 1.010)
r1 = ptax_base * 1.002
r2 = ptax_base * 1.006
r3 = ptax_base * 1.010

# Variação do Spot
variacao = ((spot_live / fech_ant) - 1) * 100

# --- EXIBIÇÃO DO TERMINAL ---
st.markdown('<div style="font-size: 26px; font-weight: bold; text-align: center;">TERMINAL DOLAR</div>', unsafe_allow_html=True)

# Bloco SPOT (3 casas decimais)
cor_var = "#00FF00" if variacao >= 0 else "#FF0000"
st.markdown(f"""
    <div style="margin-top: 20px;">
        <span class="spot-big">{spot_live:.3f}</span>
        <span style="font-size: 28px; color: {cor_var};"> {variacao:+.2f}%</span><br>
        <span class="p-yellow">FECH. ANT: {fech_ant:.3f}</span><br>
        <span class="p-blue">PRICE: {price_val:.3f}</span>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# Lista Vertical (Nomes em Branco Negrito)
st.markdown(f"""
    <div style="line-height: 2.5;">
        <span class="label-white-bold">PARIDADE (ALVO):</span> <span class="p-orange">{alvo_principal:.3f}</span><br>
        <span class="label-white-bold">EQUILÍBRIO:</span> <span class="p-green-light">{calc_equilibrio:.3f}</span><br>
        <span class="label-white-bold">PREÇO JUSTO:</span> <span class="p-blue">{(ptax_base + price_val)/2:.3f}</span><br>
        <span class="label-white-bold">REF INSTITUCIONAL:</span> 
        <span class="p-red">{r1:.3f}</span> &nbsp;
        <span class="p-blue">{r2:.3f}</span> &nbsp;
        <span class="p-green-light">{r3:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# Status do Gatilho
if gatilho_ativo:
    st.markdown(f'<div style="color: #FF0000; font-weight: bold; text-align: center; border: 1px solid red; padding: 5px;">GATILHO ATIVO: ALVO 0.41%</div>', unsafe_allow_html=True)

# Rodapé Ticker
st.markdown(f"""
    <div style="margin-top: 40px; border-top: 1px solid #333; padding-top: 10px; font-size: 13px; color: #666;">
        DXY | EWZ | SPREAD | ATUALIZADO: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)

# AUTO-REFRESH
time.sleep(1)
st.rerun()
