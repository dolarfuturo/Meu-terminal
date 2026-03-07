import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet (Ocupar 100% da largura)
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS CUSTOMIZADO PARA COPIAR O LAYOUT DA IMAGEM
st.markdown("""
    <style>
    /* Fundo e Cores Globais */
    .stApp { background-color: #0b0e11; color: #e0e0e0; }
    
    /* Título BAIR */
    .bair-title { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 38px; letter-spacing: 2px; margin-bottom: -10px; }
    
    /* Relógios e Cabeçalhos */
    .header-box { text-align: center; border: 1px solid #1f2329; padding: 10px; border-radius: 4px; background: #161b22; }
    .clock-time { color: #ffffff; font-size: 28px; font-weight: bold; font-family: 'Courier New', monospace; }
    .clock-label { color: #848e9c; font-size: 14px; text-transform: uppercase; }

    /* Grades e Tabelas */
    .grid-container { border: 1px solid #00f2ff; padding: 0px; border-radius: 2px; }
    th { color: #848e9c !important; text-transform: uppercase; font-size: 12px; border-bottom: 1px solid #1f2329 !important; }
    td { font-family: 'Courier New', monospace; font-size: 18px; border-bottom: 1px solid #1f2329 !important; padding: 12px !important; }

    /* Painel de Cálculos Lateral */
    .calc-panel { border: 1px solid #00f2ff; padding: 15px; background: #0b0e11; height: 100%; }
    .calc-title { color: #00f2ff; font-size: 16px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #00f2ff; padding-bottom: 5px; }
    .calc-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-family: 'Courier New', monospace; }
    .perc-green { color: #00ff88; font-weight: bold; }
    .perc-red { color: #ff4d4d; font-weight: bold; }
    .formula-text { color: #848e9c; font-size: 14px; }
    .eixo-data { background: #00f2ff; color: #000; font-weight: bold; text-align: center; padding: 5px; margin: 15px 0; border-radius: 2px; }

    /* Rodapé Ticker */
    .footer-ticker { border-top: 1px solid #00f2ff; padding: 10px; font-family: monospace; font-size: 14px; color: #00f2ff; margin-top: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER (TÍTULO E RELÓGIOS) ---
col_t, col_b, col_n, col_l = st.columns([2.5, 1, 1, 1])

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

st.write("") # Espaçador

# --- CORPO PRINCIPAL ---
col_main, col_side
