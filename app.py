import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página - Estilo Terminal Bloomberg
st.set_page_config(page_title="TERMINAL BLOOMBERG | SPREAD", layout="wide")

# CSS Bloomberg Style
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] { background-color: #000000; }
    
    [data-testid="stMetricLabel"] { 
        color: #FFFFFF !important; 
        font-size: 16px !important; 
        font-weight: 800 !important; 
        text-transform: uppercase;
    }
    
    [data-testid="stMetricValue"] { 
        color: #FFB900 !important; 
        font-family: 'Courier New', monospace; 
        font-size: 30px !important; 
    }
    
    .frp-box {
        border: 1px solid #333333;
        padding: 15px;
        background-color: #000000;
        border-radius: 5px;
        text-align: center;
    }
    
    .spread-box {
        border: 1px dashed #555555;
        padding: 10px;
        background-color: #111111;
        text-align: center;
        margin: 10px 0;
    }

    .price-text { font-size: 28px; font-family: 'Courier New'; font-weight: bold; margin-top: 5px; }
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: VARIÁVEIS ESCONDIDAS ---
st.sidebar.title("⌨️ COMANDOS")

# Usando expand
