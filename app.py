import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Configuração da Página - Matando o cabeçalho padrão
st.set_page_config(page_title="ATA", layout="centered")

# 2. Inicialização Segura da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Limpeza total e Fonte Quadrada
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    /* Fonte Terminal em tudo */
    html, body, [class*="st-"], div, span, p {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    /* Remove o cabeçalho nativo que causa o erro 'KEYBOARD' */
    header[data-testid="stHeader"] { visibility: hidden; display: none !important; }
    .block-container { padding-top: 1rem !important; }

    .stApp { background-color: #000000; color: #FFFFFF; }

    /* Título ATA */
    .terminal-title {
        font-size: 32px;
        color: #FFFFFF;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        letter-spacing: 8px;
    }

    /* Cards de Ativos (Vertical) */
    .v-card {
        background: #0A0A0A;
        border: 1px solid #222;
        padding: 25px;
        margin-bottom: 20px;
        border-radius: 2px;
    }

    .label-min { font-size: 14px; color: #666; margin-bottom: 8px; }
    .price-big { font-size: 52px; color: #FFB900; font-weight: bold; line-height: 1; }
    .var-big { font-size: 28px; font-weight: bold; }

    /* FRP Vertical dentro do card */
    .frp-box {
        margin-top: 15px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        border-top: 1px solid #222;
        padding-top: 15px;
    }
    .frp-line { display: flex; justify-content: space-between; font-size: 20px; font-weight: bold; }

    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }

    /* Estilo do botão de acesso SET */
    .stExpander {
        border: 1px solid #333 !important;
        background: #111 !important;
        margin-bottom: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Topo do Terminal
st.markdown('<div class="terminal-title">ATA</div>', unsafe_allow_html=True)

# Acesso às variáveis (SET) via Expander limpo
with st.expander("SET «"):
    col1, col2 = st.columns(2)
    val_aj_manual = col1.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_min = col2.number_input("PTS MIN", value=22.0)
    v_jus = col1.number_input("PTS JUS", value=31.0)
    v_max = col2.number_input("PTS MAX", value=42.0)
    if st.button("LIMPAR TRAVA"):
        st.session_state.spot_ref_locked = None

def get_market_data(ticker):
    try:
        return yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
    except: return pd.DataFrame()

# 5. Loop de Renderização
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = get_market_data("BRL=X")
        dxy_df = get_market_data("DX-Y.NYB")
        ewz_df = get_market_data("EWZ")

        if not spot_df.empty:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Lógica Trava Segura
            try:
                lock = spot_df.between_time('15:58', '16:02')
                if not lock.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock['Close'].iloc[-1])
            except: pass
            trava_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

            # Cálculos de Mercado
            d_at = float(dxy_df['Close'].iloc[-1]) if not dxy_df.empty else 0
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0]) * 100) if not dxy_df.empty else 0
            e_at = float(ewz_df['Close'].iloc[-1]) if not ewz_df.empty else 0
            v_ewz = ((e_at - float(ewz_df['Open'].iloc[0])) / float(ewz_df['Open'].iloc[0]) * 100) if not ewz_df.empty else 0

            spread = v_dxy - v_ewz
            alvo = val_aj_manual * (1 + (spread/100))
            v_s = ((spot_at - val_aj_manual) / val_aj_manual * 100)

            # --- LAYOUT VERTICAL ---

            # CARD 1: ALVO
            st.markdown(f"""
                <div class="v-card" style="border-left: 8px solid #FFB900;">
                    <div class="label-min">ALVO SPREAD</div>
                    <div style="display:flex; justify-content:space-between; align-items:baseline;">
                        <div class="price-big">{alvo:.4f}</div>
                        <div class="var-big {'positive' if spread >= 0 else 'negative'}">{spread:+.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # CARD 2: USD/BRL SPOT + FRP
            st.markdown(f"""
                <div class="v-card">
                    <div class="label-min">USD/BRL SPOT</div>
                    <div style="display:flex; justify-content:space-between; align-items:baseline;">
                        <div class="price-big" style="color:#FFF;">{spot_at:.4f}</div>
                        <div class="var-big {'positive' if v_s >= 0 else 'negative'}">{v_s:+.2f}%</div>
                    </div>
                    <div class="frp-box">
                        <div class="frp-line"><span>MIN</span><span class="negative">{spot_at + (v_min/1000):.4f}</span></div>
                        <div class="frp-line"><span>JUS</span><span style="color:#0080FF;">{spot_at + (v_jus/1000):.4f}</span></div>
                        <div class="frp-line"><span>MAX</span><span class="positive">{spot_at + (v_max/1000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # CARD 3: DXY
            st.markdown(f"""
                <div class="v-card">
                    <div class="label-min">DXY INDEX</div>
                    <div style="display:flex; justify-content:space-between; align-items:baseline;">
                        <div style="font-size:38px; font-weight:bold;">{d_at:.2f}</div>
                        <div class="var-big {'positive' if v_
