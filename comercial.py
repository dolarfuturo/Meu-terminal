import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

# Conexão forçando atualização constante
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_valores():
    # O parametro ttl=0 força o app a ler a planilha REAL toda vez, sem cache
    df = conn.read(worksheet="Sheet1", ttl=0) 
    return float(df.iloc[0, 0]), float(df.iloc[0, 1])

# ... (Mantenha o restante do estilo CSS que enviamos antes) ...

# No loop principal, use o ttl=0 também:
while True:
    try:
        # Lendo valores sem cache (ttl=0)
        aj_m, ref_m = carregar_valores() 
        # ... (restante do código de cálculos) ...
    except:
        time.sleep(2)
        st.rerun()
