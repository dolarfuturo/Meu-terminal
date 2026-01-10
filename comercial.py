import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

if 'ref_base' not in st.session_state:
    st.session_state.ref_base = 0.0

# 2. ESTILO TERMINAL PROFISSIONAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 0.5rem !important; max-width: 800px !important; margin: auto; }
    
    .terminal-header { 
        text-align: center; font-size: 14px; letter-spacing: 8px; color: #555; 
        border-bottom: 1px solid #222; padding-bottom: 10px; margin-bottom: 20px;
    }
    .terminal-title { color: #FFFFFF; font-weight: 700; }

    .alerta-wrap { display: flex; justify-content: center; height: 30px; margin-bottom: 15px; }
    .status-tag { font-size: 12px; font-weight: bold; letter-spacing: 2px; padding: 4px 20px; border: 1px solid #333; }
    .caro { color: #00FF80; border-color: #00FF80; }
    .barato { color: #FF4B4B; border-color: #FF4B4B; }

    .data-row { 
        display: flex; justify-content: space-between; align-items: center; 
        padding: 15px 0; border-bottom: 1px solid #111;
    }
    .data-label { font-size: 11px; color: #FFFFFF; font-weight: 700; letter-spacing: 2px; width: 30%; }
    .data-value { font-size: 28px; font-weight: 700; width: 70%; text-align: right; }
    
    .sub-grid { display: flex; gap: 20px; justify-content: flex-end; width: 70%; }
    .sub-item { text-align: right; }
    .sub-label { font-size: 9px; color: #444; display: block; margin-bottom: 2px; }
    .sub-val { font-size: 20px; font-weight: 700; }

    .c-pari { color: #FFB900; }
    .c-equi { color: #00FFFF; }
    .c-max { color: #00FF80; } 
    .c-min { color: #FF4B4B; } 
    .c-jus { color: #0080FF; }
</style>
""", unsafe_allow_html=True)

# Função de arredondamento para meio ponto (tick size 0.5)
def round_half(number):
    return round(number * 200) / 200

# 3. CONTROLES
with st.popover("⚙️"):
    v_ajuste = st.number_input("AJUSTE", value=5.4000, format="%.4f")
    st.session_state.ref_base = st.number_input("REFERENCIAL", value=st.session_state.ref_base, format="%.4f")

def get_data():
    try:
        d_ticker = yf.Ticker("DX-Y.NYB")
        e_ticker = yf.Ticker("EWZ")
        s_df = yf.download("BRL=X", period="1d", interval="1m", progress=False)
        s_at = float(s_df['Close'].iloc[-1])
        d_df = yf.download("DX-Y.NYB", period="2d", interval="1m", progress=False, prepost=True)
        e_df = yf.download("EWZ", period="2d", interval="1m", progress=False, prepost=True)
        d_prev = float(d_ticker.fast_info.previous_close)
        e_prev = float(e_ticker.fast_info.previous_close)
        d_at = float(d_df['Close'].iloc[-1])
        e_at = float(e_df['Close'].iloc[-1])
        return s_at, ((d_at - d_prev) / d_prev * 100) - ((e_at - e_prev) / e_prev * 100)
    except: return 0.0, 0.0

placeholder = st.empty()

while True:
    spot, spread = get_data()
    paridade = v_ajuste * (1 + (spread/100))
    ponto_equilibrio = st.session_state.ref_base + 0.0220
    
    # Cálculos Justo (+31) com arredondamento de meio ponto
    f_max = round_half(spot + 0.042)
    f_jus = round_half(spot + 0.031)
    f_min = round_half(spot + 0.022)
    
    t_max = round_half(st.session_state.ref_base + 0.042)
    t_jus = round_half(st.session_state.ref_base + 0.031)
    t_min = round_half(st.session_state.ref_base + 0.022)

    with placeholder.container():
        st.markdown('<div class="terminal-header">TERMINAL <span class="terminal-title">DOLAR</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="alerta-wrap">', unsafe_allow_html=True)
        if st.session_state.ref_base > 0:
            if spot >= t_max: st.markdown('<div class="status-tag caro">DOLAR CARO</div>', unsafe_allow_html=True)
            elif spot <= t_min: st.markdown('<div class="status-tag barato">DOLAR BARATO</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # PARIDADE (Preço cheio)
        st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE</div><div class="data-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=True)
        
        # PONTO DE EQUILÍBRIO (Preço cheio)
        st.markdown(f'<div class="data-row"><div class="data-label">PONTO DE EQUILIBRIO</div><div class="data-value c-equi">{ponto_equilibrio:.4f}</div></div>', unsafe_allow_html=True)

        # PREÇO JUSTO (Arredondado 0.5)
        st.markdown(f"""
        <div class="data-row">
            <div class="data-label">PREÇO JUSTO</div>
            <div class="sub-grid">
                <div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{f_min:.4f}</span></div>
                <div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{f_jus:.4f}</span></div>
                <div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{f_max:.4f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PREFERENCIAL INSTITUCIONAL (Arredondado 0.5)
        if st.session_state.ref_base > 0:
            st.markdown(f"""
            <div class="data-row">
                <div class="data-label">PREFERENCIAL INSTITUCIONAL</div>
                <div class="sub-grid">
                    <div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{t_min:.4f}</span></div>
                    <div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{t_jus:.4f}</span></div>
                    <div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{t_max:.4f}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    time.sleep(2)
