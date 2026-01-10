import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL ARBITRAGEM PRO", layout="wide")

if 'spot_10h' not in st.session_state:
    st.session_state.spot_10h = 0.0

# 2. ESTILO CSS (CORRIGIDO)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 500px !important; margin: auto; }
    
    .section-title { font-size: 12px; color: #555; border-bottom: 1px solid #222; padding-bottom: 5px; margin: 15px 0 10px 0; letter-spacing: 1px; }
    
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .alerta-max { background: #FF0000; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; animation: blink 0.8s infinite; margin-bottom: 10px; }
    .alerta-min { background: #00FF00; color: black; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; animation: blink 0.8s infinite; margin-bottom: 10px; }
    
    .spot-box { text-align: center; padding: 15px; border: 1px solid #333; border-radius: 8px; margin-bottom: 20px; background: #080808; }
    .box-container { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 10px; }
    .box { background: #111; padding: 12px 5px; border-radius: 4px; width: 33%; text-align: center; border: 1px solid #222; }
    .label { font-size: 9px; color: #666; margin-bottom: 4px; }
    .val { font-size: 16px; font-weight: bold; }
    
    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .ora { color: #FFB900 !important; }
</style>
""", unsafe_allow_html=True)

# 3. INTERFACE DE ENTRADA
with st.popover("⚙️ AJUSTAR REFERÊNCIAS"):
    v_ajuste = st.number_input("AJUSTE ANTERIOR", value=5.4000, format="%.4f")
    st.session_state.spot_10h = st.number_input("SPOT DAS 10H", value=st.session_state.spot_10h, format="%.4f")

def get_data():
    try:
        s_df = yf.download("BRL=X", period="1d", interval="1m", progress=False)
        d_df = yf.download("DX-Y.NYB", period="1d", interval="1m", progress=False)
        e_df = yf.download("EWZ", period="1d", interval="1m", progress=False, prepost=True)
        s_at = float(s_df['Close'].iloc[-1])
        d_prev = float(yf.Ticker("DX-Y.NYB").fast_info.previous_close)
        e_prev = float(yf.Ticker("EWZ").fast_info.previous_close)
        d_v = ((float(d_df['Close'].iloc[-1]) - d_prev) / d_prev * 100)
        e_v = ((float(e_df['Close'].iloc[-1]) - e_prev) / e_prev * 100)
        return s_at, (d_v - e_v)
    except: return 0.0, 0.0

placeholder = st.empty()

while True:
    spot, spread = get_data()
    paridade = v_ajuste * (1 + (spread/100))
    
    # 4. CÁLCULOS SOLICITADOS
    # FLUTUANTES (BASE SPOT ATUAL)
    f_max = spot + 0.042
    f_jus = spot + 0.030
    f_min = spot - 0.022 # Note: ajuste para ser abaixo do spot (mínima)
    
    # TRAVADOS (BASE 10H)
    t_max = st.session_state.spot_10h + 0.042
    t_jus = st.session_state.spot_10h + 0.030
    t_min = st.session_state.spot_10h - 0.022

    with placeholder.container():
        # ALERTA DE EXAUSTÃO (TRAVADOS)
        if st.session_state.spot_10h > 0:
            if spot >= t_max:
                st.markdown('<div class="alerta-max">⚠️ EXAUSTÃO DE COMPRA (+42 PTS)</div>', unsafe_allow_html=True)
            elif spot <= t_min:
                st.markdown('<div class="alerta-min">⚠️ EXAUSTÃO DE VENDA (-22 PTS)</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="spot-box"><div class="label">USD/BRL SPOT AGORA</div><div style="font-size:36px; font-weight:bold;">{spot:.4f}</div></div>', unsafe_allow_html=True)

        # PARIDADE
        st.markdown('<div class="section-title">ARBITRAGEM GLOBAL (DXY - EWZ)</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center; padding:0 10px; margin-bottom:10px;">'
                    f'<span style="font-size:18px; color:#888;">PARIDADE</span>'
                    f'<span style="font-size:22px; font-weight:bold; color:#FFB900;">{paridade:.4f}</span>'
                    f'<span class="{"pos" if spread >= 0 else "neg"}" style="font-weight:bold;">{spread:+.2f}%</span></div>', unsafe_allow_html=True)

        # ZONAS FLUTUANTES
        st.markdown('<div class="section-title">ZONAS FLUTUANTES (SPOT + PONTOS)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="box-container">'
                    f'<div class="box"><div class="label">MIN (-22)</div><div class="val neg">{f_min:.4f}</div></div>'
                    f'<div class="box"><div class="label">JUS (+30)</div><div class="val blu">{f_jus:.4f}</div></div>'
                    f'<div class="box"><div class="label">MAX (+42)</div><div class="val pos">{f_max:.4f}</div></div></div>', unsafe_allow_html=True)

        # ZONAS TRAVADAS
        if st.session_state.spot_10h > 0:
            st.markdown('<div class="section-title">ZONAS TRAVADAS (BASE 10H)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="box-container">'
                        f'<div class="box"><div class="label">MIN (-22)</div><div class="val neg">{t_min:.4f}</div></div>'
                        f'<div class="box"><div class="label">JUS (+30)</div><div class="val blu">{t_jus:.4f}</div></div>'
                        f'<div class="box"><div class="label">MAX (+42)</div><div class="val pos">{t_max:.4f}</div></div></div>', unsafe_allow_html=True)
        else:
            st.info("Insira o preço das 10h no menu acima para travar as zonas.")

    time.sleep(2)
