import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL DE CÂMBIO", layout="wide")

# 2. Memória da Sessão
if 'spot_ref_locked' not in st.session_state: st.session_state.spot_ref_locked = None

# 3. Estilo CSS Terminal (Fonte Square/Mono e Título)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    .stApp { 
        background-color: #000000; 
        color: #FFFFFF; 
        font-family: 'Share Tech Mono', monospace; 
    }
    
    .terminal-title {
        font-size: 24px;
        color: #FFB900;
        border-bottom: 2px solid #FFB900;
        margin-bottom: 20px;
        letter-spacing: 2px;
        font-weight: bold;
    }
    
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        border-bottom: 1px solid #222;
        background-color: #080808;
    }
    
    .ticker-name { font-size: 14px; font-weight: bold; color: #888; width: 150px; }
    .ticker-price { font-size: 24px; font-weight: bold; color: #FFB900; width: 150px; text-align: right; }
    .ticker-var { font-size: 18px; width: 100px; text-align: right; font-weight: bold; }
    
    .frp-label { font-size: 10px; color: #555; }
    .frp-value { font-size: 18px; font-weight: bold; margin-left: 15px; }
    
    .positive { color: #00FF00; }
    .negative { color: #FF4B4B; }
    
    .ewz-pre-highlight { background-color: #001a33 !important; }
    
    .alvo-box {
        background-color: #0A0A0A;
        border: 1px solid #333;
        padding: 15px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Sidebar
with st.sidebar:
    st.markdown("### ⚙️ CONFIGURAÇÃO")
    val_ajuste_manual = st.number_input("AJUSTE DOL (MANUAL)", value=5.3900, format="%.4f")
    st.divider()
    v_min = st.number_input("PTS MÍN", value=22.0)
    v_justo = st.number_input("PTS JUSTO", value=31.0)
    v_max = st.number_input("PTS MÁX", value=42.0)
    if st.button("RESET TRAVA 16H"): st.session_state.spot_ref_locked = None

def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 5. Lógica e Renderização
placeholder = st.empty()
with placeholder.container():
    # Título no Topo
    st.markdown('<div class="terminal-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)
    
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

        # DXY & EWZ
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

        # Spread & Alvo
        spread_total = v_dxy - v_ewz
        alvo_calc = val_ajuste_manual * (1 + (spread_total / 100))

        # --- EXIBIÇÃO ---
        
        # PREÇO ALVO
        st.markdown(f"""
            <div class="alvo-box">
                <div style="font-size:12px; color:#888;">ALVO SPREAD (AJUSTE + {spread_total:+.2f}%)</div>
                <div style="font-size:32px; font-weight:bold; color:#FFB900;">{alvo_calc:.4f}</div>
            </div>
        """, unsafe_allow_html=True)

        # TICKER SPOT + FRP
        v_spot_aj = ((spot_at - val_ajuste_manual) / val_ajuste_manual) * 100
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">USD/BRL SPOT</div>
                <div class="ticker-price">{spot_at:.4f}</div>
                <div class="ticker-var {'positive' if v_spot_aj >= 0 else 'negative'}">{v_spot_aj:+.2f}%</div>
                <div style="display:flex;">
                    <div style="text-align:right;"><span class="frp-label">MÍN</span><br><span class="frp-value" style="color:#FF4B4B;">{spot_at + (v_min/1000):.4f}</span></div>
                    <div style="text-align:right;"><span class="frp-label">JUSTO</span><br><span class="frp-value" style="color:#0080FF;">{spot_at + (v_justo/1000):.4f}</span></div>
                    <div style="text-align:right;"><span class="frp-label">MÁX</span><br><span class="frp-value" style="color:#00FF00;">{spot_at + (v_max/1000):.4f}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # TICKER TRAVA
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">TRAVA 16H</div>
                <div class="ticker-price" style="color:#555;">{trava_16h:.4f}</div>
                <div class="ticker-var" style="color:#333;">LOCKED</div>
                <div style="width:200px;"></div>
            </div>
        """, unsafe_allow_html=True)

        # TICKER DXY
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">DXY INDEX</div>
                <div class="ticker-price">{d_price:.2f}</div>
                <div class="ticker-var {'positive' if v_dxy >= 0 else 'negative'}">{v_dxy:+.2f}%</div>
                <div style="width:200px;"></div>
            </div>
        """, unsafe_allow_html=True)

        # TICKER EWZ (Com destaque se for PRE)
        ewz_class = "ewz-pre-highlight" if is_pre_market else ""
        st.markdown(f"""
            <div class="ticker-row {ewz_class}">
                <div class="ticker-name">EWZ {'(PRE)' if is_pre_market else '(REG)'}</div>
                <div class="ticker-price">{e_price:.2f}</div>
                <div class="ticker-var {'positive' if v_ewz >= 0 else 'negative'}">{v_ewz:+.2f}%</div>
                <div style="width:200px; text-align:right; font-size:10px; color:#555;">{ 'GAP ONTEM' if is_pre_market else 'VAR ABERTURA' }</div>
            </div>
        """, unsafe_allow_html=True)

        st.caption(f"SERVER TIME: {hora_br} | DATA SOURCE: YAHOO FINANCE")

time.sleep(2)
st.rerun()
