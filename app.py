import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="TERMINAL", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. INICIALIZAÇÃO DE ESTADO PARA A TRAVA
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - ESTILO TERMINAL DARK COM VARIÁVEIS NO TOPO
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Remove elementos nativos do Streamlit */
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    
    .block-container { padding-top: 1rem !important; max-width: 900px !important; margin: auto; }

    /* TÍTULO */
    .main-title { 
        font-size: 20px; font-weight: bold; color: #FFF; 
        text-align: left; padding-bottom: 10px; border-bottom: 1px solid #333; margin-bottom: 15px;
    }

    /* CONTAINER DE VARIÁVEIS */
    .vars-box {
        background-color: #111; padding: 10px; border-radius: 4px;
        margin-bottom: 20px; border: 1px solid #222;
    }

    /* LINHAS DE ATIVOS */
    .asset-row { display: flex; gap: 20px; margin-bottom: 8px; align-items: center; }
    .name { width: 150px; font-size: 17px; color: #888; }
    .price { width: 110px; font-size: 18px; font-weight: bold; }
    .var { font-size: 17px; font-weight: bold; }
    
    .price-paridade { color: #FFB900 !important; }
    .price-ptax { color: #00FFFF !important; }

    /* PONTOS VERTICAIS */
    .frp-box { margin-left: 170px; margin-top: -5px; margin-bottom: 12px; display: flex; flex-direction: column; gap: 2px; }
    .frp-item { display: flex; gap: 20px; font-size: 13px; font-weight: 400 !important; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 17px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
    
    /* Ajuste dos Inputs para ficarem compactos */
    div[data-baseweb="input"] { background-color: #000 !important; border: 1px solid #333 !important; height: 35px; }
    input { color: #00FF00 !important; font-size: 14px !important; }
    label { color: #666 !important; font-size: 10px !important; margin-bottom: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. TÍTULO E INPUTS (SUBSTITUINDO A SIDEBAR)
st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

with st.container():
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    with c2: val_ptax_manual = st.number_input("PTAX", value=5.3850, format="%.4f", step=0.0001)
    with c3: v_max =
