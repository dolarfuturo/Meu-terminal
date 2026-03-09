import streamlit as st
import yfinance as yf
import time

# Configuração de Layout para Tablet
st.set_page_config(page_title="K97 - TERMINAL", layout="wide")

# --- MOTOR DE CÁLCULO K97 ---
def calcular_dolfut_k97(eixo_ewz_ontem, preco_ewz_atual, eixo_dolfut_manual):
    try:
        # (EIXO ONTEM / PREÇO AGORA - 1) * 100 / 2
        var_ewz = ((eixo_ewz_ontem / preco_ewz_atual) - 1) * 100 / 2
        preco_sintetico = eixo_dolfut_manual * (1 + (var_ewz / 100))
        return preco_sintetico, var_ewz
    except:
        return eixo_dolfut_manual, 0.0

# --- CAPTURA DE DADOS (EWZ) ---
@st.cache_data(ttl=5)
def fetch_ewz_data():
    try:
        t = yf.Ticker("EWZ")
        # Buscamos 2 dias para ter o histórico de ontem e o pre-market de hoje
        df = t.history(period="2d", interval="1m", prepost=True)
        
        if not df.empty:
            # Identifica os dias presentes no dataframe
            dias = df.index.normalize().unique()
            
            # Dados de Ontem (Dia anterior ao último disponível)
            df_ontem = df[df.index.normalize() == dias[0]]
            eixo_ontem = (df_ontem['High'].max() + df_ontem['Low'].min()) / 2
            
            # Preço de Agora (Último tick do Pre-market ou Regular)
            preco_atual = df['Close'].iloc[-1]
            
            return {
                "price": preco_atual,
                "eixo_ontem": eixo_ontem,
                "max_ontem": df_ontem['High'].max(),
                "min_ontem": df_ontem['Low'].min()
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
    .metric-val { font-size: 44px; font-family: 'Arial Black'; font-weight: 900; color: #ffffff; }
    .metric-label { font-size: 14px; color: #00f2ff; font-weight: bold; }
    .eixo-destaque { border: 2px dashed #ffcc00; color: #ffcc00; text-align: center; padding: 15px; font-size: 26px; font-weight: 900; margin-top: 20px; }
    .elastic-row { display: flex; justify-content: space-between; padding: 5px 10px; border-bottom: 1px solid #1e2226; font-family: 'monospace'; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL K97</span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ AJUSTE MANUAL")
    eixo_dol_input = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")

market = fetch_ewz_data()

if market:
    # Agora o cálculo usa o Eixo de Ontem
    p_dolfut, v_desvio = calcular_dolfut_k97(market["eixo_ontem"], market["price"], eixo_dol_input)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">EWZ (PREÇO AGORA)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val">{market["price"]:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #848e9c; font-size: 16px;">Eixo Fixado (Ontem): {market["eixo_ontem"]:.2f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">DOLFUT SINTÉTICO (K97)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val">{p_dolfut:.2f}</div>', unsafe_allow_html=True)
        color = "#00ff88" if v_desvio >= 0 else "#ff4d4d"
        st.markdown(f'<div style="color: {color}; font-weight:bold; font-size: 20px;">Desvio: {v_desvio:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- GRID DE VARIÁVEIS ---
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

    st.markdown(f'<div class="eixo-destaque">EIXO DÓLAR ANCORADO: {eixo_dol_input:.2f}</div>', unsafe_allow_html=True)

else:
    st.error("Buscando dados históricos do EWZ...")

time.sleep(5)
st.rerun()
