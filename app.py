import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL", layout="wide")

if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 2. CSS - ESTILO TERMINAL
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 850px !important; margin: auto; }
    .main-title { font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 15px; }
    
    .asset-row { display: flex; gap: 20px; margin-bottom: 8px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 130px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    .pre-tag { font-size: 10px; color: #FFB900; margin-left: 5px; font-weight: bold; }
    
    .price-paridade { color: #FFB900 !important; }
    .price-ptax { color: #00FFFF !important; }
    
    .frp-box { margin-left: 180px; margin-top: -5px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 2px; }
    .frp-item { display: flex; gap: 25px; font-size: 13px; font-weight: 400 !important; }
    
    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
    .stPopover button { background-color: #111 !important; color: #666 !important; border: 1px solid #222 !important; font-size: 10px !important; height: 25px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFACE
st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

with st.popover("⚙️ AJUSTAR PARÂMETROS"):
    val_aj_manual = st.number_input("AJUSTE MANUAL", value=5.3900, format="%.4f", step=0.0001)
    val_ptax_manual = st.number_input("VALOR PTAX", value=5.3850, format="%.4f", step=0.0001)
    st.divider()
    v_max = st.number_input("PTS MÁXIMA", value=42.0)
    v_jus = st.number_input("PTS JUSTO", value=31.0)
    v_min = st.number_input("PTS MÍNIMA", value=22.0)

def get_market_data(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        last_price = info.last_price
        prev_close = info.previous_close
        change_pct = ((last_price - prev_close) / prev_close) * 100
        return last_price, change_pct
    except:
        return 0, 0

# 4. LOOP DE ATUALIZAÇÃO (2 SEGUNDOS)
placeholder = st.empty()

while True:
    # Verifica horário para a tag PRE (Mercado abre às 11:30 Brasília)
    agora = datetime.now().time()
    is_pre_market = agora < datetime.strptime("11:30", "%H:%M").time()

    with placeholder.container():
        spot_data = yf.download("BRL=X", period="1d", interval="1m", progress=False)
        
        if spot_data is not None and not spot_data.empty:
            spot_at = float(spot_data['Close'].iloc[-1])
            
            # Trava 16h
            try:
                lock_data = spot_data.between_time('15:58', '16:02')
                if not lock_data.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
            except: pass
            trava_exibir = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

            # Dados de Mercado
            dxy_p, dxy_v = get_market_data("DX-Y.NYB")
            ewz_p, ewz_v = get_market_data("EWZ")

            spread_calc = dxy_v - ewz_v
            paridade_val = val_aj_manual * (1 + (spread_calc/100))
            var_spot = ((spot_at - val_aj_manual) / val_aj_manual * 100)

            # RENDERIZAÇÃO
            st.markdown(f'<div class="asset-row"><div class="name">PARIDADE</div><div class="price price-paridade">{paridade_val:.4f}</div><div class="var {"pos" if spread_calc >= 0 else "neg"}">{spread_calc:+.2f}%</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="asset-row"><div class="name">USD/BRL SPOT</div><div class="price">{spot_at:.4f}</div><div class="var {"pos" if var_spot >= 0 else "neg"}">{var_spot:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(spot_at+(v_max/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(spot_at+(v_jus/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(spot_at+(v_min/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="asset-row"><div class="name">PTAX</div><div class="price price-ptax">{val_ptax_manual:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(val_ptax_manual+(v_max/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(val_ptax_manual+(v_jus/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(val_ptax_manual+(v_min/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="asset-row"><div class="name">DXY INDEX</div><div class="price">{dxy_p:.2f}</div><div class="var {"pos" if dxy_v >= 0 else "neg"}">{dxy_v:+.2f}%</div></div>', unsafe_allow_html=True)
            
            # Lógica da TAG PRE: Só aparece se for antes das 11:30
            pre_label = '<span class="pre-tag">PRE</span>' if is_pre_market else ''
            st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{ewz_p:.2f}{pre_label}</div><div class="var {"pos" if ewz_v >= 0 else "neg"}">{ewz_v:+.2f}%</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="trava-orange">TRAVA 16H: {trava_exibir:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
