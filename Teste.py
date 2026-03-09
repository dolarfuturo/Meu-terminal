import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - SOMENTE EWZ", layout="wide")

# --- MOTOR K97: LÓGICA X ---
def calcular_k97_ewz_only(eixo_fixo, x_media_atual, eixo_dol_manual):
    try:
        # Cálculo do desvio: (Eixo Fixo / X - 1) * 100 / 2
        # Inversão: Se X subir, o desvio fica negativo (Dólar cai)
        desvio_perc = ((eixo_fixo / x_media_atual) - 1) * 100 / 2
        
        # Preço Sintético do Dólar
        preco_sintetico = eixo_dol_manual * (1 + (desvio_perc / 100))
        
        return preco_sintetico, desvio_perc
    except:
        return eixo_dol_manual, 0.0

@st.cache_data(ttl=10)
def fetch_ewz_core():
    try:
        t = yf.Ticker("EWZ")
        # Dados de 1 dia com pre-market (início 06h BRT)
        df = t.history(period="1d", interval="1m", prepost=True)
        if not df.empty:
            return {
                "max": df['High'].max(),
                "min": df['Low'].min()
            }
    except:
        return None

# --- ESTILO LIMPO ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .terminal-title { color: #00f2ff; font-family: 'Arial Black'; font-size: 28px; font-weight: 900; }
    .box-ewz { border: 2px solid #3d444d; border-top: 4px solid #ffcc00; padding: 20px; border-radius: 4px; }
    .val-display { font-size: 50px; font-family: 'Arial Black'; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="terminal-title">BAIR - TERMINAL K97 (EWZ ONLY)</div>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.header("⚙️ AJUSTE")
    eixo_dol_manual = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")
    eixo_fixo_ewz = st.number_input("EIXO FIXO EWZ:", value=36.56, format="%.2f")

# EXECUÇÃO
market = fetch_ewz_core()

if market:
    # Valor X = Média do dia no EWZ
    x_media = (market["max"] + market["min"]) / 2
    
    # Cálculo Final
    p_sintetico, desvio = calcular_k97_ewz_only(eixo_fixo_ewz, x_media, eixo_dol_manual)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="box-ewz">', unsafe_allow_html=True)
        st.write("VALOR X (MÉDIA EWZ)")
        st.markdown(f'<div class="val-display" style="color:#ffcc00;">{x_media:.2f}</div>', unsafe_allow_html=True)
        st.write(f"Máxima: {market['max']:.2f} | Mínima: {market['min']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="box-ewz">', unsafe_allow_html=True)
        st.write("DOLFUT SINTÉTICO")
        st.markdown(f'<div class="val-display">{p_sintetico:.2f}</div>', unsafe_allow_html=True)
        color = "#00ff88" if desvio >= 0 else "#ff4d4d"
        st.markdown(f'<div style="color:{color}; font-weight:bold; font-size:22px;">Ajuste: {desvio:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="text-align:center; margin-top:40px; color:#848e9c;">REFERÊNCIA EWZ: {eixo_fixo_ewz:.2f}</div>', unsafe_allow_html=True)

time.sleep(10)
st.rerun()
