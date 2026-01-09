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
    .asset-row { display: flex; gap: 20px; margin-bottom: 4px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 130px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    
    .pre-row { display: flex; gap: 20px; margin-bottom: 12px; align-items: center; margin-left: 20px; }
    .pre-name { width: 140px; font-size: 12px; color: #FFB900; font-weight: bold; }
    .pre-price { width: 130px; font-size: 14px; color: #BBB; }
    .pre-var { font-size: 14px; font-weight: bold; }

    .price-paridade { color: #FFB900 !important; }
    .price-ptax { color: #00FFFF !important; }
    .frp-box { margin-left: 180px; margin-top: -5px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 2px; }
    .frp-item { display: flex; gap: 25px; font-size: 13px; }
    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. INTERFACE E VARIÁVEIS
st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

with st.popover("⚙️ AJUSTAR VARIÁVEIS"):
    v_aj = st.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_ptax_m = st.number_input("PTAX", value=5.3850, format="%.4f")
    st.divider()
    v_max_pts = st.number_input("PTS MAX", value=42.0)
    v_jus_pts = st.number_input("PTS JUS", value=31.0)
    v_min_pts = st.number_input("PTS MIN", value=22.0)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        f = t.fast_info
        return {"last": f.last_price, "prev": f.previous_close}
    except:
        return {"last": 0, "prev": 0}

# 4. LOOP DE ATUALIZAÇÃO (AUTOMÁTICO 2S)
placeholder = st.empty()

while True:
    # Horário de Brasília: Pré-market até 11:30
    is_pre = datetime.now().time() < datetime.strptime("11:30", "%H:%M").time()

    with placeholder.container():
        # Busca Spot USD/BRL
        s_df = yf.download("BRL=X", period="1d", interval="1m", progress=False)
        
        if s_df is not None and not s_df.empty:
            s_at = float(s_df['Close'].iloc[-1])
            d_m = get_data("DX-Y.NYB")
            e_m = get_data("EWZ")

            # Cálculos de Variação
            d_v = ((d_m["last"] - d_m["prev"]) / d_m["prev"] * 100) if d_m["prev"] != 0 else 0
            e_v = ((e_m["last"] - e_m["prev"]) / e_m["prev"] * 100) if e_m["prev"] != 0 else 0
            
            sprd = d_v - e_v
            pari = v_aj * (1 + (sprd/100))
            v_s = ((s_at - v_aj) / v_aj * 100)

            # --- EXIBIÇÃO ---
            
            # 1. PARIDADE
            st.markdown(f'<div class="asset-row"><div class="name">PARIDADE</div><div class="price price-paridade">{pari:.4f}</div><div class="var {"pos" if sprd >= 0 else "neg"}">{sprd:+.2f}%</div></div>', unsafe_allow_html=True)
            
            # 2. USD/BRL SPOT
            st.markdown(f'<div class="asset-row"><div class="name">USD/BRL SPOT</div><div class="price">{s_at:.4f}</div><div class="var {"pos" if v_s >= 0 else "neg"}">{v_s:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(s_at+(v_max_pts/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(s_at+(v_jus_pts/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(s_at+(v_min_pts/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            # 3. PTAX
            st.markdown(f'<div class="asset-row"><div class="name">PTAX</div><div class="price price-ptax">{v_ptax_m:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(v_ptax_m+(v_max_pts/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(v_ptax_m+(v_jus_pts/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(v_ptax_m+(v_min_pts/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            # 4. DXY INDEX
            st.markdown(f'<div class="asset-row"><div class="name">DXY INDEX</div><div class="price">{d_m["last"]:.2f}</div><div class="var {"pos" if d_v >= 0 else "neg"}">{d_v:+.2f}%</div></div>', unsafe_allow_html=True)
            
            # 5. EWZ ADR + PRE-MARKET (Onde estava sumindo)
            if is_pre:
                # Exibe fechamento anterior na linha principal
                st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_m["prev"]:.2f}</div><div class="var" style="color:#333">0.00%</div></div>', unsafe_allow_html=True)
                # Exibe Pré-Market na linha debaixo
                st.markdown(f'<div class="pre-row"><div class="pre-name">∟ PRE-MARKET</div><div class="pre-price">{e_m["last"]:.2f}</div><div class="pre-var {"pos" if e_v >= 0 else "neg"}">{e_v:+.2f}%</div></div>', unsafe_allow_html=True)
            else:
                # Após 11:30 exibe preço real
                st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_m["last"]:.2f}</div><div class="var {"pos" if e_v >= 0 else "neg"}">{e_v:+.2f}%</div></div>', unsafe_allow_html=True)

            # 6. TRAVA 16H
            st.markdown(f'<div class="trava-orange">TRAVA 16H: {s_at:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
