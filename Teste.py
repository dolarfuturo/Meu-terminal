import streamlit as st
import yfinance as yf
import time

# Configuração de Layout para Tablet
st.set_page_config(page_title="K97 - SINTÉTICO AUTO", layout="wide")

# --- MOTOR K97: INVERSÃO E CÁLCULO ---
def calcular_dolfut_k97_inverso(eixo_ewz, preco_ewz_atual, eixo_dol_manual):
    try:
        # Sua lógica exata: (EIXO / PREÇO - 1) * 100 / 2
        # Se Eixo(36,56) > Preço(36,30) -> Resultado positivo (Dólar sobe)
        var_fator = ((eixo_ewz / preco_ewz_atual) - 1) * 100 / 2
        
        # DOLFUT = eixo do dol manual * (1 + variação/100)
        preco_sintetico = eixo_dol_manual * (1 + (var_fator / 100))
        
        return preco_sintetico, var_fator
    except:
        return eixo_dol_manual, 0.0

@st.cache_data(ttl=10)
def fetch_ewz_full():
    try:
        t = yf.Ticker("EWZ")
        # Captura Pre-market e Regular (desde 06h BRT)
        df = t.history(period="1d", interval="1m", prepost=True)
        if not df.empty:
            return {
                "price": df['Close'].iloc[-1],
                "max": df['High'].max(),
                "min": df['Low'].min()
            }
    except:
        return None

# --- ESTILIZAÇÃO TERMINAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black'; font-size: 30px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black'; font-size: 30px; font-weight: 900; }
    .frame-box { border: 2px solid #3d444d; border-top: 4px solid #00f2ff; padding: 20px; background: #0b0e11; border-radius: 4px; }
    .metric-val { font-size: 42px; font-family: 'Arial Black'; font-weight: 900; }
    .label-k97 { color: #00f2ff; font-weight: bold; margin-bottom: 5px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL K97</span></div>', unsafe_allow_html=True)

# SIDEBAR - APENAS O DOLFUT É MANUAL
with st.sidebar:
    st.header("⚙️ CONFIGURAÇÃO")
    eixo_dol_manual = st.number_input("EIXO DOLFUT (S):", value=5295.50, format="%.2f")
    st.write("---")
    st.info("O Eixo do EWZ é calculado automaticamente com base na Máxima e Mínima do dia atual.")

# EXECUÇÃO DO MOTOR
market = fetch_ewz_full()

if market:
    # Eixo EWZ Automático: (Max + Min) / 2
    eixo_ewz_auto = (market["max"] + market["min"]) / 2
    
    # Cálculo do Sintético com Inversão
    p_dolfut, v_desvio = calcular_dolfut_k97_inverso(eixo_ewz_auto, market["price"], eixo_dol_manual)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown('<div class="label-k97">EWZ (ATUAL)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val">{market["price"]:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#848e9c;">Eixo Auto: {eixo_ewz_auto:.2f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown('<div class="label-k97">DOLFUT SINTÉTICO (K97)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val" style="color:#ffffff;">{p_dolfut:.2f}</div>', unsafe_allow_html=True)
        color = "#00ff88" if v_desvio >= 0 else "#ff4d4d"
        st.markdown(f'<div style="color:{color}; font-weight:bold;">Ajuste Inverso: {v_desvio:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Destaque do Eixo Manual
    st.markdown(f'<div style="text-align:center; border: 2px dashed #00f2ff; padding:15px; color:#ffcc00; font-size:20px; font-weight:bold; margin-top:20px;">EIXO DÓLAR: {eixo_dol_manual:.2f}</div>', unsafe_allow_html=True)

else:
    st.warning("Conectando aos servidores de dados...")

time.sleep(10)
st.rerun()
