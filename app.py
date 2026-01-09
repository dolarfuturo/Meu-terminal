import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# 2. Inicialização da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS PARA MATAR O "KEYBOARD" E AJUSTAR A SETA
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    /* Força fonte quadrada em tudo */
    html, body, [class*="st-"], div, span, p {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    /* ESCONDE O CABEÇALHO NATIVO (Onde aparece o Keyboard) */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Ajuste de Espaçamento do Topo */
    .block-container {
        padding-top: 0rem !important;
        max-width: 500px; /* Mantém vertical no centro */
    }

    /* Título Limpo */
    .terminal-title {
        font-size: 20px;
        color: #FFFFFF;
        font-weight: bold;
        padding: 20px 0 10px 0;
        border-bottom: 1px solid #333;
        margin-bottom: 10px;
        text-align: center;
    }

    /* Blocos Verticais */
    .v-block {
        border-bottom: 1px solid #222;
        padding: 15px 5px;
    }

    .main-price { font-size: 44px; color: #FFB900; font-weight: bold; line-height: 1; }
    .label-min { font-size: 11px; color: #666; }

    /* Cores */
    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }

    /* Forçar a seta da Sidebar a ser branca e visível */
    [data-testid="sidebar-button"] {
        color: white !important;
        background: #222 !important;
        border-radius: 5px !important;
        left: 10px !important;
        top: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. SET NA SIDEBAR (Acesso pela seta lateral esquerda)
with st.sidebar:
    st.markdown("### « SET VARIÁVEIS")
    val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_min = st.number_input("PTS MIN", value=22.0)
    v_jus = st.number_input("PTS JUS", value=31.0)
    v_max = st.number_input("PTS MAX", value=42.0)
    if st.button("RESET TRAVA 16H"):
        st.session_state.spot_ref_locked = None

def get_data(ticker):
    try:
        return yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
    except: return pd.DataFrame()

# 5. Interface Principal
st.markdown('<div class="terminal-title">TERMINAL DE CAMBIO</div>', unsafe_allow_html=True)
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = get_data("BRL=X")
        dxy_df = get_data("DX-Y.NYB")
        ewz_df = get_data("EWZ")

        if not spot_df.empty:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Trava 16h
            try:
                lock = spot_df.between_time('15:58', '16:02')
                if not lock.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock['Close'].iloc[-1])
            except: pass
            trava_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

            # Cálculos
            d_at = float(dxy_df['Close'].iloc[-1]) if not dxy_df.empty else 0
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0]) * 100) if not dxy_df.empty else 0
            e_at = float(ewz_df['Close'].iloc[-1]) if not ewz_df.empty else 0
            v_ewz = ((e_at - float(ewz_df['Open'].iloc[0])) / float(ewz_df['Open'].iloc[0]) * 100) if not ewz_df.empty else 0

            spread = v_dxy - v_ewz
            alvo = val_aj_manual * (1 + (spread/100))
            v_s = ((spot_at - val_aj_manual) / val_aj_manual * 100)

            # --- RENDER VERTICAL ---
            
            # BLOCO ALVO
            st.markdown(f"""
                <div class="v-block" style="background:#080808; border-left: 5px solid #FFB900; padding-left:15px;">
                    <div class="label-min">ALVO SPREAD</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div class="main-price">{alvo:.4f}</div>
                        <div style="font-size:22px;" class="{'positive' if spread >= 0 else 'negative'}">{spread:+.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # BLOCO SPOT + FRP
            st.markdown(f"""
                <div class="v-block">
                    <div class="label-min">USD/BRL SPOT</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div class="main-price" style="color:#FFF;">{spot_at:.4f}</div>
                        <div style="font-size:22px;" class="{'positive' if v_s >= 0 else 'negative'}">{v_s:+.2f}%</div>
                    </div>
                    <div style="margin-top:15px; display:flex; flex-direction:column; gap:5px;">
                        <div style="display:flex; justify-content:space-between;"><span>MIN</span><span class="negative">{spot_at + (v_min/1000):.4f}</span></div>
                        <div style="display:flex; justify-content:space-between;"><span>JUS</span><span style="color:#0080FF;">{spot_at + (v_jus/1000):.4f}</span></div>
                        <div style="display:flex; justify-content:space-between;"><span>MAX</span><span class="positive">{spot_at + (v_max/1000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # BLOCO ÍNDICES
            c1, c2 = st.columns(2)
            c1.markdown(f'<div class="label-min">DXY</div><div style="font-size:20px;">{d_at:.2f} <span class="{"positive" if v_dxy >= 0 else "negative"}">{v_dxy:+.2f}%</span></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="label-min">EWZ</div><div style="font-size:20px;">{e_at:.2f} <span class="{"positive" if v_ewz >= 0 else "negative"}">{v_ewz:+.2f}%</span></div>', unsafe_allow_html=True)

            # TRAVA
            st.markdown(f'<div style="text-align:center; padding:20px; color:#444; font-size:12px;">TRAVA 16H: {trava_val:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
