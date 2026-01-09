import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL PROFISSIONAL", layout="wide")

# 2. Memória da Sessão
if 'history' not in st.session_state: st.session_state.history = []
if 'spot_ref_locked' not in st.session_state: st.session_state.spot_ref_locked = None

# 3. CSS Terminal Profissional (Fontes Quadradas e Layout Compacto)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Roboto Mono', monospace; }
    
    /* Linha de Ativo Estilo Ticker */
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        border-bottom: 1px solid #222;
        background-color: #050505;
    }
    
    .ticker-name { font-size: 14px; font-weight: bold; color: #888; width: 150px; }
    .ticker-price { font-size: 22px; font-weight: bold; color: #FFB900; width: 150px; text-align: right; }
    .ticker-var { font-size: 16px; width: 100px; text-align: right; }
    
    /* FRP ao lado */
    .frp-label { font-size: 10px; color: #666; text-transform: uppercase; }
    .frp-value { font-size: 16px; font-weight: bold; margin-right: 20px; }
    
    .positive { color: #00FF00; }
    .negative { color: #FF4B4B; }
    
    /* Alvo Highlight */
    .alvo-box {
        background-color: #111;
        border-left: 5px solid #FFB900;
        padding: 15px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Sidebar Inputs
with st.sidebar:
    st.header("CONFIG")
    val_ajuste_manual = st.number_input("Ajuste DOL (Manual)", value=5.3900, format="%.4f")
    st.divider()
    v_min = st.number_input("Pts Mín", value=22.0)
    v_justo = st.number_input("Pts Justo", value=31.0)
    v_max = st.number_input("Pts Máx", value=42.0)
    if st.button("Reset Trava 16h"): st.session_state.spot_ref_locked = None

def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 5. Lógica e Renderização
placeholder = st.empty()
with placeholder.container():
    spot_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    now_br = datetime.now() - timedelta(hours=3)
    is_pre_market = now_br.time() < datetime.strptime("11:30", "%H:%M").time()

    if not spot_df.empty:
        spot_at = float(spot_df['Close'].iloc[-1])
        
        # Trava Automática 16h
        try:
            lock_data = spot_df.between_time('15:58', '16:02')
            if not lock_data.empty and st.session_state.spot_ref_locked is None:
                st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
        except: pass
        
        ref_16h = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

        # Cálculo Spread e Alvo
        v_dxy = 0.0
        if not dxy_df.empty:
            v_dxy = ((d_at := float(dxy_df['Close'].iloc[-1])) - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0]) * 100
        
        v_ewz = 0.0
        if not ewz_df.empty:
            ewz_at = float(ewz_df['Close'].iloc[-1])
            ref_ewz = float(ewz_df['Close'].iloc[0]) if is_pre_market else float(ewz_df['Open'].iloc[0])
            v_ewz = ((ewz_at - ref_ewz) / ref_ewz) * 100

        spread = v_dxy - v_ewz
        preco_alvo = val_ajuste_manual * (1 + (spread / 100))

        # --- LAYOUT TERMINAL ---
        
        # 1. Bloco de Preço Alvo (Topo)
        st.markdown(f"""
            <div class="alvo-box">
                <div style="font-size:12px; color:#888;">PREÇO ALVO PELO SPREAD (AJUSTE MANUAL + SPREAD)</div>
                <div style="font-size:32px; font-weight:bold; color:#FFB900;">{preco_alvo:.4f} <span style="font-size:16px; color:#666;">Spread: {spread:+.2f}%</span></div>
            </div>
        """, unsafe_allow_html=True)

        # 2. Tabela de Ativos Estilo Ticker
        # SPOT
        v_spot_ajuste = ((spot_at - val_ajuste_manual) / val_ajuste_manual) * 100
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">USD/BRL SPOT</div>
                <div class="ticker-price">{spot_at:.4f}</div>
                <div class="ticker-var {'positive' if v_spot_ajuste >= 0 else 'negative'}">{v_spot_ajuste:+.2f}%</div>
                <div style="display:flex;">
                    <div style="margin-right:20px;"><span class="frp-label">MÍN</span><br><span class="frp-value" style="color:#FF4B4B;">{spot_at + (v_min/1000):.4f}</span></div>
                    <div style="margin-right:20px;"><span class="frp-label">JUSTO</span><br><span class="frp-value" style="color:#0080FF;">{spot_at + (v_justo/1000):.4f}</span></div>
                    <div><span class="frp-label">MÁX</span><br><span class="frp-value" style="color:#00FF00;">{spot_at + (v_max/1000):.4f}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
