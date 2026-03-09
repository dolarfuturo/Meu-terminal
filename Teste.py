import streamlit as st

# Configuração de Layout para Tablet
st.set_page_config(page_title="K97 - CALCULADORA", layout="wide")

# --- MOTOR DE CÁLCULO K97 ---
def calcular_dolfut_k97(eixo_ewz, preco_ewz_atual, eixo_dolfut_manual):
    try:
        # Fórmulas validadas conforme sua estratégia
        var_ewz = ((eixo_ewz / preco_ewz_atual) - 1) * 100 / 2
        preco_sintetico = eixo_dolfut_manual * (1 + (var_ewz / 100))
        return preco_sintetico, var_ewz
    except:
        return eixo_dolfut_manual, 0.0

# --- ESTILO VISUAL TERMINAL K97 ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .frame-box { border: 2px solid #3d444d; border-top: 4px solid #00f2ff; padding: 20px; background: #0b0e11; border-radius: 4px; }
    .metric-val { font-size: 44px; font-family: 'Arial Black'; font-weight: 900; color: #ffffff; }
    .metric-label { font-size: 14px; color: #00f2ff; font-weight: bold; }
    .elastic-row { display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #1e2226; font-family: 'monospace'; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- CALCULADORA K97</span></div>', unsafe_allow_html=True)

# --- ENTRADA DE DADOS MANUAL (PRECISÃO TOTAL) ---
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    eixo_ewz = st.number_input("EIXO EWZ (SEXTA):", value=35.70, format="%.2f")
with col_in2:
    preco_ewz_atual = st.number_input("PREÇO EWZ AGORA (T.VIEW):", value=35.70, format="%.2f")
with col_in3:
    eixo_dol = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")

# Cálculos
p_dolfut, v_desvio = calcular_dolfut_k97(eixo_ewz, preco_ewz_atual, eixo_dol)

# --- EXIBIÇÃO ---
col_res1, col_res2 = st.columns(2)

with col_res1:
    st.markdown('<div class="frame-box">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">VARIAÇÃO EWZ / 2</div>', unsafe_allow_html=True)
    color = "#00ff88" if v_desvio >= 0 else "#ff4d4d"
    st.markdown(f'<div class="metric-val" style="color:{color}">{v_desvio:+.2f}%</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_res2:
    st.markdown('<div class="frame-box">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">DÓLAR SINTÉTICO ALVO</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-val">{p_dolfut:.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- ALVOS DE ELÁSTICO ---
st.markdown('<div class="frame-box" style="margin-top:20px; border-top: 4px solid #ffcc00;">', unsafe_allow_html=True)
st.markdown('<div class="metric-label" style="color:#ffcc00; margin-bottom:10px;">VARIÁVEIS DE ELÁSTICO</div>', unsafe_allow_html=True)

p_vars = [1.0, 0.62, 0.31]
for p in p_vars:
    up = p_dolfut * (1 + (p/100))
    st.markdown(f'<div class="elastic-row"><span style="color:#ff4d4d;">RESISTÊNCIA +{p}%</span> <span>{up:.2f}</span></div>', unsafe_allow_html=True)

st.markdown(f'<div class="elastic-row" style="background:#1e2226;"><span style="color:#00f2ff;">CENTRO SINTÉTICO</span> <span>{p_dolfut:.2f}</span></div>', unsafe_allow_html=True)

for p in reversed(p_vars):
    down = p_dolfut * (1 - (p/100))
    st.markdown(f'<div class="elastic-row"><span style="color:#00ff88;">SUPORTE -{p}%</span> <span>{down:.2f}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
