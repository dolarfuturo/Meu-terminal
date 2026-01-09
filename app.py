import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="ATA", layout="centered")

# 2. Inicialização da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Limpeza Total e Layout Vertical Espaçado
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    /* Fonte Quadrada Bloomberg */
    html, body, [class*="st-"], div, span, p {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    /* MATAR O CABEÇALHO (Remove o erro Keyboard) */
    header[data-testid="stHeader"] { visibility: hidden; display: none !important; }
    .block-container { padding-top: 1rem !important; }

    .stApp { background-color: #000000; color: #FFFFFF; }

    /* Título ATA */
    .terminal-title {
        font-size: 26px;
        color: #FFFFFF;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        letter-spacing: 5px;
    }

    /* Blocos Verticais Largos */
    .v-card {
        background: #0A0A0A;
        border: 1px solid #222;
        padding: 25px;
        margin-bottom: 25px;
        border-radius: 4px;
    }

    .label-min { font-size: 13px; color: #666; margin-bottom: 10px; }
    .price-big { font-size: 50px; color: #FFB900; font-weight: bold; line-height: 1; }
    .var-big { font-size: 26px; font-
