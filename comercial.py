import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL ARBITRAGEM", layout="wide")

if 'ref_institucional' not in st.session_state:
    st.session_state.ref_institucional = 0.0
if 'ptax_dia' not in st.session_state:
    st.session_state.ptax_dia = 0.0

# 2. ESTILO CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 650px !important; margin: auto; }
    
    .alerta-container { display: flex; justify-content: center; margin-bottom: 15px; height: 30px; }
    .tag-modern { font-size: 11px; font-weight: bold; letter-spacing: 2px; padding: 6px 30px; border-radius: 2px; }
    .tag-caro { color: #00FF80; border: 1px solid #00FF80; border-left: 5px solid #00FF80; background: rgba(0, 255, 128, 0.05); }
    .tag-barato { color: #FF4B4B; border: 1px solid #FF4B4B; border-left: 5px solid #FF4B4B; background: rgba(255, 75, 75, 0.05); }

    .section-title { font-size: 10px; color: #444; letter-spacing: 3px; margin: 20px 0 10px 0; text-align: center; font-weight: bold; }

    .dual-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 10px; }
    .info-box { background: #080808; padding: 15px; border-radius: 4px; border: 1px solid #111; text-align: center; width: 100%; }
    .pari-val { font-size: 32px; font-weight: 700; color: #FFB900; }
    .equi-val { font-size: 32px; font-weight: 700; color: #00FFFF; }

    .box-container { display: flex; justify-content: space-between; gap: 10px; }
    .box { background: #080808; padding: 15px 5px; border-radius: 4px; width: 33%; text-align: center; border: 1px solid #111; }
    .label { font-size: 9px; color: #555; margin-bottom: 6px; }
    .val { font-size: 20px; font-weight: 700; }
    
    .c-max { color: #00FF80; } 
    .c-min { color: #FF4B4B; } 
    .c-jus { color: #0080FF; }
</style>
""", unsafe_allow_html=True)

# 3. ENTRADAS (ENGRENAGEM)
with st.popover("⚙️"):
    v_ajuste = st.number_input("AJUSTE", value=5.4000, format="%.4f")
    st.session_state.ptax_dia = st.number_input("VALOR PTAX", value=st.session_state.ptax_dia, format="%.4f")
    st.session_state.ref_institucional = st.number_input("REF INSTITUCIONAL", value=st.session_state.ref_institucional, format="%.4f")

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
    
    # CÁLCULO PONTO DE EQUILÍBRIO (PTAX + 22)
    ponto_equilibrio = st.session_state.ptax_dia + 0.0220
    
    # Cálculos das Zonas (+22 e +42)
    f_max, f_jus, f_min = spot + 0.042, spot + 0.030, spot + 0.022
    t_max, t_jus, t_min = st.session_state.ref_institucional + 0.042, st.session_state.ref_institucional + 0.030, st.session_state.ref_institucional + 0.022

    with placeholder.container():
        # ALERTAS DISCRETOS
        st.markdown('<div class="alerta-container">', unsafe_allow_html=True)
        if st.session_state.ref_institucional > 0:
            if spot >= t_max: st.markdown('<div class="tag-modern tag-caro">DOLAR CARO</div>', unsafe_allow_html=True)
            elif spot <= t_min: st.markdown('<div class="tag-modern tag-barato">DOLAR BARATO</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 1. PARIDADE E PONTO DE EQUILÍBRIO
        st.markdown('<div class="dual-container">', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="width:50%;">
                <div class="section-title">PARIDADE</div>
                <div class="info-box"><div class="pari-val">{paridade:.4f}</div></div>
            </div>
            <div style="width:50%;">
                <div class="section-title">PONTO DE EQUILIBRIO</div>
                <div class="info-box"><div class="equi-val">{ponto_equilibrio:.4f}</div></div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. PREÇO JUSTO
        st.markdown('<div class="section-title">PREÇO JUSTO</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="box-container">
            <div class="box"><div class="label">MINIMA</div><div class="val c-min">{f_min:.4f}</div></div>
            <div class="box"><div class="label">JUSTO</div><div class="val c-jus">{f_jus:.4f}</div></div>
            <div class="box"><div class="label">MAXIMA</div><div class="val c-max">{f_max:.4f}</div></div>
        </div>""", unsafe_allow_html=True)

        # 3. PREFERENCIAL INSTITUCIONAL
        if st.session_state.ref_institucional > 0:
            st.markdown('<div class="section-title">PREFERENCIAL INSTITUCIONAL</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="box-container">
                <div class="box"><div class="label">MINIMA</div><div class="val c-min">{t_min:.4f}</div></div>
                <div class="box"><div class="label">JUSTO</div><div class="val c-jus">{t_jus:.4f}</div></div>
                <div class="box"><div class="label">MAXIMA</div><div class="val c-max">{t_max:.4f}</div></div>
            </div>""", unsafe_allow_html=True)

    time.sleep(2)
