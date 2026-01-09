import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL", layout="wide")

# 2. Inicialização Segura da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Letras Quadradas e Limpeza de Interface
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    html, body, [class*="st-"], div, span, p {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Remove elementos nativos do Streamlit que poluem o topo */
    header {visibility: hidden;}
    .block-container {padding-top: 1rem !important;}
    footer {visibility: hidden;}

    /* Estilo do Título */
    .terminal-title {
        font-size: 24px;
        color: #FFFFFF;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 15px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }

    /* Linhas de Dados */
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0px;
        border-bottom: 1px solid #222;
    }

    .ticker-name { font-size: 15px; color: #FFFFFF; width: 180px; font-weight: bold; }
    .ticker-price { font-size: 26px; color: #FFB900; width: 150px; text-align: right; font-weight: bold; }
    .ticker-var { font-size: 20px; width: 100px; text-align: right; font-weight: bold; }

    /* Alvo Bloomberg */
    .alvo-box {
        background-color: #080808;
        border: 1px solid #333;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 6px solid #FFB900;
    }
    .alvo-price { font-size: 40px; color: #FFB900; font-weight: bold; }

    /* Cores de Sinal */
    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }

    /* Esconde o expander visualmente para parecer um botão do terminal */
    .stExpander {
        border: 1px solid #444 !important;
        background-color: #111 !important;
        margin-bottom: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Título e SET de Variáveis (Escondido)
st.markdown('<div class="terminal-title">TERMINAL DE CAMBIO</div>', unsafe_allow_html=True)

with st.expander("⌨️ ACESSAR VARIÁVEIS (SET)"):
    c1, c2, c3, c4 = st.columns(4)
    val_aj_manual = c1.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_min = c2.number_input("PTS MIN", value=22.0)
    v_jus = c3.number_input("PTS JUS", value=31.0)
    v_max = c4.number_input("PTS MAX", value=42.0)
    if st.button("RESET TRAVA 16H"):
        st.session_state.spot_ref_locked = None

def get_market_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 5. Loop de Atualização
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = get_market_data("BRL=X")
        dxy_df = get_market_data("DX-Y.NYB")
        ewz_df = get_market_data("EWZ")

        if not spot_df.empty:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Lógica de Trava (Correção do AttributeError)
            try:
                lock_data = spot_df.between_time('15:58', '16:02')
                if not lock_data.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
            except: pass
            
            trava_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

            # Cálculos de Mercado
            d_at = float(dxy_df['Close'].iloc[-1]) if not dxy_df.empty else 0
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0]) * 100) if not dxy_df.empty else 0
            
            e_at = float(ewz_df['Close'].iloc[-1]) if not ewz_df.empty else 0
            v_ewz = ((e_at - float(ewz_df['Open'].iloc[0])) / float(ewz_df['Open'].iloc[0]) * 100) if not ewz_df.empty else 0

            # Spread e Alvo
            spread = v_dxy - v_ewz
            alvo = val_aj_manual * (1 + (spread/100))
            spread_class = "positive" if spread >= 0 else "negative"

            # RENDER: BLOCO ALVO
            st.markdown(f"""
                <div class="alvo-box">
                    <div style="font-size:14px; margin-bottom:5px;">PREÇO ALVO PELO SPREAD (SINAL: <span class="{spread_class}">{spread:+.2f}%</span>)</div>
                    <div class="alvo-price">{alvo:.4f}</div>
                </div>
            """, unsafe_allow_html=True)

            # RENDER: USD/BRL SPOT
            v_s = ((spot_at - val_aj_manual) / val_aj_manual * 100)
            st.markdown(f"""
                <div class="ticker-row">
                    <div class="ticker-name">USD/BRL SPOT</div>
                    <div class="ticker-price">{spot_at:.4f}</div>
                    <div class="ticker-var {'positive' if v_s >= 0 else 'negative'}">{v_s:+.2f}%</div>
                    <div style="display:flex; gap:20px;">
                        <div style="text-align:right;"><span style="font-size:10px; color:#666; display:block;">MIN</span><span class="negative" style="font-size:18px;">{spot_at + (v_min/1000):.4f}</span></div>
                        <div style="text-align:right;"><span style="font-size:10px; color:#666; display:block;">JUS</span><span style="font-size:18px; color:#0080FF;">{spot_at + (v_jus/1000):.4f}</span></div>
                        <div style="text-align:right;"><span style="font-size:10px; color:#666; display:block;">MAX</span><span class="positive" style="font-size:18px;">{spot_at + (v_max/1000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # RENDER: DXY E EWZ
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">DXY INDEX</div><div class="ticker-price">{d_at:.2f}</div><div class="ticker-var {"positive" if v_dxy >= 0 else "negative"}">{v_dxy:+.2f}%</div><div style="width:300px;"></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">EWZ ADR</div><div class="ticker-price">{e_at:.2f}</div><div class="ticker-var {"positive" if v_ewz >= 0 else "negative"}">{v_ewz:+.2f}%</div><div style="width:300px;"></div></div>', unsafe_allow_html=True)

            # RENDER: TRAVA
            st.markdown(f'<div class="ticker-row"><div class="ticker-name" style="color:#666;">TRAVA 16H</div><div class="ticker-price" style="color:#444;">{trava_val:.4f}</div><div class="ticker-var" style="color:#444;">FIXED</div><div style="width:300px;"></div></div>', unsafe_allow_html=True)

    time.sleep(2)
