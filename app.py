import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL", layout="wide")

# 2. Memória da Sessão (Correção do AttributeError)
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Estilo Bloomberg Terminal
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    html, body, [class*="st-"], div, span, p {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    .stApp { background-color: #000000; color: #FFFFFF; }
    header {visibility: hidden;}
    .block-container {padding-top: 1rem !important;}

    /* Título Branco */
    .terminal-title {
        font-size: 26px;
        color: #FFFFFF;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }

    /* Linhas de Ativos */
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0px;
        border-bottom: 1px solid #222;
    }

    .ticker-name { font-size: 16px; color: #FFFFFF; width: 180px; font-weight: bold; }
    .ticker-price { font-size: 26px; color: #FFB900; width: 150px; text-align: right; font-weight: bold; }
    .ticker-var { font-size: 20px; width: 100px; text-align: right; font-weight: bold; }

    /* Cores */
    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }

    /* Bloco Alvo */
    .alvo-box {
        background-color: #080808;
        border: 1px solid #333;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 6px solid #FFB900;
    }
    .alvo-price { font-size: 42px; color: #FFB900; font-weight: bold; }

    /* FRP Container */
    .frp-container { display: flex; gap: 20px; }
    .frp-label { font-size: 10px; color: #666; display: block; }
    .frp-value { font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. SET de Variáveis (Escondido em Expander)
st.markdown('<div class="terminal-title">TERMINAL DE CAMBIO</div>', unsafe_allow_html=True)

with st.expander("⚙️ AJUSTAR VARIÁVEIS (SET)"):
    c1, c2, c3, c4 = st.columns(4)
    val_aj_manual = c1.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_min = c2.number_input("PTS MIN", value=22.0)
    v_jus = c3.number_input("PTS JUS", value=31.0)
    v_max = c4.number_input("PTS MAX", value=42.0)
    if st.button("RESET TRAVA 16H"):
        st.session_state.spot_ref_locked = None

def get_data(ticker):
    try:
        d = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return d
    except: return pd.DataFrame()

# 5. Renderização em Tempo Real
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = get_data("BRL=X")
        dxy_df = get_data("DX-Y.NYB")
        ewz_df = get_data("EWZ")
        
        if not spot_df.empty:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Lógica Trava 16h
            try:
                lock_data = spot_df.between_time('15:58', '16:02')
                if not lock_data.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
            except: pass
            
            trava_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

            # Cálculos Globais
            d_at = float(dxy_df['Close'].iloc[-1]) if not dxy_df.empty else 0
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0]) * 100) if not dxy_df.empty else 0
            
            e_at = float(ewz_df['Close'].iloc[-1]) if not ewz_df.empty else 0
            v_ewz = ((e_at - float(ewz_df['Open'].iloc[0])) / float(ewz_df['Open'].iloc[0]) * 100) if not ewz_df.empty else 0

            # Spread e Alvo
            spread = v_dxy - v_ewz
            alvo = val_aj_manual * (1 + (spread/100))
            spread_class = "positive" if spread >= 0 else "negative"

            # Render Alvo
            st.markdown(f"""
                <div class="alvo-box">
                    <div style="font-size:14px;">ALVO SPREAD (SINAL: <span class="{spread_class}">{spread:+.2f}%</span>)</div>
                    <div class="alvo-price">{alvo:.4f}</div>
                </div>
            """, unsafe_allow_html=True)

            # USD/BRL SPOT
            v_s = ((spot_at - val_aj_manual) / val_aj_manual * 100)
            st.markdown(f"""
                <div class="ticker-row">
                    <div class="ticker-name">USD/BRL SPOT</div>
                    <div class="ticker-price">{spot_at:.4f}</div>
                    <div class="ticker-var {'positive' if v_s >= 0 else 'negative'}">{v_s:+.2f}%</div>
                    <div class="frp-container">
                        <div class="frp-item"><span class="frp-label">MIN</span><span class="frp-value negative">{spot_at + (v_min/1000):.4f}</span></div>
                        <div class="frp-item"><span class="frp-label">JUS</span><span class="frp-value" style="color:#0080FF;">{spot_at + (v_jus/1000):.4f}</span></div>
                        <div class="frp-item"><span class="frp-label">MAX</span><span class="frp-value positive">{spot_at + (v_max/1000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # DXY e EWZ
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">DXY INDEX</div><div class="ticker-price">{d_at:.2f}</div><div class="ticker-var {"positive" if v_dxy >= 0 else "negative"}">{v_dxy:+.2f}%</div><div style="width:300px;"></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ticker-row"><div class="ticker-name
