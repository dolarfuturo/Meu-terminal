import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# Configuração de Layout para Tablet
st.set_page_config(page_title="K97 - TERMINAL", layout="wide")

# --- MOTOR DE CÁLCULO K97 ---
def calcular_dolfut_k97(eixo_ewz, preco_ewz_atual, eixo_dolfut_manual):
    try:
        # Variação baseada no Eixo Fixo vs Preço Vivo
        var_ewz = ((eixo_ewz / preco_ewz_atual) - 1) * 100 / 2
        preco_sintetico = eixo_dolfut_manual * (1 + (var_ewz / 100))
        return preco_sintetico, var_ewz
    except:
        return eixo_dolfut_manual, 0.0

# --- CAPTURA DE DADOS (EIXO FIXO VS PREÇO PRE-MARKET) ---
@st.cache_data(ttl=5)
def fetch_terminal_data():
    try:
        t = yf.Ticker("EWZ")
        # Puxamos 5 dias para garantir que a Sexta esteja no histórico
        df = t.history(period="5d", interval="1m", prepost=True)
        
        if not df.empty:
            dias_uteis = df[df['Volume'] > 0].index.normalize().unique()
            
            # 1. DEFINIÇÃO DO EIXO FIXO (Último Pregão: 11:30 às 18:00)
            # dias_uteis[-1] é hoje, dias_uteis[-2] é o último fechado (Sexta 06/03)
            dia_eixo = dias_uteis[-2]
            df_eixo = df[df.index.normalize() == dia_eixo]
            df_regular = df_eixo.between_time('11:30', '18:00')
            
            # Cálculo do Eixo que ficará fixo o dia todo
            eixo_fixo = (df_regular['High'].max() + df_regular['Low'].min()) / 2
            
            # 2. PREÇO DINÂMICO (Desde a abertura do Pre-market às 06:00)
            preco_vivo = df['Close'].iloc[-1]
            
            return {
                "price": preco_vivo,
                "eixo": eixo_fixo,
                "data_eixo": dia_eixo.strftime('%d/%m')
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
    .eixo-destaque { border: 2px dashed #00f2ff; color: #ffcc00; text-align: center; padding: 15px; font-size: 26px; font-weight: 900; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL K97</span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ AJUSTE MANUAL")
    eixo_dol_input = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")

data = fetch_terminal_data()

if data:
    p_dolfut, v_desvio = calcular_dolfut_k97(data["eixo"], data["price"], eixo_dol_input)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">EWZ (PREÇO VIVO - PRE-MARKET)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val">{data["price"]:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #848e9c; font-size: 16px;">Eixo Fixo ({data["data_eixo"]}): {data["eixo"]:.2f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">DOLFUT SINTÉTICO (K97)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val">{p_dolfut:.2f}</div>', unsafe_allow_html=True)
        color = "#00ff88" if v_desvio >= 0 else "#ff4d4d"
        st.markdown(f'<div style="color: {color}; font-weight:bold; font-size: 20px;">Desvio: {v_desvio:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-destaque">EIXO DÓLAR ANCORADO: {eixo_dol_input:.2f}</div>', unsafe_allow_html=True)
else:
    st.error("Aguardando dados do mercado (Abertura Pre-market 06:00)...")

time.sleep(5)
st.rerun()
