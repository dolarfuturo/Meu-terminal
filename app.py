import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL", layout="wide")

# 2. Inicialização da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Letras Quadradas e Menu Lateral "Ghost"
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

    /* Título */
    .terminal-title {
        font-size: 24px;
        color: #FFFFFF;
        font-weight: bold;
        letter-spacing: 2px;
        border-bottom: 2px solid #FFFFFF;
        padding-bottom: 10px;
        margin-bottom: 20px;
        margin-left: 40px; /* Espaço para a aba lateral */
    }

    /* Linhas de Dados */
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0px;
        border-bottom: 1px solid #222;
        margin-left: 40px;
    }

    .ticker-name { font-size: 16px; color: #FFFFFF; width: 180px; font-weight: bold; }
    .ticker-price { font-size: 26px; color: #FFB900; width: 150px; text-align: right; font-weight: bold; }
    .ticker-var { font-size: 20px; width: 100px; text-align: right; font-weight: bold; }

    /* Alvo */
    .alvo-box {
        background-color: #080808;
        border: 1px solid #333;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 6px solid #FFB900;
        margin-left: 40px;
    }
    .alvo-price { font-size: 42px; color: #FFB900; font-weight: bold; }

    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }

    /* MENU LATERAL CUSTOMIZADO (SET ESCONDIDO) */
    .stSidebar {
        background-color: #111111 !important;
        transition: 0.3s;
    }
    
    /* Forçar a abertura da sidebar no mobile */
    [data-testid="stSidebarNav"] {display: none;}
    
    </style>
    """, unsafe_allow_html=True)

# 4. SET NA SIDEBAR (Ao lado esquerdo)
# O Streamlit por padrão deixa uma seta ">" no topo esquerdo para abrir.
with st.sidebar:
    st.markdown("### ⚙️ VARIÁVEIS (SET)")
    val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    v_min = st.number_input("PTS MIN", value=22.0, step=0.5)
    v_jus = st.number_input("PTS JUS", value=31.0, step=0.5)
    v_max = st.number_input("PTS MAX", value=42.0, step=0.5)
    st.divider()
    if st.button("RESET TRAVA 16H"):
        st.session_state.spot_ref_locked = None
    st.markdown("---")
    st.caption("CLIQUE NA SETA « PARA FECHAR")

def get_market_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 5. Renderização Principal
placeholder = st.empty()

while True:
    with placeholder.container():
        st.markdown('<div class="terminal-title">TERMINAL DE CAMBIO</div>', unsafe_allow_html=True)
        
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
            spread_class = "positive" if spread >= 0 else "negative"

            # BLOCO ALVO
            st.markdown(f"""
                <div class="alvo-box">
                    <div style="font-size:14px; margin-bottom:5px;">ALVO SPREAD (SINAL: <span class="{spread_class}">{spread:+.2f}%</span>)</div>
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
                    <div style="display:flex; gap:15px;">
                        <div style="text-align:right;"><span style="font-size:10px; color:#666;">MIN</span><br><span class="negative" style="font-size:18px;">{spot_at + (v_min/1000):.4f}</span></div>
                        <div style="text-align:right;"><span style="font-size:10px; color:#666;">JUS</span><br><span style="font-size:18px; color:#0080FF;">{spot_at + (v_jus/1000):.4f}</span></div>
                        <div style="text-align:right;"><span style="font-size:10px; color:#666;">MAX</span><br><span class="positive" style="font-size:18px;">{spot_at + (v_max/1000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # DXY e EWZ
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">DXY INDEX</div><div class="ticker-price">{d_at:.2f}</div><div class="ticker-var {"positive" if v_dxy >= 0 else "negative"}">{v_dxy:+.2f}%</div><div style="width:300px;"></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">EWZ ADR</div><div class="ticker-price">{e_at:.2f}</div><div class="ticker-var {"positive" if v_ewz >= 0 else "negative"}">{v_ewz:+.2f}%</div><div style="width:300px;"></div></div>', unsafe_allow_html=True)

            # TRAVA
            st.markdown(f'<div class="ticker-row"><div class="ticker-name" style="color:#666;">TRAVA 16H</div><div class="ticker-price" style="color:#444;">{trava_val:.4f}</div><div class="ticker-var" style="color:#444;">FIXED</div><div style="width:300px;"></div></div>', unsafe_allow_html=True)

    time.sleep(2)
