import streamlit as st
import time
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="TERMINAL DOLAR", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #000000; }
    * { font-family: 'JetBrains Mono', monospace !important; color: white; }
    .header { font-size: 26px; font-weight: bold; text-align: center; color: #FFFFFF; }
    .spot-big { font-size: 55px; font-weight: bold; color: #FFFFFF; }
    .label-bold { font-weight: bold; color: #FFFFFF; font-size: 20px; }
    .p-orange { color: #FFA500; font-size: 26px; font-weight: bold; }
    .p-green { color: #90EE90; font-size: 26px; font-weight: bold; }
    .p-blue { color: #00BFFF; font-size: 26px; font-weight: bold; }
    .p-red { color: #FF4B4B; font-size: 26px; font-weight: bold; }
    .p-yellow { color: #FFFF00; font-size: 16px; }
    /* Ajuste para os boxes de input não ficarem brancos demais */
    .stNumberInput input { background-color: #111; color: white; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- ÁREA DE INPUT DE VARIÁVEIS (VISÍVEL NO TOPO) ---
st.markdown('<div class="header">INPUT DE DADOS</div>', unsafe_allow_html=True)
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    ptax_input = st.number_input("PTAX", value=5.340, format="%.3f", step=0.001)
with col_in2:
    price_input = st.number_input("PRICE", value=5.335, format="%.3f", step=0.001)
with col_in3:
    fech_input = st.number_input("FECH. ANT", value=5.360, format="%.3f", step=0.001)

st.write("---")

# --- LÓGICA DE MERCADO ---
# Aqui simulamos o Spot acompanhando seus inputs ou uma variação mínima
if 'spot' not in st.session_state:
    st.session_state.spot = 5.362

# Simula pequena oscilação para o terminal não ficar "morto"
st.session_state.spot += 0.001 

# Cálculos com 3 casas decimais
variacao = ((st.session_state.spot / fech_input) - 1) * 100
equilibrio = (ptax_input * 1.004) - (price_input * 1.004)
paridade = st.session_state.spot + 0.005
p_justo = (ptax_input + price_input) / 2

# Referências
r1, r2, r3 = ptax_input * 1.002, ptax_input * 1.006, ptax_input * 1.010

# --- EXIBIÇÃO DO TERMINAL ---
st.markdown('<div class="header">TERMINAL DOLAR</div>', unsafe_allow_html=True)

# SPOT
st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <span class="spot-big">{st.session_state.spot:.3f}</span>
        <span style="font-size: 25px; color: {'#00FF00' if variacao >= 0 else '#FF0000'};"> {variacao:+.2f}%</span><br>
        <span class="p-yellow">FECH. ANT: {fech_input:.3f}</span><br>
        <span class="p-blue" style="font-size: 16px;">PRICE: {price_input:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# DADOS
st.markdown(f"""
    <div style="line-height: 2.2;">
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
    <div style="margin-top: 30px; border-top: 1px solid #333; padding-top: 10px; font-size: 12px; color: #666;">
        DXY: 103.450 | HORA: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)

# Atualização de 1 segundo
time.sleep(1)
st.rerun()
