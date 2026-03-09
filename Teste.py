import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - EIXO X", layout="wide")

# --- MOTOR DE CÁLCULO K97 (ESTRATÉGIA EWZ) ---
def calcular_k97_x(eixo_fixo_ewz, x_media, eixo_dol_manual):
    try:
        # 1. Cálculo do Desvio Percentual: (Eixo / X - 1) * 100 / 2
        # A inversão ocorre aqui: Se X > Eixo, o desvio fica negativo.
        desvio_perc = ((eixo_fixo_ewz / x_media) - 1) * 100 / 2
        
        # 2. Cálculo do DOLFUT: Eixo Dólar * Desvio Percentual
        # (Ajustado para aplicação direta sobre a ancoragem)
        preco_sintetico = eixo_dol_manual * (1 + (desvio_perc / 100))
        
        return preco_sintetico, desvio_perc
    except:
        return eixo_dol_manual, 0.0

@st.cache_data(ttl=10)
def fetch_ewz_core():
    try:
        t = yf.Ticker("EWZ")
        # Captura desde a abertura do Pre-market (06:00 BRT)
        df = t.history(period="1d", interval="1m", prepost=True)
        if not df.empty:
            return {
                "max": df['High'].max(),
                "min": df['Low'].min()
            }
    except:
        return None

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .box-terminal { border: 2px solid #3d444d; border-top: 4px solid #00f2ff; padding: 25px; background: #0b0e11; border-radius: 4px; }
    .display-val { font-size: 52px; font-family: 'Arial Black'; font-weight: 900; color: #ffffff; }
    .label-terminal { color: #ffcc00; font-weight: bold; font-size: 16px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 style="color:#00f2ff; font-family:Arial Black;">BAIR - TERMINAL K97</h1>', unsafe_allow_html=True)

# SIDEBAR: PARÂMETROS MANUAIS
with st.sidebar:
    st.header("⚙️ CONFIGURAÇÃO")
    eixo_dol_manual = st.number_input("EIXO DÓLAR (MANUAL):", value=5295.50, format="%.2f")
    eixo_fixo_ewz = st.number_input("EIXO FIXO EWZ:", value=36.56, format="%.2f")

# EXECUÇÃO DA LÓGICA
market = fetch_ewz_core()

if market:
    # 1. Max + min / 2 = X
    x_val = (market["max"] + market["min"]) / 2
    
    # 2. Executa a Fórmula de Desvio e Dólar Sintético
    dolfut_calc, desvio_calc = calcular_k97_x(eixo_fixo_ewz, x_val, eixo_dol_manual)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="box-terminal">', unsafe_allow_html=True)
        st.markdown('<div class="label-terminal">VALOR X (MÉDIA EWZ)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="display-val" style="color:#ffcc00;">{x_val:.2f}</div>', unsafe_allow_html=True)
        st.write(f"Máx: {market['max']:.2f} | Mín: {market['min']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="box-terminal">', unsafe_allow_html=True)
        st.markdown('<div class="label-terminal">DOLFUT SINTÉTICO</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="display-val">{dolfut_calc:.2f}</div>', unsafe_allow_html=True)
        color = "#00ff88" if desvio_calc >= 0 else "#ff4d4d"
        st.markdown(f'<div style="color:{color}; font-weight:bold; font-size:22px;">Desvio DOL: {desvio_calc:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("Conectando aos dados do EWZ...")

time.sleep(10)
st.rerun()
