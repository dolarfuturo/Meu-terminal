import streamlit as st
import time
from datetime import datetime

# --- CONFIGURAÇÃO DE INTERFACE (TERMUX STYLE) ---
st.set_page_config(page_title="TERMINAL DOLAR", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #000000; }
    * { font-family: 'JetBrains Mono', monospace !important; color: white; }
    
    /* Inputs Estilizados */
    .stNumberInput input { background-color: #111 !important; color: white !important; border: 1px solid #333 !important; }
    
    /* Classes de Cores Reais */
    .label-white-bold { font-weight: bold; color: #FFFFFF; font-size: 20px; }
    .spot-big { font-size: 55px; font-weight: bold; color: #FFFFFF; }
    .p-orange { color: #FFA500; font-size: 26px; font-weight: bold; }
    .p-green-light { color: #90EE90; font-size: 26px; font-weight: bold; }
    .p-blue { color: #00BFFF; font-size: 26px; font-weight: bold; }
    .p-red { color: #FF4B4B; font-size: 26px; font-weight: bold; }
    .p-yellow { color: #FFFF00; font-size: 16px; }
    
    /* Esconder Lixo de UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ÁREA DE VARIÁVEIS (INPUTS DINÂMICOS) ---
with st.sidebar:
    st.header("⚙️ AJUSTE DE VARIÁVEIS")
    # Multiplicadores de Esticamento
    m_equil = st.number_input("Var. Equilíbrio", value=1.004, format="%.3f")
    m_ref1 = st.number_input("Var. Ref 1 (Red)", value=1.002, format="%.3f")
    m_ref2 = st.number_input("Var. Ref 2 (Blue)", value=1.008, format="%.3f")
    m_ref3 = st.number_input("Var. Ref 3 (Green)", value=1.010, format="%.3f")
    m_alvo_trava = st.number_input("Var. Alvo Trava (0.41%)", value=0.0041, format="%.4f")
    
    st.write("---")
    st.header("📊 PREÇOS OPERACIONAIS")
    ptax_base = st.number_input("PTAX ÂNCORA", value=5.345, format="%.3f")
    price_azul = st.number_input("PRICE (TRAVA)", value=5.335, format="%.3f")
    fech_ant = st.number_input("FECH. ANTERIOR", value=5.360, format="%.3f")
    spot_live = st.number_input("CASH / SPOT", value=5.342, format="%.3f")

# --- LÓGICA DO SISTEMA ---
# 1. Gatilho de Ativação (Perda da PTAX - 2 pontos)
gatilho_on = spot_live <= (ptax_base - 0.002)

# 2. Alvo Automático (Regra 0.41%)
alvo_final = ptax_base * (1 - m_alvo_trava) if gatilho_on else ptax_base

# 3. Cálculo Equilíbrio: (PTAX * Var) - (PRICE * Var)
resultado_equilibrio = (ptax_base * m_equil) - (price_azul * m_equil)

# 4. Referências (Usando os multiplicadores manuais)
r1_val = ptax_base * m_ref1
r2_val = ptax_base * m_ref2
r3_val = ptax_base * m_ref3

# Variação Percentual do Spot
perc_var = ((spot_live / fech_ant) - 1) * 100

# --- TERMINAL DISPLAY ---
st.markdown('<div style="text-align: center; font-size: 24px; font-weight: bold;">TERMINAL DOLAR</div>', unsafe_allow_html=True)

# Box de Status do Plano de Voo
if gatilho_on:
    st.markdown(f'<div style="background-color: #FF0000; padding: 10px; text-align: center; font-weight: bold;">GATILHO ATIVO: TRAVA {m_alvo_trava*100:.2f}%</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="background-color: #222; padding: 10px; text-align: center; font-weight: bold;">STATUS: PASSIVO (ACIMA DA PTAX)</div>', unsafe_allow_html=True)

# Bloco de Preços Principais
cor_spot_var = "#00FF00" if perc_var >= 0 else "#FF0000"
st.markdown(f"""
    <div style="margin-top: 25px;">
        <span class="spot-big">{spot_live:.3f}</span>
        <span style="font-size: 28px; color: {cor_spot_var};"> {perc_var:+.2f}%</span><br>
        <span class="p-yellow">FECH. ANT: {fech_ant:.3f}</span><br>
        <span class="p-blue" style="font-size: 16px;">PRICE: {price_azul:.3f}</span>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# Dados Verticais com Nomes em Branco Negrito
st.markdown(f"""
    <div style="line-height: 2.6;">
        <span class="label-white-bold">ALVO PRINCIPAL:</span> <span class="p-orange">{alvo_final:.3f}</span><br>
        <span class="label-white-bold">EQUILÍBRIO:</span> <span class="p-green-light">{resultado_equilibrio:.3f}</span><br>
        <span class="label-white-bold">PREÇO JUSTO:</span> <span class="p-blue">{(ptax_base + price_azul)/2:.3f}</span><br>
        <span class="label-white-bold">REF INSTITUCIONAL:</span> 
        <span class="p-red">{r1_val:.3f}</span> &nbsp;
        <span class="p-blue">{r2_val:.3f}</span> &nbsp;
        <span class="p-green-light">{r3_val:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# Rodapé Ticker
st.markdown(f"""
    <div style="margin-top: 50px; border-top: 1px solid #333; padding-top: 10px; font-size: 13px; color: #555;">
        DXY | EWZ | SPREAD B3-SPOT | HORA: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)

# Auto-Refresh 1s
time.sleep(1)
st.rerun()
