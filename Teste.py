import streamlit as st
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import hashlib
import uuid
from streamlit_gsheets import GSheetsConnection

# 1. SETUP ALPHA & TRAVA DE SEGURANÇA 
st.set_page_config(page_title="SHARK VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

# CSS MANTIDO INTEGRALMENTE CONFORME SOLICITADO
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
    [data-testid="stVerticalBlock"] > div:first-child {
        position: sticky; top: 0; z-index: 999999; background-color: #000000; border-bottom: 2px solid #D4AF37;
    }
    .dot { 
        height: 12px !important; width: 12px !important; background-color: #00FF00 !important; 
        border-radius: 50% !important; display: inline-block !important;
        box-shadow: 0 0 10px #00FF00 !important; animation: pulse-glow 1s infinite alternate !important;
        margin-right: 8px !important;
    }
    @keyframes pulse-glow { from { opacity: 1; transform: scale(1); } to { opacity: 0.2; transform: scale(0.8); } }
    .title-gold { color: #D4AF37; font-size: 26px; font-weight: 900; text-align: center; margin: 5px 0; }
    .header-grid { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; background: #080808; padding: 10px 0; }
    .h-col { font-size: 9px; color: #FFF; text-align: center; font-weight: bold; }
    .row-container { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; align-items: center; padding: 12px 0; border-bottom: 1px solid #222; }
    .w-col { text-align: center; font-family: monospace; font-size: 15px; font-weight: bold; color: #FFF; }
    .vision-block { display: flex; justify-content: center; gap: 30px; padding: 5px 0; background: #050505; border-bottom: 2px solid #333; }
    div.stButton > button { background-color: #D4AF37; color: black; font-weight: bold; width: 100%; border-radius: 5px; border: none; }
    .stApp { background-color: #000000; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

def verificar_acesso():
    conn = st.connection("gsheets", type=GSheetsConnection)
    CHAVE_MESTRA_ADM = "SHARK_ADM_2026" 
    
    if "autenticado" not in st.session_state:
        st.markdown("<h1 style='text-align:center; color:#D4AF37; font-family:monospace;'>SHAKE VISION LOGIN</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            chave = st.text_input("", type="password", placeholder="Digite a Chave...")
            btn = st.button("ACESSAR TERMINAL CRYPTO")
        
        if btn and chave:
            if chave == CHAVE_MESTRA_ADM:
                st.session_state.update({"autenticado": True, "usuario": "ADMINISTRADOR", "role": "admin", "session_id": "MASTER"})
                st.rerun()
            
            try:
                df = conn.read(ttl=0)
                hash_t = hashlib.sha256(chave.encode()).hexdigest()
                df.columns = df.columns.str.strip()
                idx_list = df.index[(df['HASH_SENHA'].astype(str).str.strip() == hash_t) & (df['STATUS'].str.strip() == 'ATIVO')].tolist()
                
                if idx_list:
                    row_idx = idx_list[0]
                    novo_id = str(uuid.uuid4())[:8
