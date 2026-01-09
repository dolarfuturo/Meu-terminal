import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL", layout="centered")

# 2. Inicialização da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Estilo Bloomberg, Espaçamento e Remoção de Lixo do Topo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    html, body, [class*="st-"], div, span, p {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Esconde o cabeçalho nativo que gera o erro 'Keyboard' */
    header[data-testid="stHeader"] { visibility: hidden; display: none; }
    .block-container { padding-top: 1rem !important; }

    /* Container de Título */
    .terminal-header {
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #333;
        margin-bottom: 20px;
    }
    .terminal-title { font-size: 22px; font-weight: bold; letter-spacing: 2px; }

    /* Blocos de Preço */
    .price-card {
        background: #080808;
        border: 1px solid #222;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    
    .label-text { font-size: 12px; color: #888; margin-bottom: 8px; }
    .value-main { font-size: 48px; font-weight: bold; color: #FFB900; line-height: 1; }
    .value-sub { font-size: 24px; font-weight: bold; }

    /* FRP Vertical Espaçado */
    .frp-container {
        margin-top: 20px;
        padding-top: 15px;
        border-top: 1px solid #222;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .frp-row { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; }

    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }

    /* Estilo do Botão SET */
    .stExpander { border: 1px solid #444 !important; background: #111 !important; margin-bottom: 30px !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. Título e Acesso às Variáveis (SET) no topo
st.markdown('<div class="terminal-header"><div class="terminal-title">TERMINAL DE CAMBIO</div></div>', unsafe_allow_html=True)

# O acesso agora é um Expander claro e direto
with st.expander("⚙️ ACESSAR VARIÁVEIS (SET) «"):
    col1, col2 = st.columns(2)
    val_aj_manual = col1.number_input("AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    v_min = col2.number_input("PTS MIN", value=22.0, step=0.5)
    v_jus = col1.number_input("PTS JUS", value=31.0, step=0.5)
    v_max = col2.number_input("PTS MAX", value=42.0, step=0.5)
    if st.button("LIMPAR TRAVA 16H"):
        st.session_state.spot_ref_locked = None

def get_market_data(ticker):
    try:
        return yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
    except: return pd.DataFrame()

# 5. Renderização em Loop
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = get_market_data("BRL=X")
        dxy_df = get_market_data("DX-Y.NYB")
        ewz_df = get_market_data("EWZ")

        if not spot_df.empty:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Lógica Trava
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

            # --- DISPLAY VERTICAL ESPAÇADO ---

            # BLOCO 1: ALVO
            st.markdown(f"""
                <div class="price-card" style="border-left: 6px solid #FFB900;">
                    <div class="label-text">PREÇO ALVO (SPREAD)</div>
                    <div style="display:flex; justify-content:space-between; align-items:baseline;">
                        <div class="value-main">{alvo:.4f}</div>
                        <div class="value-sub {'positive' if spread >= 0 else 'negative'}">{spread:+.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # BLOCO 2: SPOT E PONTOS
            st.markdown(f"""
                <div class="price-card">
                    <div class="label-text">USD/BRL SPOT</div>
                    <div style="display:flex; justify-content:space-between; align-items:baseline;">
                        <div class="value-main" style="color:white;">{spot_at:.4f}</div>
                        <div class="value-sub {'positive' if v_s >= 0 else 'negative'}">{v_s:+.2f}%</div>
                    </div>
                    <div class="frp-container">
                        <div class="frp-row"><span>MIN</span><span class="negative">{spot_at + (v_min/1000):.4f}</span></div>
                        <div class="frp-row"><span>JUS</span><span style="color:#0080FF;">{spot_at + (v_jus/1000):.4f}</span></div>
                        <div class="frp-row"><span>MAX</span><span class="positive">{spot_at + (v_max/1000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # BLOCO 3: ÍNDICES (LADO A LADO)
            c1, c2 = st.columns(2)
            c1.markdown(f"""
                <div class="price-card" style="padding:15px;">
                    <div class="label-text">DXY</div>
                    <div style="font-size:20px; font-weight:bold;">{d_at:.2f}</div>
                    <div class="{'positive' if v_dxy >= 0 else 'negative'}">{v_dxy:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
            c2.markdown(f"""
                <div class="price-card" style="padding:15px;">
                    <div class="label-text">EWZ</div>
                    <div style="font-size:20px; font-weight:bold;">{e_at:.2f}</div>
                    <div class="{'positive' if v_ewz >= 0 else 'negative'}">{v_ewz:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

            # TRAVA
            st.markdown(f'<div style="text-align:center; color:#555; font-size:12px; margin-top:10px;">TRAVA 16H: {trava_val:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
