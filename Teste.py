import streamlit as st

# Configuração para Tablet (Foco em Usabilidade)
st.set_page_config(page_title="K97 - OPERACIONAL", layout="wide")

# --- LÓGICA DE CÁLCULO K97 ---
def calcular_k97(eixo_ewz, preco_atual, eixo_dol):
    try:
        # Variação: (Eixo / Preço - 1) * 100 / 2
        var_ewz = ((eixo_ewz / preco_atual) - 1) * 100 / 2
        p_sintetico = eixo_dol * (1 + (var_ewz / 100))
        return p_sintetico, var_ewz
    except:
        return eixo_dol, 0.0

# --- INTERFACE VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .frame-box { border: 2px solid #3d444d; border-top: 4px solid #00f2ff; padding: 20px; background: #161b22; border-radius: 4px; }
    .metric-val { font-size: 50px; font-family: 'Arial Black'; font-weight: 900; color: #ffffff; line-height: 1; }
    .metric-label { font-size: 16px; color: #00f2ff; font-weight: bold; margin-bottom: 10px; }
    .elastic-row { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #30363d; font-family: 'monospace'; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- OPERACIONAL K97</span></div>', unsafe_allow_html=True)

# --- ENTRADA DE DADOS (RÁPIDA) ---
with st.container():
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        eixo_ewz = st.number_input("EIXO EWZ (FIXO):", value=35.70, step=0.01, format="%.2f")
    with col_in2:
        preco_vivo = st.number_input("PREÇO EWZ (T. VIEW):", value=35.70, step=0.01, format="%.2f")
    with col_in3:
        eixo_dol = st.number_input("EIXO DOLFUT:", value=5295.50, step=0.50, format="%.2f")

# Processamento
p_sintetico, v_desvio = calcular_k97(eixo_ewz, preco_vivo, eixo_dol)

# --- RESULTADO PRINCIPAL ---
st.markdown("---")
col_res1, col_res2 = st.columns(2)

with col_res1:
    st.markdown('<div class="frame-box">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">DÓLAR SINTÉTICO</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-val">{p_sintetico:.2f}</div>', unsafe_allow_html=True)
    color = "#00ff88" if v_desvio >= 0 else "#ff4d4d"
    st.markdown(f'<div style="color:{color}; font-size:24px; font-weight:bold;">Desvio: {v_desvio:+.2f}%</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_res2:
    st.markdown('<div class="frame-box" style="border-top: 4px solid #ffcc00;">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label" style="color:#ffcc00;">ALVOS DO ELÁSTICO</div>', unsafe_allow_html=True)
    
    p_vars = [1.0, 0.62, 0.31]
    # Resistências
    for p in p_vars:
        val = p_sintetico * (1 + (p/100))
        st.markdown(f'<div class="elastic-row"><span style="color:#ff4d4d;">+{p}%</span> <span>{val:.2f}</span></div>', unsafe_allow_html=True)
    
    # Suportes
    for p in reversed(p_vars):
        val = p_sintetico * (1 - (p/100))
        st.markdown(f'<div class="elastic-row"><span style="color:#00ff88;">-{p}%</span> <span>{val:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:center; margin-top:30px; color:#3d444d; font-size:12px;">TERMINAL K97 | FOCO EM EXECUÇÃO</div>', unsafe_allow_html=True)
