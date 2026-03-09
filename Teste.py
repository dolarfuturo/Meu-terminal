import streamlit as st
import yfinance as yf
import time

# Configuração de Layout para Tablet
st.set_page_config(page_title="K97 - TERMINAL ELÁSTICO", layout="wide")

# --- MOTOR DE CÁLCULO K97 ---
def calcular_dolfut_k97(eixo_ewz, preco_ewz_atual, eixo_dolfut_manual):
    try:
        # Fórmula Invertida: (EIXO / PREÇO - 1) * 100 / 2
        var_ewz = ((eixo_ewz / preco_ewz_atual) - 1) * 100 / 2
        # Preço Sintético Central
        preco_sintetico = eixo_dolfut_manual * (1 + (var_ewz / 100))
        return preco_sintetico, var_ewz
    except:
        return eixo_dolfut_manual, 0.0

# --- CAPTURA DE DADOS ---
@st.cache_data(ttl=10)
def fetch_ewz():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d")
        if not df.empty:
            return {
                "price": df['Close'].iloc[-1],
                "max": df['High'].max(),
                "min": df['Low'].min()
            }
    except:
        return None

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .frame-box { border: 2px solid #3d444d; border-top: 4px solid #00f2ff; padding: 15px; background: #0b0e11; border-radius: 4px; text-align: center; }
    .metric-val { font-size: 38px; font-family: 'Arial Black'; font-weight: 900; color: #ffffff; }
    .elastic-box { padding: 10px; border-radius: 4px; margin: 5px 0; font-family: 'Courier New'; font-weight: bold; }
    .up-band { background-color: rgba(255, 77, 77, 0.1); border-left: 4px solid #ff4d4d; color: #ff4d4d; }
    .down-band { background-color: rgba(0, 255, 136, 0.1); border-left: 4px solid #00ff88; color: #00ff88; }
    .center-band { background-color: rgba(0, 242, 255, 0.1); border-left: 4px solid #00f2ff; color: #00f2ff; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL K97</span></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ AJUSTE MANUAL")
    eixo_dol_input = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")
    eixo_ewz_manual = st.number_input("EIXO EWZ (FIXO):", value=36.56, format="%.2f")

market = fetch_ewz()

if market:
    # Cálculo Principal
    p_dolfut, v_desvio = calcular_dolfut_k97(eixo_ewz_manual, market["price"], eixo_dol_input)

    # Definição das Variáveis de Elástico
    elasticos = [1.0, 0.62, 0.31]

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.write("PREÇO ATUAL EWZ")
        st.markdown(f'<div class="metric-val" style="color:#00f2ff;">{market["price"]:.2f}</div>', unsafe_allow_html=True)
        st.write(f"Âncora Fixo: {eixo_ewz_manual:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # --- TABELA DE ELÁSTICO ---
        st.markdown('<div class="frame-box" style="border-top: 4px solid #ffcc00;">', unsafe_allow_html=True)
        st.write("GRID DE EXAUSTÃO (ELÁSTICO)")
        
        # CIMA (Resistências do Elástico)
        for pct in elasticos:
            val_up = p_dolfut * (1 + (pct / 100))
            st.markdown(f'<div class="elastic-box up-band">VENDAS (+{pct}%) → {val_up:.2f}</div>', unsafe_allow_html=True)
        
        # CENTRO (Preço Sintético Atual)
        st.markdown(f'<div class="elastic-box center-band">K97 SINTÉTICO → {p_dolfut:.2f}</div>', unsafe_allow_html=True)
        
        # BAIXO (Suportes do Elástico)
        for pct in reversed(elasticos):
            val_down = p_dolfut * (1 - (pct / 100))
            st.markdown(f'<div class="elastic-box down-band">COMPRAS (-{pct}%) → {val_down:.2f}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("Conectando ao EWZ...")

time.sleep(10)
st.rerun()
