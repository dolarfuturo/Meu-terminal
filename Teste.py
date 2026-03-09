import streamlit as st
import yfinance as yf
import time

# Configuração de Layout para Tablet
st.set_page_config(page_title="K97 - TERMINAL", layout="wide")

# --- MOTOR DE CÁLCULO K97 (SUA FÓRMULA VALIDADA) ---
def calcular_dolfut_k97(eixo_ewz, preco_ewz_atual, eixo_dolfut_manual):
    try:
        # (EIXO MANUAL / PREÇO ATUAL - 1) * 100 / 2
        var_ewz = ((eixo_ewz / preco_ewz_atual) - 1) * 100 / 2
        # DOLFUT = eixo do dol * (1 + variação/100)
        preco_sintetico = eixo_dolfut_manual * (1 + (var_ewz / 100))
        return preco_sintetico, var_ewz
    except:
        return eixo_dolfut_manual, 0.0

# --- CAPTURA DE DADOS (EWZ) - PRE-MARKET VIVO ---
@st.cache_data(ttl=5)
def fetch_ewz():
    try:
        t = yf.Ticker("EWZ")
        # prepost=True busca o movimento do Pre-market desde as 06h
        df = t.history(period="1d", interval="1m", prepost=True) 
        if not df.empty:
            return df['Close'].iloc[-1]
    except:
        return None

# --- ESTILO VISUAL TERMINAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .frame-box { border: 2px solid #3d444d; border-top: 4px solid #00f2ff; padding: 20px; background: #0b0e11; border-radius: 4px; }
    .metric-val { font-size: 44px; font-family: 'Arial Black'; font-weight: 900; color: #ffffff; }
    .metric-label { font-size: 14px; color: #00f2ff; font-weight: bold; }
    .eixo-destaque { border: 2px dashed #00f2ff; color: #ffcc00; text-align: center; padding: 15px; font-size: 26px; font-weight: 900; margin-top: 20px; }
    .elastic-row { display: flex; justify-content: space-between; padding: 5px 10px; border-bottom: 1px solid #1e2226; font-family: 'monospace'; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL K97</span></div>', unsafe_allow_html=True)

# --- SIDEBAR (CONTROLE TOTAL) ---
with st.sidebar:
    st.header("⚙️ AJUSTE MANUAL")
    # Agora você controla o Eixo do EWZ manualmente para travar o valor de sexta
    eixo_ewz_manual = st.number_input("EIXO EWZ (MANUAL):", value=27.72, format="%.2f")
    eixo_dol_input = st.number_input("EIXO DOLFUT (MANUAL):", value=5295.50, format="%.2f")

# Execução
preco_vivo = fetch_ewz()

if preco_vivo:
    # Cálculo do seu DOLFUT Sintético com Eixo Manual
    p_dolfut, v_desvio = calcular_dolfut_k97(eixo_ewz_manual, preco_vivo, eixo_dol_input)

    # Painel Principal
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-label">EWZ (PRE-MARKET VIVO)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val">{preco_vivo:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #848e9c; font-size: 18
