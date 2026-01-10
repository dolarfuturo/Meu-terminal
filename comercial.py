import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO INICIAL
st.set_page_config(page_title="TERMINAL ARBITRAGEM", layout="wide")

if 'ref_institucional' not in st.session_state:
    st.session_state.ref_institucional = 0.0
if 'ptax_dia' not in st.session_state:
    st.session_state.ptax_dia = 0.0

# 2. ESTILO VISUAL (TÍTULOS EM BRANCO E NITIDEZ MÁXIMA)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 700px !important; margin: auto; }
    
    /* ALERTAS */
    .alerta-container { display: flex; justify-content: center; margin-bottom: 15px; height: 35px; }
    .tag-modern { font-size: 12px; font-weight: bold; letter-spacing: 2px; padding: 6px 30px; border-radius: 2px; }
    .tag-caro { color: #00FF80; border: 1px solid #00FF80; border-left: 5px solid #00FF80; background: rgba(0, 255, 128, 0.1); }
    .tag-barato { color: #FF4B4B; border: 1px solid #FF4B4B; border-left: 5px solid #FF4B4B; background: rgba(255, 75, 75, 0.1); }

    /* TÍTULOS BRANCO PURO */
    .section-title { font-size: 11px; color: #FFFFFF !important; letter-spacing: 3px; margin: 25px 0 10px 0; text-align: center; font-weight: bold; }

    /* LINHA SUPERIOR LADO A LADO */
    .dual-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 5px; }
    .info-box { background: #080808; padding: 20px 5px; border-radius: 4px; border: 1px solid #222; text-align: center; width: 100%; }
    .pari-val { font-size: 36px; font-weight: 700; color: #FFB900; }
    .equi-val { font-size: 36px; font-weight: 700; color: #00FFFF; }

    /* BOXES DE REFERÊNCIA */
    .box-container { display: flex; justify-content: space-between; gap: 10px; }
    .box { background: #080808; padding: 18px 5px; border-radius: 4px; width: 33%; text-align: center; border: 1px solid #1A1A1A; }
    .label { font-size: 10px; color: #777; margin-bottom: 8px; font-weight: bold; }
    .val { font-size: 22px; font-weight: 700; }
    
    .c-max { color: #00FF80; } /* VERDE */
    .c-min { color: #FF4B4B; } /* VERMELHO */
    .c-jus { color: #0080FF; } /* AZUL */
</style>
""", unsafe_allow_html=True)

# 3. PAINEL DE CONTROLE (ENGRENAGEM)
with st.popover("⚙️ CONFIGURAÇÕES"):
    v_ajuste = st.number_input("AJUSTE ANTERIOR", value=5.4000, format="%.4f")
    st.session_state.ptax_dia = st.number_input("DIGITE A PTAX", value=st.session_state.ptax_dia, format="%.4f")
    st.session_state.ref_institucional = st.number_input("REFERENCIAL 10H", value=st.session_state.ref_institucional, format="%.4f")

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
    
    # LÓGICA VARIÁVEL: PTAX + 22 PONTOS
    ponto_equilibrio = st.session_state.ptax_dia + 0.0220
    
    # CÁLCULOS DAS ZONAS (ATUALIZADO JUSTO PARA +31)
    f_max, f_jus, f_min = spot + 0.042, spot + 0.031, spot + 0.022
    t_max, t_jus, t_min = st.session_state.ref_institucional + 0.042, st.session_state.ref_institucional + 0.031, st.session_state.ref_institucional + 0.022

    with placeholder.container():
        # ALERTA
        st.markdown('<div class="alerta-container">', unsafe_allow_html=True)
        if st.session_state.ref_institucional > 0:
            if spot >= t_max: st.markdown('<div class="tag-modern tag-caro">DOLAR CARO</div>', unsafe_allow_html=True)
            elif spot <= t_min: st.markdown('<div class="tag-modern tag-barato">DOLAR BARATO</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # PARIDADE E EQUILÍBRIO (LADO A LADO)
        st.markdown(f"""
        <div class="dual-container">
            <div style="width:48%;">
                <div class="section-title">PARIDADE</div>
                <div class="info-box"><div class="pari-val">{paridade:.4f}</div></div>
            </div>
            <div style="width:48%;">
                <div class="section-title">PONTO DE EQUILIBRIO</div>
                <div class="info-box"><div class="equi-val">{ponto_equilibrio:.4f}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PREÇO JUSTO
        st.markdown('<div class="section-title">PREÇO JUSTO</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="box-container">
            <div class="box"><div class="label">MINIMA</div><div class="val c-min">{f_min:.4f}</div></div>
            <div class="box"><div class="label">JUSTO</div><div class="val c-jus">{f_jus:.4f}</div></div>
            <div class="box"><div class="label">MAXIMA</div><div class="val c-max">{f_max:.4f}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # PREFERENCIAL INSTITUCIONAL
        if st.session_state.ref_institucional > 0:
            st.markdown('<div class="section-title">PREFERENCIAL INSTITUCIONAL</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="box-container">
                <div class="box"><div class="label">MINIMA</div><div class="val c-min">{t_min:.4f}</div></div>
                <div class="box"><div class="label">JUSTO</div><div class="val c-jus">{t_jus:.4f}</div></div>
                <div class="box"><div class="label">MAXIMA</div><div class="val c-max">{t_max:.4f}</div></div>
            </div>
            """, unsafe_allow_html=True)

    time.sleep(2)
