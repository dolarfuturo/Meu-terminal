import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import time as dt_time
import time

# Configuração de Layout
st.set_page_config(page_title="K97 - SINTÉTICO HORÁRIO", layout="wide")

# --- MOTOR K97: INVERSÃO E CÁLCULO ---
def calcular_dolfut_k97_inverso(eixo_ewz, preco_ewz_atual, eixo_dol_manual):
    try:
        # Fórmula: (EIXO / PREÇO - 1) * 100 / 2
        var_fator = ((eixo_ewz / preco_ewz_atual) - 1) * 100 / 2
        preco_sintetico = eixo_dol_manual * (1 + (var_fator / 100))
        return preco_sintetico, var_fator
    except:
        return eixo_dol_manual, 0.0

@st.cache_data(ttl=30)
def fetch_ewz_with_filter():
    try:
        t = yf.Ticker("EWZ")
        # Captura dados de 1 minuto para filtrar o horário exato
        df = t.history(period="2d", interval="1m", prepost=True)
        if df.empty: return None
        
        # Converte o índice para o fuso de Brasília (aproximado pelo fechamento de NY)
        df.index = df.index.tz_convert('America/Sao_Paulo')
        
        # Filtro: Segunda a Sexta, entre 11:30 e 18:00
        df_eixo = df.between_time(dt_time(11, 30), dt_time(18, 0))
        
        # Se hoje ainda não chegou às 11:30, usamos o eixo de ontem
        if df_eixo.empty:
            df_eixo = df.between_time(dt_time(11, 30), dt_time(18, 0))

        return {
            "price_now": df['Close'].iloc[-1],
            "eixo_max": df_eixo['High'].max(),
            "eixo_min": df_eixo['Low'].min(),
            "last_update": df.index[-1].strftime('%H:%M:%S')
        }
    except:
        return None

# --- INTERFACE ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black'; font-size: 30px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black'; font-size: 30px; font-weight: 900; }
    .frame-box { border: 2px solid #3d444d; border-top: 4px solid #00f2ff; padding: 20px; background: #0b0e11; border-radius: 4px; }
    .metric-val { font-size: 42px; font-family: 'Arial Black'; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL K97</span></div>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.header("⚙️ AJUSTE")
    eixo_dol_manual = st.number_input("EIXO DOLFUT (S):", value=5295.50, format="%.2f")
    st.caption("Eixo EWZ: Automático (11:30 - 18:00 BRT)")

# PROCESSAMENTO
data = fetch_ewz_with_filter()

if data:
    eixo_ewz_auto = (data["eixo_max"] + data["eixo_min"]) / 2
    p_dolfut, v_desvio = calcular_dolfut_k97_inverso(eixo_ewz_auto, data["price_now"], eixo_dol_manual)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.write("EWZ PREÇO ATUAL")
        st.markdown(f'<div class="metric-val">{data["price_now"]:.2f}</div>', unsafe_allow_html=True)
        st.write(f"Eixo (11:30-18h): **{eixo_ewz_auto:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="frame-box">', unsafe_allow_html=True)
        st.write("DOLFUT SINTÉTICO")
        st.markdown(f'<div class="metric-val">{p_dolfut:.2f}</div>', unsafe_allow_html=True)
        color = "#00ff88" if v_desvio >= 0 else "#ff4d4d"
        st.markdown(f'<div style="color:{color}; font-weight:bold;">Ajuste: {v_desvio:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.caption(f"Última atualização: {data['last_update']} | Dados filtrados Seg-Sex")

time.sleep(10)
st.rerun()
