import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL", layout="wide")

# 2. Memória da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Letras Quadradas e Estética Clean
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    html, body, [class*="st-"], div, span, p {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    .stApp { 
        background-color: #000000; 
        color: #FFFFFF; 
    }

    /* Limpeza de Topo */
    header {visibility: hidden;}
    .block-container {padding-top: 0.5rem !important;}

    /* Título */
    .terminal-title {
        font-size: 24px;
        color: #FFFFFF;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 5px;
    }

    /* Linhas de Ativos */
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0px;
        border-bottom: 1px solid #222;
        background-color: #000000;
    }

    .ticker-name { font-size: 15px; color: #FFFFFF; width: 180px; font-weight: bold; }
    .ticker-price { font-size: 26px; color: #FFB900; width: 160px; text-align: right; font-weight: bold; }
    .ticker-var { font-size: 20px; width: 110px; text-align: right; font-weight: bold; }

    /* FRP */
    .frp-container { display: flex; gap: 20px; }
    .frp-item { text-align: right; }
    .frp-label { font-size: 10px; color: #666; display: block; }
    .frp-value { font-size: 18px; font-weight: bold; }

    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }

    /* Alvo */
    .alvo-box {
        background-color: #080808;
        border: 1px solid #333;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #FFB900;
    }
    .alvo-label { font-size: 13px; color: #FFFFFF; }
    .alvo-price { font-size: 38px; color: #FFB900; font-weight: bold; }
    
    /* Estilo do Expander (SET Escondido) */
    .stExpander {
        border: none !important;
        background-color: #111 !important;
        margin-bottom: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Título e SET Escondido (Expander)
st.markdown('<div class="terminal-title">TERMINAL DE CAMBIO</div>', unsafe_allow_html=True)

with st.expander("⚙️ ACESSAR VARIÁVEIS (SET)"):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    with col2:
        v_min = st.number_input("PTS MIN", value=22.0, step=0.5)
    with col3:
        v_jus = st.number_input("PTS JUS", value=31.0, step=0.5)
    with col4:
        v_max = st.number_input("PTS MAX", value=42.0, step=0.5)
    with col5:
        st.write("") # Espaçador
        if st.button("RESET 16H"): 
            st.session_state.spot_ref_locked = None

def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 5. Renderização dos Dados
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = get_live_data("BRL=X")
        dxy_df = get_live_data("DX-Y.NYB")
        ewz_df = get_live_data("EWZ")
        now_br = datetime.now() - timedelta(hours=3)
        is_pre = now_br.time() < datetime.strptime("11:30", "%H:%M").time()

        if not spot_df.empty:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Trava 16h
            try:
                lock_data = spot_df.between_time('15:58', '16:02')
                if not lock_data.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
            except: pass
            trava_val = st.session_
