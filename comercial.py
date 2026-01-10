import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL ARBITRAGEM", layout="wide")

if 'ref_institucional' not in st.session_state:
    st.session_state.ref_institucional = 0.0

# 2. ESTILO CSS PREMIUM
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 600px !important; margin: auto; }
    
    /* ALERTA DISCRETO */
    .alerta-container { display: flex; justify-content: center; margin-bottom: 20px; height: 30px; }
    .tag { font-size: 12px; font-weight: bold; letter-spacing: 3px; padding: 5px 20px; border-radius: 4px; }
    .tag-caro { color: #FF4B4B; border: 1px solid #FF4B4B; background: rgba(255, 75, 75, 0.1); }
    .tag-barato { color: #00FF80; border: 1px solid #00FF80; background: rgba(0, 255, 128, 0.1); }

    .section-title { font-size: 11px; color: #444; letter-spacing: 3px; margin: 25px 0 10px 0; text-align: center; font-weight: bold; border-bottom: 1px solid #111; padding-bottom: 5px; }

    /* PARIDADE */
    .pari-val { font-size: 54px; font-weight: 700; color: #FFB900; text-align: center; margin-bottom: 5px; }

    /* CAIXAS */
    .box-container { display: flex; justify-content: space-between; gap: 10px; }
    .box { background: #050505; padding: 15px 5px; border-radius: 4px; width: 33%; text-align: center; border: 1px solid #111; }
    .label { font-size: 9px; color: #555; margin-bottom: 6px; font-weight: bold; }
    .val { font-size: 21px; font-weight: 700; }
    
    .c-max { color: #FF4B4B; }
    .c-jus { color: #0080FF; }
    .c-min { color: #00FF80; }
</style>
""", unsafe_allow_html=True)

# 3. ENTRADAS (OCULTAS NO POP OVER)
with st.popover("⚙️"):
    v_ajuste = st.number_input("AJUSTE", value=5.4000, format="%.4f")
    st.session_state.ref_institucional = st.number_input("VALOR REFERÊNCIA", value=st.session_state.ref_institucional, format="%.4f")

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
    
    # Cálculos das Zonas
    f_max, f_jus, f_min = spot + 0.042, spot + 0.030, spot - 0.022
    t_max, t_jus, t_min = st.session_state.ref_institucional + 0.042, st.session_state.ref_institucional + 0.030, st.session_state.ref_institucional - 0.022

    with placeholder.container():
        # TAG DE ALERTA
        st.markdown('<div class="alerta-container">', unsafe_allow_html=True)
        if st.session_state.ref_institucional > 0:
            if spot >= t_max: st.markdown('<div class="tag tag-caro">CARO</div>', unsafe_allow_html=True)
            elif spot <= t_min: st.markdown('<div class="tag tag-barato">BARATO</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 1. PARIDADE
        st.markdown('<div class="section-title">PARIDADE</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="pari-val">{paridade:.4f}</div>', unsafe_allow_html=True)

        # 2. PREÇO JUSTO
        st.markdown('<div class="section-title">PREÇO JUSTO</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="box-container">
            <div class="box"><div class="label">MÍNIMA</div><div class="val c-min">{f_min:.4f}</div></div>
            <div class="box"><div class="label">JUSTO</div><div class="val c-jus">{f_jus:.4f}</div></div>
            <div class="box"><div class="label">MÁXIMA</div><div class="val c-max">{f_max:.4f}</div></div>
        </div>""", unsafe_allow_html=True)

        # 3. PREFERENCIAL INSTITUCIONAL
        if st.session_state.ref_institucional > 0:
            st.markdown('<div class="section-title">PREFERENCIAL INSTITUCIONAL</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="box-container">
                <div class="box"><div class="label">MÍNIMA</div><div class="val c-min">{t_min:.4f}</div></div>
                <div class="box"><div class="label">JUSTO</div><div class="val c-jus">{t_jus:.4f}</div></div>
                <div class="box"><div class="label">MÁXIMA</div><div class="val c-max">{t_max:.4f}</div></div>
            </div>""", unsafe_allow_html=True)

    time.sleep(2)
