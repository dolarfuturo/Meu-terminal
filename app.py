import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL DE CÂMBIO", layout="wide")

# 2. Memória da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS BLOOMBERG TOTAL (Fontes Quadradas e Alinhamento)
st.markdown("""
    <style>
    /* Importação de fontes quadradas */
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');

    /* Aplicação global da fonte quadrada */
    html, body, [class*="st-"], div, span, p {
        font-family: 'Share Tech Mono', 'Roboto Mono', 'Courier New', monospace !important;
        text-transform: uppercase;
    }

    .stApp { 
        background-color: #000000; 
        color: #FFFFFF; 
    }

    /* Cabeçalho do Terminal */
    .terminal-header {
        background-color: #1a1a1a;
        padding: 5px 15px;
        border-bottom: 2px solid #ffffff;
        margin-bottom: 15px;
    }

    .terminal-title {
        font-size: 22px;
        color: #ffffff;
        letter-spacing: 4px;
        font-weight: bold;
    }

    /* Linhas de Ativos */
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
        border-bottom: 1px solid #333;
        background-color: #000000;
        letter-spacing: 1px;
    }

    .ticker-name { font-size: 14px; color: #00e5ff; width: 180px; font-weight: bold; }
    .ticker-price { font-size: 26px; color: #ffb900; width: 150px; text-align: right; font-weight: bold; }
    .ticker-var { font-size: 18px; width: 110px; text-align: right; font-weight: bold; }

    /* Estilo dos pontos FRP */
    .frp-container { display: flex; gap: 20px; }
    .frp-item { text-align: right; }
    .frp-label { font-size: 10px; color: #666; display: block; }
    .frp-value { font-size: 18px; font-weight: bold; }

    /* Cores de Variação */
    .positive { color: #00ff00 !important; }
    .negative { color: #ff0000 !important; }

    /* Caixa de Alvo (Spread) */
    .alvo-box {
        background-color: #0c0c0c;
        border: 1px solid #333;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 10px solid #ffb900;
    }

    .alvo-label { font-size: 12px; color: #aaa; margin-bottom: 5px; }
    .alvo-price { font-size: 36px; color: #ffb900; font-weight: bold; }

    </style>
    """, unsafe_allow_html=True)

# 4. Sidebar
with st.sidebar:
    st.markdown("### PARAMETERS")
    val_ajuste_manual = st.number_input("AJUSTE DOL (MANUAL)", value=5.3900, format="%.4f")
    st.divider()
    v_min = st.number_input("PTS MIN", value=22.0)
    v_justo = st.number_input("PTS JUSTO", value=31.0)
    v_max = st.number_input("PTS MAX", value=42.0)
    if st.button("RESET TRAVA 16H"): st.session_state.spot_ref_locked = None

def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except:
        return pd.DataFrame()

# 5. Renderização
placeholder = st.empty()
with placeholder.container():
    # Header Branco
    st.markdown('<div class="terminal-header"><div class="terminal-title">TERMINAL DE CÂMBIO</div></div>', unsafe_allow_html=True)

    spot_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    now_br = datetime.now() - timedelta(hours=3)
    hora_br = now_br.strftime("%H:%M:%S")
    is_pre_market = now_br.time() < datetime.strptime("11:30", "%H:%M").time()

    if not spot_df.empty:
        spot_at = float(spot_df['Close'].iloc[-1])
        
        # Trava 16h
        try:
            lock_data = spot_df.between_time('15:58', '16:02')
            if not lock_data.empty and st.session_state.spot_ref_locked is None:
                st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
        except: pass
        trava_16h = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

        # Dados Ativos
        v_dxy = 0.0
        d_price = 0.0
        if not dxy_df.empty:
            d_price = float(dxy_df['Close'].iloc[-1])
            v_dxy = ((d_price - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0])) * 100
        
        v_ewz = 0.0
        e_price = 0.0
        if not ewz_df.empty:
            e_price = float(ewz_df['Close'].iloc[-1])
            ref_ewz = float(ewz_df['Close'].iloc[0]) if is_pre_market else float(ewz_df['Open'].iloc[0])
            v_ewz = ((e_price - ref_ewz) / ref_ewz) * 100

        # Spread
        spread_total = v_dxy - v_ewz
        alvo_calc = val_ajuste_manual * (1 + (spread_total / 100))

        # --- EXIBIÇÃO ---

        # ALVO SPREAD
        st.markdown(f"""
            <div class="alvo-box">
                <div class="alvo-label">ALVO SPREAD (AJUSTE + {spread_total:+.2f}%)</div>
                <div class="alvo-price">{alvo_calc:.4f}</div>
            </div>
        """, unsafe_allow_html=True)

        # SPOT + FRP
        v_spot_aj = ((spot_at - val_ajuste_manual) / val_ajuste_manual) * 100
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">USD/BRL SPOT</div>
                <div class="ticker-price">{spot_at:.4f}</div>
                <div class="ticker-var {'positive' if v_spot_aj >= 0 else 'negative'}">{v_spot_aj:+.2f}%</div>
                <div class="frp-container">
                    <div class="frp-item"><span class="frp-label">MIN</span><span class="frp-value negative">{spot_at + (v_min/1000):.4f}</span></div>
                    <div class="frp-item"><span class="frp-label">JUSTO</span><span class="frp-value" style="color:#0080ff;">{spot_at + (v_justo/1000):.4f}</span></div>
                    <div class="frp-item"><span class="frp-label">MAX</span><span class="frp-value positive">{spot_at + (v_max/1000):.4f}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # DXY
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">DXY INDEX</div>
                <div class="ticker-price">{d_price:.2f}</div>
                <div class="ticker-var {'positive' if v_dxy >= 0 else 'negative'}">{v_dxy:+.2f}%</div>
                <div style="width:350px;"></div>
            </div>
        """, unsafe_allow_html=True)

        # EWZ
        st.markdown(f"""
            <div class="ticker-row" style="background-color: {'#001a33' if is_pre_market else '#000'}">
                <div class="ticker-name">EWZ {'(PRE-MKT)' if is_pre_market else '(REGULAR)'}</div>
                <div class="ticker-price">{e_price:.2f}</div>
                <div class="ticker-var {'positive' if v_ewz >= 0 else 'negative'}">{v_ewz:+.2f}%</div>
                <div style="width:350px; text-align:right; font-size:10px; color:#555;">REF: {'YESTERDAY' if is_pre_market else 'OPENING'}</div>
            </div>
        """, unsafe_allow_html=True)

        # TRAVA
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">TRAVA 16H</div>
                <div class="ticker-price" style="color:#555;">{trava_16h:.4f}</div>
                <div class="ticker-var" style="color:#444;">LOCKED</div>
                <div style="width:350px;"></div>
            </div>
        """, unsafe_allow_html=True)

        st.caption(f"UPDATE: {hora_br} BRT")

time.sleep(2)
st.rerun()
