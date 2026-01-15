import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO (Deve ser a primeira linha)
st.set_page_config(page_title="TERMINAL", layout="wide")

# 2. ESTILO CSS - CORREÇÃO DE ÍCONES E LAYOUT
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 600px !important; margin: auto; }
    
    .main-title { font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 15px; color: #00FF00; }
    .asset-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding: 10px; border-bottom: 1px solid #111; background-color: #050505; }
    .name { font-size: 14px; color: #888; font-weight: bold; }
    .price { font-size: 18px; font-weight: bold; color: #FFF; }
    .var { font-size: 16px; font-weight: bold; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 16px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. FUNÇÃO DE DADOS (COM PROTEÇÃO CONTRA VALOR VAZIO)
@st.cache_data(ttl=30)
def fetch_finance_data(ticker):
    try:
        asset = yf.Ticker(ticker)
        df = asset.history(period="2d")
        if df.empty or len(df) < 2:
            return 0.0, 0.0
        
        price = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        var = ((price - prev) / prev) * 100
        return price, var
    except Exception:
        return 0.0, 0.0

# --- INTERFACE PRINCIPAL ---
st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

# Parâmetros em colunas simples (evita bug de ícone do expander)
col_p1, col_p2 = st.columns(2)
with col_p1:
    v_aj = st.number_input("AJUSTE", value=5.3900, format="%.4f")
with col_p2:
    v_ptax_m = st.number_input("PTAX", value=5.3850, format="%.4f")

st.markdown("---")

# Lista de Ativos
ativos = {
    "DÓLAR B3": "USDBRL=X",
    "DXY INDEX": "DX-Y.NYB",
    "S&P 500": "ES=F"
}

for nome, ticker in ativos.items():
    valor, variacao = fetch_finance_data(ticker)
    
    # Define a cor baseada na variação
    cor_classe = "pos" if variacao >= 0 else "neg"
    
    # FORMATAÇÃO SEGURA (Evita o ValueError do seu print)
    txt_valor = f"{valor:.3f}" if valor > 0 else "CARREGANDO..."
    txt_var = f"{variacao:+.2f}%" if valor > 0 else "0.00%"

    st.markdown(f"""
    <div class="asset-row">
        <span class="name">{nome}</span>
        <span class="price">{txt_valor}</span>
        <span class="var {cor_classe}">{txt_var}</span>
    </div>
    """, unsafe_allow_html=True)

# 4. RODAPÉ TÉCNICO
st.markdown(f'<div class="trava-orange">REF. AJUSTE: {v_aj:.4f}</div>', unsafe_allow_html=True)

if st.button("🔄 RECARREGA"):
    st.rerun()
