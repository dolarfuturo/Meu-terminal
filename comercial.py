import streamlit as st
import time

st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

# ==========================================
# EDITE OS VALORES ABAIXO QUANDO QUISER MUDAR
# ==========================================
valor_ajuste = 5.4215
valor_referencial = 5.3705
# ==========================================

# Estilo visual
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700;800&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid #111; }
    .data-label { font-size: 12px; font-weight: 700; color: #888; }
    .data-value { font-size: 38px; font-weight: 800; text-align: right; }
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="text-align:center; padding: 20px; color:#444; letter-spacing:5px;">TERMINAL ATIVO</div>', unsafe_allow_html=True)

# Exibição dos valores fixos
st.markdown(f'<div class="data-row"><div class="data-label">AJUSTE MESTRE</div><div class="data-value c-pari">{valor_ajuste:.4f}</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="data-row"><div class="data-label">REFERENCIAL</div><div class="data-value c-equi">{valor_referencial:.4f}</div></div>', unsafe_allow_html=True)

if st.button("🔄 ATUALIZAR"):
    st.rerun()

time.sleep(10)
st.rerun()
