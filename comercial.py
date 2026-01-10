import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL ARBITRAGEM", layout="wide")

if 'spot_10h' not in st.session_state:
    st.session_state.spot_10h = 0.0

# 2. ESTILO CSS CLEAN
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 500px !important; margin: auto; }
    
    .section-title { font-size: 11px; color: #444; border-bottom: 1px solid #111; padding-bottom: 3px; margin: 15px 0 10px 0; }
    
    .alerta { padding: 8px; border-radius: 4px; text-align: center; font-size: 13px; margin-bottom: 15px; font-weight: bold; }
    .caro { background: rgba(255, 0, 0, 0.2); color: #FF4B4B; border: 1px solid #FF4B4B; }
    .barato { background: rgba(0, 255, 0, 0.15); color: #00FF00; border: 1px solid #00FF00; }
    .neutro { background: #111; color: #666; border: 1px solid #222; }

    .box-container { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 15px; }
    .box { background: #080808; padding: 15px 5px; border-radius: 4px; width: 33%; text-align: center; border: 1px solid #111; }
    .label { font-size: 10px; color: #555; margin-bottom: 5px; }
    .val { font-size: 19px; font-weight: bold; }
    
    .pos { color: #FF4B4B !important; } 
    .neg { color: #00FF00 !important; } 
    .blu { color: #0080FF !important; } 
    .ora { color: #FFB900 !important; }
</style>
""", unsafe_allow_html=True)

# 3. ENTRADAS DE DADOS
with st.popover("⚙️ REFERÊNCIAS"):
    v_ajuste = st.number_input("AJUSTE ANTERIOR", value=5.4000, format="%.4f")
    st.session_state.spot_10h = st.number_input("SPOT 10H", value=st.session_state.spot_10h, format="%.4f")

def get_data():
    try:
        # Puxa dados com suporte a Pre-Market (inicia às 4h BRT)
        d_ticker = yf.Ticker("DX-Y.NYB")
        e_ticker = yf.Ticker("EWZ")
        
        # Spot USD/BRL
        s_df = yf.download("BRL=X", period="1d", interval="1m", progress=False)
        s_at = float(s_df['Close'].iloc[-1])
        
        # DXY e EWZ com Pre-Market
        # Usamos period=2d para garantir que temos o fechamento de ontem (prev) e o agora
        d_df = yf.download("DX-Y.NYB", period="2d", interval="1m", progress=False, prepost=True)
        e_df = yf.download("EWZ", period="2d", interval="1m", progress=False, prepost=True)
        
        # Preço de fechamento de ontem (referência para variação %)
        d_prev = float(d_ticker.fast_info.previous_close)
        e_prev = float(e_ticker.fast_info.previous_close)
        
        # Preço atual (considerando pré-mercado se disponível)
        d_at = float(d_df['Close'].iloc[-1])
        e_at = float(e_df['Close'].iloc[-1])
        
        d_v = ((d_at - d_prev) / d_prev * 100)
        e_v = ((e_at - e_prev) / e_prev * 100)
        
        return s_at, (d_v - e_v)
    except: 
        return 0.0, 0.0

placeholder = st.empty()

while True:
    spot, spread = get_data()
    paridade = v_ajuste * (1 + (spread/100))
    
    # CÁLCULOS SOLICITADOS
    # Dinâmicos (Base Spot)
    f_max, f_jus, f_min = spot + 0.042, spot + 0.030, spot - 0.022
    # Travados (Base 10h)
    t_max, t_jus, t_min = st.session_state.spot_10h + 0.042, st.session_state.spot_10h + 0.030, st.session_state.spot_10h - 0.022

    with placeholder.container():
        # ALERTA DISCRETO (Baseado nas Travas de 10h)
        if st.session_state.spot_10h > 0:
            if spot >= t_max:
                st.markdown('<div class="alerta caro">DÓLAR CARO / EXAUSTÃO</div>', unsafe_allow_html=True)
            elif spot <= t_min:
                st.markdown('<div class="alerta barato">DÓLAR BARATO / EXAUSTÃO</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alerta neutro">ZONA DE EQUILÍBRIO</div>', unsafe_allow_html=True)

        # PARIDADE (SÓ PREÇO)
        st.markdown('<div class="section-title">EQUILÍBRIO GLOBAL (DESDE 4H BRT)</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; padding:10px;"><span style="font-size:32px; font-weight:bold; color:#FFB900;">{paridade:.4f}</span></div>', unsafe_allow_html=True)

        # REFERÊNCIA ATUAL (DINÂMICA)
        st.markdown('<div class="section-title">REFERÊNCIA DE PREÇO (SPOT)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="box-container">'
                    f'<div class="box"><div class="label">MÍNIMA</div><div class="val neg">{f_min:.4f}</div></div>'
                    f'<div class="box"><div class="label">PREÇO JUSTO</div><div class="val blu">{f_jus:.4f}</div></div>'
                    f'<div class="box"><div class="label">MÁXIMA</div><div class="val pos">{f_max:.4f}</div></div></div>', unsafe_allow_html=True)

        # REFERÊNCIA FIXA (TRAVADA 10H)
        if st.session_state.spot_10h > 0:
            st.markdown(f'<div class="section-title">REFERÊNCIA DE PREÇO (10H)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="box-container">'
                        f'<div class="box"><div class="label">MÍNIMA</div><div class="val neg">{t_min:.4f}</div></div>'
                        f'<div class="box"><div class="label">PREÇO JUSTO</div><div class="val blu">{t_jus:.4f}</div></div>'
                        f'<div class="box"><div class="label">MÁXIMA</div><div class="val pos">{t_max:.4f}</div></div></div>', unsafe_allow_html=True)

    time.sleep(2)
