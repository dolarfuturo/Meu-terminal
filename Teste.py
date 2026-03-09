import streamlit as st
import yfinance as yf
import time

# Configuração de Layout
st.set_page_config(page_title="K97 - SINTÉTICO", layout="wide")

# --- MOTOR DE CÁLCULO K97 ---
def calcular_dolfut_k97(eixo_ewz, preco_ewz_atual, eixo_dolfut_manual):
    try:
        # Sua fórmula: (EIXO / PREÇO - 1) * 100 / 2
        var_ewz = ((eixo_ewz / preco_ewz_atual) - 1) * 100 / 2
        
        # DOLFUT = eixo do dol * (1 + variação/100)
        preco_sintetico = eixo_dolfut_manual * (1 + (var_ewz / 100))
        
        return preco_sintetico, var_ewz
    except:
        return eixo_dolfut_manual, 0.0

# --- CAPTURA DE DADOS (EWZ) ---
@st.cache_data(ttl=10)
def fetch_ewz():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d")
        if not df.empty:
            return {
                "price": df['Close'].iloc[-1],
                "max": df['High'].iloc[-1],
                "min": df['Low'].iloc[-1]
            }
    except:
        return None

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .frame-box { border: 2px solid #3d444d; border-top: 4px solid #00f2ff; padding: 20px; background: #0b0e11; border-radius: 4px; }
    .metric-val { font-size: 40px; font-family: 'Arial Black'; font-weight: 900; color: #ffffff; }
    .metric-label { font-size: 14px; color: #00f2ff; font-weight: bold; }
    .eixo-destaque { border: 2px dashed #00f2ff; color: #ffcc00; text-align: center; padding: 15px; font-size: 24px; font-weight: 900; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFACE PRINCIPAL ---
st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL K97</span></div>', unsafe_allow_html=True)

# Sidebar para ajuste manual
with st.sidebar:
    st.header("⚙️ AJUSTE MANUAL")
    eixo_dol_input = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")

# Execução
market = fetch_ewz()

if market:
    # Eixo EWZ automático (Max+Min)/2
    eixo_ewz_calc = (market["max"] + market["min"]) / 2
    
    # Cálculo do seu DOLFUT
    p_dolfut, v_desvio = calcular_dolfut_k97(eixo_ewz_calc, market["price"], eixo_dol_input)

    # Display em Colunas
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-label">EWZ (REAL-TIME)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val">{market["price"]:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #848e9c;">Eixo: {eixo_ewz_calc:.22f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-label">DOLFUT SINTÉTICO (K97)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val">{p_dolfut:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: {"#00ff88" if v_desvio >= 0 else "#ff4d4d"}; font-weight:bold;">Desvio: {v_desvio:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-destaque">EIXO DÓLAR ANCORADO: {eixo_dol_input:.2f}</div>', unsafe_allow_html=True)

else:
    st.error("Aguardando conexão com dados do EWZ...")

# Loop de atualização
time.sleep(10)
st.rerun()
