import streamlit as st
import yfinance as yf
import time
import pandas as pd

# Configuração de Layout para Tablet
st.set_page_config(page_title="K97 - TERMINAL", layout="wide")

# --- MOTOR DE CÁLCULO K97 ---
def calcular_dolfut_k97(eixo_ewz, preco_ewz_atual, eixo_dolfut_manual):
    try:
        # Variação: (EIXO FIXO SEXTA / PREÇO VIVO AGORA - 1) * 100 / 2
        var_ewz = ((eixo_ewz / preco_ewz_atual) - 1) * 100 / 2
        preco_sintetico = eixo_dolfut_manual * (1 + (var_ewz / 100))
        return preco_sintetico, var_ewz
    except:
        return eixo_dolfut_manual, 0.0

# --- CAPTURA DE DADOS ---
@st.cache_data(ttl=5)
def fetch_ewz_k97():
    try:
        t = yf.Ticker("EWZ")
        # Puxamos 7 dias para garantir que a Sexta (06/03) esteja completa no histórico
        df = t.history(period="7d", interval="1m", prepost=True)
        
        if not df.empty:
            # 1. LOCALIZAR SEXTA-FEIRA (06/03) PARA O EIXO FIXO
            # Filtramos o DataFrame para pegar apenas as linhas do dia 06/03
            df_sexta = df[df.index.strftime('%Y-%m-%d') == '2026-03-06']
            
            # Filtro do pregão regular (11:30 às 18:00) conforme sua regra
            df_regular = df_sexta.between_time('11:30', '18:00')
            
            # CÁLCULO DO EIXO (VALOR CONGELADO)
            max_sexta = df_regular['High'].max()
            min_sexta = df_regular['Low'].min()
            eixo_fixo = (max_sexta + min_sexta) / 2
            
            # 2. PREÇO VIVO (Último clique do Pre-market de HOJE)
            preco_agora = df['Close'].iloc[-1]
            
            return {
                "price": preco_agora,
                "eixo_estatico": eixo_fixo,
                "max_s": max_sexta,
                "min_s": min_sexta
            }
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
    .elastic-row { display: flex; justify-content: space-between; padding: 5px 10px; border-bottom: 1px solid #1e2226; font-family: 'monospace'; }
    .eixo-destaque { border: 2px dashed #00f2ff; color: #ffcc00; text-align: center; padding: 15px; font-size: 26px; font-weight: 900; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL K97</span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ AJUSTE MANUAL")
    eixo_dol_input = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")

market = fetch_ewz_k97()

if market:
    eixo_fixo = market["eixo_estatico"]
    p_dolfut, v_desvio = calcular_dolfut_k97(eixo_fixo, market["price"], eixo_dol_input)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">EWZ (PREÇO AGORA - PRE-MARKET)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val">{market["price"]:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #848e9c; font-size: 14px;">Eixo Fixo (06/03): {eixo_fixo:.2f} (M: {market["max_s"]:.2f} / m: {market["min_s"]:.2f})</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">DOLFUT SINTÉTICO (K97)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val">{p_dolfut:.2f}</div>', unsafe_allow_html=True)
        color = "#00ff88" if v_desvio >= 0 else "#ff4d4d"
        st.markdown(f'<div style="color: {color}; font-weight:bold; font-size: 20px;">Desvio: {v_desvio:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- GRID DE ELÁSTICO ---
    st.markdown('<div class="frame-box" style="margin-top:20px; border-top: 4px solid #ffcc00;">', unsafe_allow_html=True)
    p_vars = [1.0, 0.62, 0.31]
    for p in p_vars:
        up = p_dolfut * (1 + (p/100))
        st.markdown(f'<div class="elastic-row"><span style="color:#ff4d4d;">RESISTÊNCIA +{p}%</span> <span>{up:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="elastic-row" style="background:#1e2226;"><span style="color:#00f2ff;">CENTRO SINTÉTICO</span> <span>{p_dolfut:.2f}</span></div>', unsafe_allow_html=True)
    for p in reversed(p_vars):
        down = p_dolfut * (1 - (p/100))
        st.markdown(f'<div class="elastic-row"><span style="color:#00ff88;">SUPORTE -{p}%</span> <span>{down:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-destaque">EIXO DÓLAR ANCORADO: {eixo_dol_input:.2f}</div>', unsafe_allow_html=True)
else:
    st.error("Buscando dados da Sexta (06/03) e Pre-market...")

time.sleep(5)
st.rerun()
