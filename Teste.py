import streamlit as st
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import hashlib

# 1. SETUP ALPHA & TRAVA DE SEGURANÇA 
st.set_page_config(page_title="SHARK VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

# CSS MESTRE: TOPO TRAVADO E PONTO GLOW PISCANDO
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }

    /* TRAVA O CABEÇALHO NO TOPO */
    [data-testid="stVerticalBlock"] > div:first-child {
        position: sticky;
        top: 0;
        z-index: 999999;
        background-color: #000000;
        border-bottom: 2px solid #D4AF37;
    }

    /* PONTO VERDE PISCANDO (GLOW) */
    .dot { 
        height: 12px !important; 
        width: 12px !important; 
        background-color: #00FF00 !important; 
        border-radius: 50% !important; 
        display: inline-block !important;
        box-shadow: 0 0 10px #00FF00 !important;
        animation: pulse-glow 1s infinite alternate !important;
        margin-right: 8px !important;
    }
    @keyframes pulse-glow {
        from { opacity: 1; transform: scale(1); box-shadow: 0 0 5px #00FF00; }
        to { opacity: 0.2; transform: scale(0.8); box-shadow: 0 0 15px #00FF00; }
    }

    .title-gold { color: #D4AF37; font-size: 26px; font-weight: 900; text-align: center; margin: 5px 0; }
    .header-grid { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; background: #080808; padding: 10px 0; }
    .h-col { font-size: 9px; color: #FFF; text-align: center; font-weight: bold; }
    .row-container { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; align-items: center; padding: 12px 0; border-bottom: 1px solid #222; }
    .w-col { text-align: center; font-family: monospace; font-size: 15px; font-weight: bold; color: #FFF; }
    .vision-block { display: flex; justify-content: center; gap: 30px; padding: 5px 0; background: #050505; border-bottom: 2px solid #333; }
    
    /* BOTÃO CUSTOMIZADO */
    div.stButton > button {
        background-color: #D4AF37;
        color: black;
        font-weight: bold;
        width: 100%;
        border-radius: 5px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

def verificar_acesso():
    URL_SISTEMA = "https://docs.google.com/spreadsheets/d/1m86_Lj5p7tV9U4sNIKudbU1DVWFgAfaSXSIRATo6G70/export?format=csv"
    CHAVE_MESTRA_ADM = "SHARK_ADM_2026" 
    
    if "autenticado" not in st.session_state:
        st.markdown("<h1 style='text-align:center; color:#D4AF37; font-family:monospace;'>SHAKE VISION LOGIN</h1>", unsafe_allow_html=True)
