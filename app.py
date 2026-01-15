import streamlit as st  # Corrigido: 'import' em minúsculo
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DO TERMINAL
st.set_page_config(page_title="TERMINAL", layout="wide")

# 2. ESTILO CSS (DARK MODE)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin: auto; }
    .main-title { font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 15px; }
    .asset-row { display: flex; gap: 20px; margin-bottom: 4px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 130px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .dist-box { background: #111; padding: 10px; border-radius: 5px; margin-top: 20px; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">TERMINAL DE CÂMBIO - QUANT</div>', unsafe_allow_html=True)

# 3. INPUTS NO POPOVER
with st.popover("⚙️ AJUSTAR PARÂMETROS"):
    v_aj = st.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_ptax_m = st.number_input("PTAX", value=5.3850, format="%.4f")
    # Seletor para o usuário escolher qual âncora usar agora
    ancora_ativa = st.radio("ÂNCORA ATIVA:", ["AJUSTE", "PTAX"], horizontal=True)

# 4. BUSCA DE DADOS (SPOT ATUAL)
@st.cache_data(ttl=5)
def get_spot():
    try:
        data = yf.Ticker("USDBRL=X").history(period="1d", interval="1m")
        return data['Close'].iloc[-1]
    except:
        return 5.3800 # Fallback caso a API falhe

spot = get_spot()
referencia = v_aj if ancora_ativa == "AJUSTE" else v_ptax_m

# 5. EXIBIÇÃO DO PREÇO ATUAL
st.markdown(f"""
<div class="asset-row">
    <div class="name">DÓLAR SPOT</div>
    <div class="price">{spot:.4f}</div>
    <div class="var {'pos' if spot >= referencia else 'neg'}">
        {((spot/referencia)-1)*100:.2f}%
    </div>
</div>
""", unsafe_allow_html=True)

# 6. LÓGICA DE DISTORÇÃO (O SEU +22, +31, +42)
st.markdown('<div class="dist-box">', unsafe_allow_html=True)
st.write(f"DISTORÇÕES SOBRE {ancora_ativa}:")

def mostrar_nivel(label, pontos):
    valor_nivel = referencia + (pontos / 1000)
    dist_atual = (spot - valor_nivel) * 1000
    color = "#FF0000" if spot > valor_nivel else "#00FF00"
    st.markdown(f"**{label} ({pontos} PTS):** {valor_nivel:.4f} | <span style='color:{color}'>DIST: {dist_atual:.1f} PTS</span>", unsafe_allow_html=True)

mostrar_nivel("NÍVEL 1", 22)
mostrar_nivel("NÍVEL 2", 31)
mostrar_nivel("NÍVEL 3", 42)
st.markdown('</div>', unsafe_allow_html=True)

# AUTO-REFRESH
time.sleep(5)
st.rerun()
