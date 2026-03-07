import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS REFINADO - CORES E ALINHAMENTO
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #e0e0e0; }
    .bair-title { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 32px; letter-spacing: 2px; }
    .header-box { text-align: center; border: 1px solid #1f2329; padding: 10px; border-radius: 4px; background: #161b22; }
    .clock-time { color: #ffffff; font-size: 24px; font-weight: bold; }
    .clock-label { color: #848e9c; font-size: 12px; }
    .calc-panel { border: 1px solid #00f2ff; padding: 15px; background: #0b0e11; border-radius: 5px; }
    .eixo-data { background: #00f2ff; color: #000; font-weight: bold; text-align: center; padding: 8px; margin: 15px 0; border-radius: 2px; }
    .calc-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-family: monospace; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
col_t, col_b, col_n, col_l = st.columns([2, 1, 1, 1])

with col_t:
    st.markdown('<p class="bair-title">BAIR - TERMINAL DOLAR</p>', unsafe_allow_html=True)

def get_tz_time(tz):
    return datetime.now(pytz.timezone(tz)).strftime("%H:%M:%S")

with col_b:
    st.markdown(f'<div class="header-box"><div class="clock-label">BRASÍLIA</div><div class="clock-time">{get_tz_time("America/Sao_Paulo")}</div></div>', unsafe_allow_html=True)
with col_n:
    st.markdown(f'<div class="header-box"><div class="clock-label">NEW YORK</div><div class="clock-time">{get_tz_time("America/New_York")}</div></div>', unsafe_allow_html=True)
with col_l:
    st.markdown(f'<div class="header-box"><div class="clock-label">LONDRES</div><div class="clock-time">{get_tz_time("Europe/London")}</div></div>', unsafe_allow_html=True)

st.write("---")

# --- CORPO (DIVIDINDO O ESPAÇO) ---
# Aqui definimos col1 e col2 explicitamente para evitar o erro da imagem
col1, col2 = st.columns([2.5, 1.5])

with col1:
    st.markdown('<p style="color:#848e9c;">GRADE PRINCIPAL DE ATIVOS</p>', unsafe_allow_html=True)
    grade_data = {
        "ATIVO": ["SPOT", "DOLFUT", "DXY", "EWZ", "EUR/USD", "XAU/USD", "BRENT"],
        "PRICE": ["0.00"]*7, "VAR": ["0.00%"]*7
    }
    st.table(grade_data)

with col2:
    st.markdown('<div class="calc-panel">', unsafe_allow_html=True)
    st.markdown('<p style="color:#00f2ff; font-weight:bold;">PAINEL DE CÁLCULOS</p>', unsafe_allow_html=True)
    
    close_input = st.number_input("DIGITE O CLOSE:", value=5.4223, format="%.4f")
    
    # Cálculos Positivos
    for p, m in [("3,00%", 1.030), ("2,00%", 1.020), ("1,00%", 1.010)]:
        st.markdown(f'<div class="calc-row"><span style="color:#00ff88;">{p}</span><span>{close_input*m:.4f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-data">CLOSE EIXO: {close_input:.4f}</div>', unsafe_allow_html=True)

    # Cálculos Negativos
    for p, m in [("-1,00%", 0.9900), ("-2,00%", 0.9800), ("-3,00%", 0.9700)]:
        st.markdown(f'<div class="calc-row"><span style="color:#ff4d4d;">{p}</span><span>{close_input*m:.4f}</span></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Rodapé simples
st.markdown('<p style="text-align:center; color:#00f2ff; margin-top:30px;">DXY 0,01% | EWZ 0,0% | SPOT 0,0%</p>', unsafe_allow_html=True)

# Atualização automática
time.sleep(1)
st.rerun()
