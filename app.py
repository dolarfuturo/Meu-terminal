import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. CONFIGURAÇÃO - Sidebar aberta por padrão e layout largo
st.set_page_config(
    page_title="TERMINAL", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. INICIALIZAÇÃO DE ESTADO
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - ESTILO TERMINAL (VARIAVEIS FIXAS À ESQUERDA, TOPO LIMPO)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Esconde cabeçalho nativo e qualquer botão de menu no topo */
    header { visibility: hidden; display: none !important; }
    [data-testid="stHeader"] { display: none !important; }
    
    /* Esconde o botão de fechar (X) da barra lateral para ela ficar fixa */
    button[kind="headerNoPadding"] { display: none !important; }
    section[data-testid="stSidebarNav"] { display: none !important; }

    /* Ajuste de margens */
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin-left: 10px; }
    
    /* Barra Lateral de Variáveis */
    [data-testid="stSidebar"] { 
        background-color: #111111 !important; 
        border-right: 1px solid #333; 
        min-width: 250px !important;
    }

    .terminal-header { font-size: 18px; font-weight: bold; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 5px; }
    .asset-row { display: flex; gap: 20px; margin-bottom: 12px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 110px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    
    .price-paridade { color: #FFB900 !important; }
    .price-ptax { color: #00FFFF !important; }

    /* Pontos menores e sem negrito (VERTICAL) */
    .frp-box { margin-left: 180px; margin-top: -5px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 2px; }
    .frp-item { display: flex; gap: 25px; font-size: 13px; font-weight: 400 !important; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 15px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. PAINEL DE VARIÁVEIS (FIXO À ESQUERDA)
with st.sidebar:
    st.markdown("### ⚙️ SET DE VARIÁVEIS")
    st.write("---")
    val_aj_manual = st.number_input("AJUSTE MANUAL", value=5.3900, format="%.4f", step=0.0001)
    val_ptax_manual = st.number_input("VALOR PTAX", value=5.3850, format="%.4f", step=0.0001)
    st.write("---")
    st.markdown("### 📊 PONTOS (PTS)")
    v_max = st.number_input("MAXIMA", value=42.0)
    v_jus = st.number_input("JUSTO", value=31.0)
    v_min = st.number_input("MINIMA", value=22.0)
    st.write("---")
    if st.button("LIMPAR TRAVA 16H"):
        st.session_state.spot_ref_locked = None

# Interface Principal
st.markdown('<div class="terminal-header">TERMINAL DE CAMBIO</div>', unsafe_allow_html=True)

def fetch_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False)
        return data if not data.empty else None
    except: return None

# 5. LOOP DE ATUALIZAÇÃO (2 SEGUNDOS)
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = fetch_data("BRL=X")
        dxy_df = fetch_data("DX-Y.NYB")
        ewz_df = fetch_data("EWZ")

        if spot_df is not None:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            try:
                lock = spot_df.between_time('15:58', '16:02')
                if not lock.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_
