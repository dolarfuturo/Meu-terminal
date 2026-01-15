import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO INICIAL
st.set_page_config(page_title="TERMINAL", layout="wide")

# 2. ESTILO CSS (DARK MODE PROFISSIONAL)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 600px !important; margin: auto; }
    
    .main-title { font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 15px; color: #00FF00; }
    .asset-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding: 5px; border-bottom: 1px solid #111; }
    .name { font-size: 16px; color: #888; }
    .price { font-size: 18px; font-weight: bold; color: #FFF; }
    .var { font-size: 16px; font-weight: bold; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 16px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. FUNÇÃO COM CACHE (EVITA TRAVAMENTO)
@st.cache_data(ttl=60)
def fetch_finance_data(ticker):
    try:
        asset = yf.Ticker(ticker)
        df = asset.history(period="2d")
        if len(df) >= 2:
            price = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            var = ((price - prev) / prev) * 100
            return price, var
        return 0.0, 0.0
    except:
        return 0.0, 0.0

# --- INTERFACE ---
st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

# Ajuste de Parâmetros
with st.expander("⚙️ AJUSTAR PARÂMETROS"):
    v_aj = st.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_ptax_m = st.number_input("PTAX", value=5.3850, format="%.4f")

# Lista de Ativos
ativos = {
    "DÓLAR B3": "USDBRL=X",
    "DXY INDEX": "DX-Y.NYB",
    "S&P 500": "ES=F"
}

for nome, ticker in ativos.items():
    valor, variacao = fetch_finance_data(ticker)
    cor = "pos" if variacao >= 0 else "neg"
    
    st.markdown(f"""
    <div class="asset-row">
        <span class="name">{nome}</span>
        <span class="price">{valor:.3f if "DXY" not in nome else valor:.2f}</span>
        <span class="var {cor}">{variacao:+.2f}%</span>
    </div>
    """, unsafe_allow_html=True)

# Rodapé de Cálculo
st.markdown(f'<div class="trava-orange">VARIAÇÃO REF. AJUSTE: {v_aj}</div>', unsafe_allow_html=True)

# Botão de refresh manual se precisar
if st.button("ATUALIZAR"):
    st.rerun()
