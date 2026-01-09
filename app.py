import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página para Mobile/Vertical
st.set_page_config(page_title="TERMINAL", layout="centered")

# 2. Inicialização da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Layout Vertical e Botão SET Manual
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    html, body, [class*="st-"], div, span, p {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    .stApp { background-color: #000000; color: #FFFFFF; }
    header {visibility: hidden;}
    .block-container {padding-top: 0.5rem !important; padding-left: 1rem; padding-right: 1rem;}

    /* Título e Botão SET */
    .header-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .terminal-title {
        font-size: 18px;
        color: #FFFFFF;
        font-weight: bold;
    }

    /* Blocos Verticais */
    .vertical-block {
        border-bottom: 1px solid #222;
        padding: 15px 0px;
        margin-bottom: 5px;
    }

    .label-small { font-size: 12px; color: #666; margin-bottom: 5px; }
    
    .main-price { font-size: 40px; color: #FFB900; font-weight: bold; line-height: 1; }
    
    .row-flex { display: flex; justify-content: space-between; align-items: baseline; }
    
    .var-badge { font-size: 20px; font-weight: bold; }

    /* FRP Vertical */
    .frp-box {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 10px;
        background: #0A0A0A;
        padding: 10px;
        border-radius: 4px;
    }
    .frp-line { display: flex; justify-content: space-between; font-size: 16px; }

    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. SET - Variáveis Escondidas no Expander (Substituindo a Sidebar problemática)
st.markdown('<div class="header-nav"><div class="terminal-title">TERMINAL DE CAMBIO</div></div>', unsafe_allow_html=True)

with st.expander("SET « (AJUSTAR VARIÁVEIS)"):
    val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    v_min = st.number_input("PTS MIN", value=22.0, step=0.5)
    v_jus = st.number_input("PTS JUS", value=31.0, step=0.5)
    v_max = st.number_input("PTS MAX", value=42.0, step=0.5)
    if st.button("RESET TRAVA 16H"):
        st.session_state.spot_ref_locked = None

def get_market_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 5. Loop Principal
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = get_market_data("BRL=X")
        dxy_df = get_market_data("DX-Y.NYB")
        ewz_df = get_market_data("EWZ")

        if not spot_df.empty:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Trava 16h
            try:
                lock_data = spot_df.between_time('15:58', '16:02')
                if not lock_data.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
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

            # --- BLOCO 1: ALVO (VERTICAL) ---
            st.markdown(f"""
                <div class="vertical-block" style="border-left: 5px solid #FFB900; padding-left:15px; background:#080808;">
                    <div class="label-small">ALVO SPREAD</div>
                    <div class="row-flex">
                        <div class="main-price">{alvo:.4f}</div>
                        <div class="var-badge {'positive' if spread >= 0 else 'negative'}">{spread:+.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # --- BLOCO 2: USD/BRL SPOT ---
            st.markdown(f"""
                <div class="vertical-block">
                    <div class="label-small">USD/BRL SPOT</div>
                    <div class="row-flex">
                        <div class="main-price" style="color:#FFF;">{spot_at:.4f}</div>
                        <div class="var-badge {'positive' if v_s >= 0 else 'negative'}">{v_s:+.2f}%</div>
                    </div>
                    <div class="frp-box">
                        <div class="frp-line"><span>MIN</span><span class="negative">{spot_at + (v_min/1000):.4f}</span></div>
                        <div class="frp-line"><span>JUS</span><span style="color:#0080FF;">{spot_at + (v_jus/1000):.4f}</span></div>
                        <div class="frp-line"><span>MAX</span><span class="positive">{spot_at + (v_max/1000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # --- BLOCO 3: ÍNDICES ---
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                    <div class="vertical-block">
                        <div class="label-small">DXY</div>
                        <div style="font-size:22px; font-weight:bold;">{d_at:.2f}</div>
                        <div class="{'positive' if v_dxy >= 0 else 'negative'}">{v_dxy:+.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                    <div class="vertical-block">
                        <div class="label-small">EWZ</div>
                        <div style="font-size:22px; font-weight:bold;">{e_at:.2f}</div>
                        <div class="{'positive' if v_ewz >= 0 else 'negative'}">{v_ewz:+.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)

            # --- BLOCO 4: TRAVA ---
            st.markdown(f"""
                <div style="padding:10px 0; color:#444; font-size:14px; text-align:center; border-top:1px solid #111;">
                    TRAVA 16H: {trava_val:.4f} • FIXED
                </div>
            """, unsafe_allow_html=True)

    time.sleep(2)
