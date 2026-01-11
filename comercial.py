import streamlit as st
import time

st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

# ==========================================
# 1. EDITE OS VALORES BÁSICOS AQUI
# ==========================================
valor_ajuste = 5.4215
valor_referencial = 5.3705
vencimento = "FEV/26"  # Exemplo de vencimento
# ==========================================

# Cálculos Automáticos
diferencial = valor_ajuste - valor_referencial
preco_calculado = valor_ajuste + 0.0150 # Exemplo de fórmula, ajuste se necessário

# Estilo Visual (Preto e Amarelo/Ciano)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700;800&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    
    .row { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #222; }
    .label { font-size: 14px; font-weight: 700; color: #888; }
    .value { font-size: 32px; font-weight: 800; text-align: right; }
    
    .c-pari { color: #FFB900; } /* Amarelo */
    .c-equi { color: #00FFFF; } /* Ciano */
    .c-white { color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<div style="text-align:center; padding: 10px; color:#444; letter-spacing:5px; font-size:10px;">TERMINAL DE DADOS COMERCIAL</div>', unsafe_allow_html=True)

# --- EXIBIÇÃO DOS DADOS ---

# 1. Ajuste Mestre
st.markdown(f'<div class="row"><div class="label">AJUSTE MESTRE</div><div class="value c-pari">{valor_ajuste:.4f}</div></div>', unsafe_allow_html=True)

# 2. Preço (Ajuste + Cálculo)
st.markdown(f'<div class="row"><div class="label">PREÇO ESTIMADO</div><div class="value c-white">{preco_calculado:.4f}</div></div>', unsafe_allow_html=True)

# 3. Referencial
st.markdown(f'<div class="row"><div class="label">REFERENCIAL</div><div class="value c-equi">{valor_referencial:.4f}</div></div>', unsafe_allow_html=True)

# 4. Diferencial
st.markdown(f'<div class="row"><div class="label">DIFERENCIAL</div><div class="value c-white">{diferencial:.4f}</div></div>', unsafe_allow_html=True)

# 5. Vencimento
st.markdown(f'<div class="row"><div class="label">VENCIMENTO</div><div class="value c-pari" style="font-size:24px;">{vencimento}</div></div>', unsafe_allow_html=True)

# Botão de atualização manual
if st.button("🔄 ATUALIZAR"):
    st.rerun()

# Auto-refresh a cada 10 segundos
time.sleep(10)
st.rerun()
