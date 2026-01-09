import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="ATA", layout="centered")

# 2. Inicialização Segura da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Limpeza de Cabeçalho e Layout Vertical
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    html, body, [class*="st-"], div, span, p {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    /* Remove o texto 'KEYBOARD' e cabeçalhos nativos */
    header[data-testid="stHeader"] { visibility: hidden; display: none !important; }
    .block-container { padding-top: 1rem !important; }

    .stApp { background-color: #000000; color: #FFFFFF; }

    .terminal-title {
        font-size: 28px;
        color: #FFFFFF;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        letter-spacing: 4px;
    }

    /* Cards Verticais */
    .v-card {
        background: #0A0A0A;
        border: 1px solid #222;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 2px;
    }

    .label-min { font-size: 12px; color: #666; margin-bottom: 5px; }
    
    /* Preço Alvo Ajustado (Normal) */
    .price-alvo { font-size: 38px; color: #FFB900; font-weight: bold; }
    
    /* Preço Spot e outros */
    .price-main { font-size: 42px; color: #FFFFFF; font-weight: bold; line-height: 1; }
    .var-text { font-size: 22px; font-weight: bold; }

    /* FRP Vertical */
    .frp-box {
        margin-top: 15px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        border-top: 1px solid #222;
        padding-top: 10px;
    }
    .frp-line { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; }

    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }

    /* Estilo do Botão SET « */
    .stExpander {
        border: 1px solid #333 !important;
        background: #111 !important;
        margin-bottom: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Topo
st.markdown('<div class="terminal-title">ATA</div>', unsafe_allow_html=True)

# SET Retrátil
with st.expander("SET «"):
    c1, c2 = st.columns(2)
    val_aj_manual = c1.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_min = c2.number_input("PTS MIN", value=22.0)
    v_jus = c1.number_input("PTS JUS", value=31.0)
    v_max = c2.number_input("PTS MAX", value=42.0)
    if st.button("LIMPAR TRAVA"):
        st.session_state.spot_ref_locked = None

def get_market_data(ticker):
    try:
        return yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
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
            
            # Trava
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

            # --- RENDERIZAÇÃO VERTICAL ---

            # 1. ALVO
            st.markdown(f"""
                <div class="v-card" style="border-left: 6px solid #FFB900;">
                    <div class="label-min">ALVO SPREAD</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div class="price-alvo">{alvo:.4f}</div>
                        <div class="var-text {'positive' if spread >= 0 else 'negative'}">{spread:+.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 2. SPOT
            st.markdown(f"""
                <div class="v-card">
                    <div class="label-min">USD/BRL SPOT</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div class="price-main">{spot_at:.4f}</div>
                        <div class="var-text {'positive' if v_s >= 0 else 'negative'}">{v_s:+.2f}%</div>
                    </div>
                    <div class="frp-box">
                        <div class="frp-line"><span>MIN</span><span class="negative">{spot_at + (v_min/1000):.4f}</span></div>
                        <div class="frp-line"><span>JUS</span><span style="color:#0080FF;">{spot_at + (v_jus/1000):.4f}</span></div>
                        <div class="frp-line"><span>MAX</span><span class="positive">{spot_at + (v_max/1000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 3. DXY
            st.markdown(f"""
                <div class="v-card">
                    <div class="label-min">DXY INDEX</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-size:30px; font-weight:bold;">{d_at:.2f}</div>
                        <div class="var-text {'positive' if v_dxy >= 0 else 'negative'}">{v_dxy:+.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 4. EWZ
            st.markdown(f"""
                <div class="v-card">
                    <div class="label-min">EWZ ADR</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-size:30px; font-weight:bold;">{e_at:.2f}</div>
                        <div class="var-big {'positive' if v_ewz >= 0 else 'negative'}">{v_ewz:+.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # TRAVA
            st.markdown(f'<div style="text-align:center; color:#444; font-size:12px; margin-bottom:40px;">TRAVA 16H: {trava_val:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
