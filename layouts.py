import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: ESTILIZAÇÃO SUPER COMPACTA E REMOÇÃO DE MENUS ---
st.markdown("""
<style>
    /* Remove a barra preta do topo e o menu do Streamlit */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background-color: #050a0e !important; }
    
    /* Ajuste de margem do bloco principal para subir o conteúdo */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }

    /* Redução vertical geral (aprox 30%) */
    .main-grid { border: 2px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 5px !important; text-align: center; font-size: 11px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 6px !important; text-align: center; font-size: 13px; line-height: 1.1; }
    
    .asset-name { font-size: 14px !important; color: #fff; text-align: left; font-weight: bold; padding-left: 10px !important; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    
    /* Header BAIR reduzido */
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 4px 10px; border-bottom: 2px solid #ffffff; margin-bottom: 8px; }
    .bair-text { font-size: 32px !important; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -2px; } 
    .sep-text { font-size: 32px !important; color: #ffffff; font-weight: 950; margin: 0 4px; }
    .terminal-text { font-size: 32px !important; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -2px; }
    
    /* Relógios Compactados na vertical */
    .clock-container { display: flex; gap: 6px; }
    .clock-box { text-align: center; border: 1px solid #ffffff; padding: 2px 8px; border-radius: 4px; background: #0a141a; min-width: 80px; }
    .clock-label { font-size: 8px !important; color: #d4a017; font-weight: bold; display: block; margin-bottom: 0px; }
    .clock-time { color: #fff; font-size: 14px !important; font-weight: bold; display: block; line-height: 1.1; }
    
    /* Painéis de Cálculo reduzidos */
    .calc-panel { border: 2px solid #ffffff; border-radius: 8px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 6px; }
    .calc-row { display: flex; justify-content: space-between; padding: 3px 6px; border-bottom: 1px solid #444; font-size: 11px; font-weight: bold; align-items: center; }
    .axis-box { text-align:center; padding: 5px !important; color: #00f2ff; font-size: 14px !important; font-weight: bold; border-top:1px solid #444; border-bottom:1px solid #444; margin: 3px 0; }
    
    /* Ticker compactado */
    .ticker-wrapper { padding: 4px 0 !important; margin-top: 8px !important; }
    .ticker-text { font-size: 12px !important; }
    
    .monitor-bar { padding: 4px !important; font-size: 12px !important; margin-bottom: 5px !important; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        ref_close = t.info.get('previousClose')
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: 
            return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
