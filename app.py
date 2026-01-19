import streamlit as st
import time
from datetime import datetime

# --- CONFIGURAÇÃO DE AMBIENTE ---
st.set_page_config(page_title="TERMINAL DOLAR", layout="centered")

# CSS Estilo Termux (Fundo Preto, Fonte Mono, Sem Margens)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #000000; }
    * { font-family: 'JetBrains Mono', monospace !important; color: white; }
    .header { font-size: 24px; font-weight: bold; text-align: center; color: #FFFFFF; }
    .spot-big { font-size: 60px; font-weight: bold; color: #FFFFFF; }
    .label-bold { font-weight: bold; color: #FFFFFF; font-size: 22px; }
    .p-orange { color: #FFA500; font-size: 28px; font-weight: bold; }
    .p-green { color: #90EE90; font-size: 28px; font-weight: bold; }
    .p-blue { color: #00BFFF; font-size: 28px; font-weight: bold; }
    .p-red { color: #FF4B4B; font-size: 28px; font-weight: bold; }
    .p-yellow { color: #FFFF00; font-size: 16px; }
    /* Ajuste de inputs para modo escuro */
    div[data-baseweb="input"] { background-color: #111; border: 1px solid #333; }
    input { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BLOCO DE INPUTS DE VARIÁVEIS (DISPONÍVEIS E OPERACIONAIS) ---
with st.expander("🛠️ AJUSTE DE VARIÁVEIS E PREÇOS", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        v_ptax = st.number_input("PTAX BASE", value=5.345, format="%.3f", step=0.001)
        m_equi = st.number_input("Var Equi", value=1.004, format="%.3f")
    with c2:
        v_price = st.number_input("PRICE AZUL", value=5.335, format="%.3f", step=0.001)
        m_ref1 = st.number_input("Var Ref 1", value=1.002, format="%.3f")
    with c3:
        v_fech = st.number_input("FECH ANT", value=5.360, format="%.3f", step=0.001)
        m_ref2 = st.number_input("Var Ref 2", value=1.008, format="%.3f")
    with c4:
        v_spot = st.number_input("SPOT ATUAL", value=5.342, format="%.3f", step=0.001)
        m_ref3 = st.number_input("Var Ref 3", value=1.010, format="%.3f")

# --- LÓGICA DE EXECUÇÃO (CÁLCULOS ATIVOS) ---
# Gatilho: Perda da PTAX - 2 pontos
gatilho_on = v_spot <= (v_ptax - 0.002)

# Alvo: Se gatilho ativo, trava em 0,41% abaixo da PTAX
v_alvo = v_ptax * (1 - 0.0041) if gatilho_on else v_ptax

# Equilíbrio: (PTAX * Var) - (PRICE * Var)
res_equi = (v_ptax * m_equi) - (v_price * m_equi)

# Referências Institucionais
r1, r2, r3 = v_ptax * m_ref1, v_ptax * m_ref2, v_ptax * m_ref3

# Variação %
var_pct = ((v_spot / v_fech) - 1) * 100

# --- DISPLAY DO TERMINAL ---
st.markdown('<div class="header">TERMINAL DOLAR</div>', unsafe_allow_html=True)

# Indicador de Gatilho Ativo
if gatilho_on:
    st.markdown(f'<div style="background-color:red; color:white; text-align:center; font-weight:bold; padding:5px;">GATILHO ATIVO: ALVO 0.41%</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="background-color:#222; color:white; text-align:center; font-weight:bold; padding:5px;">MONITORAMENTO PASSIVO</div>', unsafe_allow_html=True)

# Bloco Principal: SPOT e PRICE
st.markdown(f"""
    <div style="margin-top: 20px;">
        <span class="spot-big">{v_spot:.3f}</span>
        <span style="font-size: 30px; color: {'#00FF00' if var_pct >= 0 else '#FF0000'};"> {var_pct:+.2f}%</span><br>
        <span class="p-yellow">FECH. ANT: {v_fech:.3f}</span><br>
        <span class="p-blue" style="font-size: 18px;">PRICE: {v_price:.3f}</span>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# Dados de Alvo e Institucional
st.markdown(f"""
    <div style="line-height: 2.5;">
        <span class="label-bold">ALVO PRINCIPAL:</span> <span class="p-orange">{v_alvo:.3f}</span><br>
        <span class="label-bold">EQUILÍBRIO:</span> <span class="p-green">{res_equi:.3f}</span><br>
        <span class="label-bold">PREÇO JUSTO:</span> <span class="p-blue">{(v_ptax + v_price)/2:.3f}</span><br>
        <span class="label-bold">REF INSTITUCIONAL:</span> 
        <span class="p-red">{r1:.3f}</span> &nbsp;
        <span class="p-blue">{r2:.3f}</span> &nbsp;
        <span class="p-green">{r3:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# Rodapé Ticker
st.markdown(f"""
    <div style="margin-top: 40px; border-top: 1px solid #333; padding-top: 10px; font-size: 13px; color: #555;">
        DXY | EWZ | SPREAD | HORA: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)

# LOOP DE ATIVAÇÃO (Destrava o Terminal)
time.sleep(1)
st.rerun()
