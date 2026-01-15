import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO (Deve ser a primeira linha de comando Streamlit)
st.set_page_config(page_title="TERMINAL DE CÂMBIO", layout="wide")

# 2. ESTILO CSS MELHORADO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Esconde elementos desnecessários do Streamlit */
    header, [data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
    
    .block-container { padding-top: 1rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    
    .main-title { font-size: 22px; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 5px; margin-bottom: 20px; color: #00FF00; }
    
    .asset-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding: 5px; border-bottom: 1px solid #111; }
    .name { width: 40%; font-size: 16px; color: #888; }
    .price { width: 30%; font-size: 18px; font-weight: bold; text-align: right; }
    .var { width: 30%; font-size: 16px; font-weight: bold; text-align: right; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
</style>
""", unsafe_allow_html=True)

# 3. FUNÇÃO PARA BUSCAR DADOS (Com Cache para não travar)
@st.cache_data(ttl=60) # Atualiza a cada 60 segundos
def get_data(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="2d")
        if len(hist) < 2: return "N/A", 0
        
        price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2]
        change = ((price - prev_price) / prev_price) * 100
        return price, change
    except:
        return 0, 0

# 4. INTERFACE PRINCIPAL
st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

# Barra Lateral ou Popover para Parâmetros
with st.expander("⚙️ AJUSTAR PARÂMETROS"):
    col1, col2 = st.columns(2)
    with col1:
        v_aj = st.number_input("AJUSTE", value=5.3900, format="%.4f")
    with col2:
        v_ptax_m = st.number_input("PTAX", value=5.3850, format="%.4f")

# 5. MONITOR DE ATIVOS
assets = {
    "DÓLAR B3 (WDO)": "USDBRL=X",
    "DXY (ÍNDICE)": "DX-Y.NYB",
    "S&P 500 FUT": "ES=F"
}

for label, ticker in assets.items():
    p, v = get_data(ticker)
    color_class = "pos" if v >= 0 else "neg"
    
    st.markdown(f"""
    <div class="asset-row">
        <div class="name">{label}</div>
        <div class="price">{p:.3f}</div>
        <div class="var {color_class}">{v:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# 6. CÁLCULO DE VARIAÇÃO DO DIA (EXEMPLO)
st.markdown(f'<div class="trava-orange">VARIAÇÃO AJUSTE: {v_aj}</div>', unsafe_allow_html=True)

# Botão de Atualizar Manual
if st.button("🔄 ATUALIZAR AGORA"):
    st.rerun()
