import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Configuração da Página - Sidebar aberta por padrão para facilitar o ajuste lateral
st.set_page_config(page_title="ATA", layout="wide", initial_sidebar_state="expanded")

# 2. Inicialização Segura da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Estilo Limpo, Sem Quadros e Alinhamento Vertical
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    html, body, [class*="st-"], div, span, p {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    /* Esconde cabeçalhos nativos e erro Keyboard */
    header[data-testid="stHeader"] { visibility: hidden; display: none !important; }
    .block-container { padding-top: 2rem !important; max-width: 600px !important; }

    .stApp { background-color: #000000; color: #FFFFFF; }

    /* Estilo Sidebar (SET Lateral) */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #333;
    }

    .terminal-title {
        font-size: 30px;
        color: #FFFFFF;
        font-weight: bold;
        margin-bottom: 30px;
        letter-spacing: 6px;
    }

    /* Layout Vertical Sem Quadros */
    .asset-row {
        margin-bottom: 35px;
        padding-bottom: 10px;
    }

    .label-small { font-size: 11px; color: #666; letter-spacing: 1px; margin-bottom: 2px; }
    
    /* Valor Spread Reduzido */
    .price-spread { font-size: 32px; color: #FFB900; font-weight: bold; }
    
    /* Valor Spot e outros */
    .price-main { font-size: 40px; color: #FFFFFF; font-weight: bold; line-height: 1; }
    .var-badge { font-size: 20px; font-weight: bold; }

    /* FRP Alinhado */
    .frp-container {
        margin-top: 10px;
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .frp-item { display: flex; justify-content: space-between; font-size: 18px; width: 250px; }

    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. SET LATERAL (Aparece ao lado)
with st.sidebar:
    st.markdown("### SET «")
    st.markdown("---")
    val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    v_min = st.number_input("PTS MIN", value=22.0, step=0.1)
    v_jus = st.number_input("PTS JUS", value=31.0, step=0.1)
    v_max = st.number_input("PTS MAX", value=42.0, step=0.1)
    st.markdown("---")
    if st.button("LIMPAR TRAVA"):
        st.session_state.spot_ref_locked = None

def get_market_data(ticker):
    try:
        return yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
    except: return pd.DataFrame()

# 5. Interface Principal (ATA)
st.markdown('<div class="terminal-title">ATA</div>', unsafe_allow_html=True)
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

            # --- LAYOUT VERTICAL SEM QUADROS ---

            # 1. ALVO SPREAD (Reduzido e Alinhado)
            st.markdown(f"""
                <div class="asset-row">
                    <div class="label-small">ALVO SPREAD</div>
                    <div style="display:flex; gap:20px; align-items:baseline;">
                        <span class="price-spread">{alvo:.4f}</span>
                        <span class="var-badge {'positive' if spread >= 0 else 'negative'}">{spread:+.2f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 2. USD/BRL SPOT + FRP
            st.markdown(f"""
                <div class="asset-row">
                    <div class="label-small">USD/BRL SPOT</div>
                    <div style="display:flex; gap:20px; align-items:baseline;">
                        <span class="price-main">{spot_at:.4f}</span>
                        <span class="var-badge {'positive' if v_s >= 0 else 'negative'}">{v_s:+.2f}%</span>
                    </div>
                    <div class="frp-container">
                        <div class="frp-item"><span>MIN</span><span class="negative">{spot_at + (v_min/1000):.4f}</span></div>
                        <div class="frp-item"><span>JUS</span><span style="color:#0080FF;">{spot_at + (v_jus/1000):.4f}</span></div>
                        <div class="frp-item"><span>MAX</span><span class="positive">{spot_at + (v_max/1000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 3. DXY
            st.markdown(f"""
                <div class="asset-row">
                    <div class="label-small">DXY INDEX</div>
                    <div style="display:flex; gap:20px; align-items:baseline;">
                        <span style="font-size:28px; font-weight:bold;">{d_at:.2f}</span>
                        <span class="var-badge {'positive' if v_dxy >= 0 else 'negative'}">{v_dxy:+.2f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 4. EWZ
            st.markdown(f"""
                <div class="asset-row">
                    <div class="label-small">EWZ ADR</div>
                    <div style="display:flex; gap:20px; align-items:baseline;">
                        <span style="font-size:28px; font-weight:bold;">{e_at:.2f}</span>
                        <span class="var-badge {'positive' if v_ewz >= 0 else 'negative'}">{v_ewz:+.2f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 5. TRAVA (Rodapé discreto)
            st.markdown(f'<div style="color:#444; font-size:12px; margin-top:20px;">TRAVA 16H: {trava_val:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
