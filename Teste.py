import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# Configuração de tela cheia para o Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# Interface Neon/Dark do Terminal
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00f2ff; }
    .stNumberInput div { background-color: #161b22 !important; color: #00f2ff !important; }
    .title-bair { font-size: 35px; font-weight: bold; color: #00f2ff; text-shadow: 0 0 10px #00f2ff; }
    .clock-container { border: 1px solid #3d444d; padding: 10px; border-radius: 5px; text-align: center; background: #161b22; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 0; border-bottom: 0.5px solid #2d333b; font-family: monospace; }
    .eixo-close { background-color: #00f2ff; color: #000; font-weight: bold; text-align: center; padding: 5px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER: BAIR + RELÓGIOS ---
col_logo, col_br, col_ny, col_ldn = st.columns([2, 1, 1, 1])

with col_logo:
    st.markdown('<p class="title-bair">BAIR - TERMINAL DOLAR</p>', unsafe_allow_html=True)

# Função para pegar hora por Timezone
def get_time(tz_name):
    return datetime.now(pytz.timezone(tz_name)).strftime("%H:%M:%S")

with col_br:
    st.markdown(f'<div class="clock-container">BRASÍLIA<br><b style="color:#ffd700; font-size:22px;">{get_time("America/Sao_Paulo")}</b></div>', unsafe_allow_html=True)
with col_ny:
    st.markdown(f'<div class="clock-container">NEW YORK<br><b style="color:#ffd700; font-size:22px;">{get_time("America/New_York")}</b></div>', unsafe_allow_html=True)
with col_ldn:
    st.markdown(f'<div class="clock-container">LONDRES<br><b style="color:#ffd700; font-size:22px;">{get_time("Europe/London")}</b></div>', unsafe_allow_html=True)

st.divider()

# --- LAYOUT PRINCIPAL ---
col_grid, col_side = st.columns([3, 1.2])

with col_grid:
    st.markdown("### GRADE PRINCIPAL DE ATIVOS")
    ativos = ["SPOT", "DOLFUT", "DXY", "EWZ", "PRÉ/PÓS MARKET", "EUR/USD", "XAU/USD", "PETROLEO BRENT"]
    df = pd.DataFrame({
        "ATIVO": ativos,
        "PRICE": ["—"] * 8, "CLOSE": ["—"] * 8, "OPEN": ["—"] * 8,
        "MAX": ["—"] * 8, "MIN": ["—"] * 8, "VAR": ["0,00%"] * 8
    }).set_index("ATIVO")
    st.table(df)

with col_side:
    st.markdown("### PAINEL DE CÁLCULOS")
    
    # Input do PAINEL ADM e CLOSE
    painel_adm = st.number_input("PAINEL ADM:", value=5.4000, format="%.4f")
    st.write(f"Ajustes: `[1,0020]` | `[1,0070]` | `[1,0080]`")
    
    close_val = st.number_input("DIGITE O CLOSE PARA CÁLCULO:", value=5.4000, format="%.4f", step=0.0001)
    
    # Aplicação exata da lógica do rascunho
    calc_data = [
        ("3,00%", 1.030), ("2,34%", 1.0234), ("2,00%", 1.020),
        ("1,34%", 1.0134), ("1,00%", 1.010), ("0,34%", 1.0034)
    ]
    calc_neg = [
        ("-0,66%", 0.9934), ("-1,00%", 0.99), ("-1,66%", 0.9834),
        ("-2,00%", 0.98), ("-2,66%", 0.9734), ("-3,00%", 0.97)
    ]

    # Renderização da lista de cálculos
    for label, mult in calc_data:
        st.markdown(f'<div class="calc-row"><span>{label}</span><span>{close_val * mult:.4f}</span></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="eixo-close">CLOSE CENTER DATA EIXO: {close_val:.4f}</div>', unsafe_allow_html=True)
    
    for label, mult in calc_neg:
        st.markdown(f'<div class="calc-row"><span>{label}</span><span>{close_val * mult:.4f}</span></div>', unsafe_allow_html=True)

# --- RODAPÉ ---
st.markdown("---")
st.markdown("DXY 0,01% | EURUSD 0,01% | EWZ 0,0% | SPOT 0,0% | GBPUSD 1,00% | JPY/USD 0,00% | XAUUSD 0,00%")

# Refresh para manter relógios ativos
time.sleep(1)
st.rerun()
