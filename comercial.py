import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

if 'ref_base' not in st.session_state:
    st.session_state.ref_base = 0.0

# 2. ESTILO PROFISSIONAL RESTAURADO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 0.5rem !important; max-width: 850px !important; margin: auto; padding-bottom: 80px; }
    
    .terminal-header { 
        text-align: center; font-size: 14px; letter-spacing: 8px; color: #666; 
        border-bottom: 1px solid #222; padding-bottom: 10px; margin-bottom: 20px;
    }
    .terminal-title { color: #FFFFFF; font-weight: 700; }

    .data-row { 
        display: flex; justify-content: space-between; align-items: center; 
        padding: 18px 0; border-bottom: 1px solid #111;
    }
    .data-label { font-size: 11px; color: #FFFFFF; font-weight: 700; letter-spacing: 2px; width: 35%; }
    .data-value { font-size: 32px; font-weight: 700; width: 65%; text-align: right; }
    
    .sub-grid { display: flex; gap: 25px; justify-content: flex-end; width: 65%; }
    .sub-item { text-align: right; min-width: 105px; }
    .sub-label { font-size: 9px; color: #555; display: block; margin-bottom: 4px; font-weight: 700; }
    .sub-val { font-size: 24px; font-weight: 700; }

    .c-pari { color: #FFB900; }
    .c-equi { color: #00FFFF; }
    .c-max { color: #00FF80; } 
    .c-min { color: #FF4B4B; } 
    .c-jus { color: #0080FF; }

    .footer-bar {
        position: fixed; bottom: 0; left: 0; width: 100%; height: 40px;
