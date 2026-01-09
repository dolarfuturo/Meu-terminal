import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL", layout="wide")

# 2. CSS - ESTILO TERMINAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin: auto; }
    .main-title { font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 15px; }
    .asset-row { display: flex; gap: 20px; margin-bottom: 4px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 130px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    .pre-row { display: flex; gap: 20px; margin-bottom: 12px; align-items: center; margin-left: 20px; }
    .pre-name { width: 140px; font-size: 12px; color: #FFB900; font-weight: bold; }
    .pre-price { width: 130px; font-size: 14px; color: #BBB; }
    .pre-var { font-size: 14px; font-weight: bold; }
    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
    .stPopover button { background-color: #111 !important; color: #eee !important; border: 1px solid #333 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

# 3. INPUTS
with st.popover("⚙️ AJUSTAR PARÂMETROS"):
    v_aj = st.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_ptax_m = st.number_input("PTAX", value=5.3850, format="%.4f")
    st.divider()
    v_max_pts = st.number_input("PTS MAX", value=42.0)
    v_jus_pts = st.number_input("PTS JUS", value=31.0)
    v_min_pts = st.number_input("PTS MIN", value=22.0)

def get_market_data(ticker):
    try:
        # Busca dados incluindo pre-market (prepost=True)
        data = yf.download(ticker, period="1d", interval="1m", progress=False, prepost=True)
        t = yf.Ticker(ticker)
        prev = t.fast_info.previous_close
        if not data.empty:
            last = data['Close'].iloc[-1]
        else:
            last = prev
        return {"last": last, "prev": prev}
    except:
        return {"last": 0.001, "prev": 0.001}

# 4. LOOP DE ATUALIZAÇÃO AUTOMÁTICA
placeholder = st.empty()

while True:
    # Horário de Brasília (NY abre às 11:30)
    agora = datetime.now()
    is_pre = agora.hour < 11 or (agora.hour == 11 and agora.minute < 30)

    with placeholder.container():
        # Captura de Ativos
        s_df = yf.download("BRL=X", period="1d", interval="1m", progress=False)
        d_m = get_market_data("DX-Y.NYB")
        e_m = get_market_data("EWZ")
        
        if s_df is not None and not s_df.empty:
            s_at = float(s_df['Close'].iloc[-1])
            
            # Cálculos das variações fora do HTML para segurança
            d_v = ((d_m["last"] - d_m["prev"]) / d_m["prev"] * 100)
            e_v = ((e_m["last"] - e_m["prev"]) / e_m["prev"] * 100)
            
            sprd = d_v - e_v
            pari = v_aj * (1 + (sprd/100))
            v_s = ((s_at - v_aj) / v_aj * 100)

            # --- BLOCO 1: PARIDADE ---
            c_pari = "pos" if sprd >= 0 else "neg"
            st.markdown(f'<div class="asset-row"><div class="name">PARIDADE</div><div class="price" style="color:#FFB900">{pari:.4f}</div><div class="var {c_pari}">{sprd:+.2f}%</div></div>', unsafe_allow_html=True)
            
            # --- BLOCO 2: USD/BRL SPOT + PONTOS ---
            c_s = "pos" if v_s >= 0 else "neg"
            st.markdown(f'<div class="asset-row"><div class="name">USD/BRL SPOT</div><div class="price">{s_at:.4f}</div><div class="var {c_s}">{v_s:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(s_at+(v_max_pts/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(s_at+(v_jus_pts/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(s_at+(v_min_pts/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            # --- BLOCO 3: PTAX + PONTOS ---
            st.markdown(f'<div class="asset-row"><div class="name">PTAX</div><div class="price" style="color:#00FFFF">{v_ptax_m:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(v_ptax_m+(v_max_pts/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(v_ptax_m+(v_jus_pts/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(v_ptax_m+(v_min_pts/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            # --- BLOCO 4: DXY ---
            c_dxy = "pos" if d_v >= 0 else "neg"
            st.markdown(f'<div class="asset-row"><div class="name">DXY INDEX</div><div class="price">{d_m["last"]:.2f}</div><div class="var {c_dxy}">{d_v:+.2f}%</div></div>', unsafe_allow_html=True)
            
            # --- BLOCO 5: EWZ + PRÉ-MERCADO ---
            if is_pre:
                st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_m["prev"]:.2f}</div><div class="var" style="color:#333">0.00%</div></div>', unsafe_allow_html=True)
                c_pre = "pos" if e_v >= 0 else "neg"
                st.markdown(f'<div class="pre-row"><div class="pre-name">∟ PRE-MARKET</div><div class="pre-price">{e_m["last"]:.2f}</div><div class="pre-var {c_pre}">{e_v:+.2f}%</div></div>', unsafe_allow_html=True)
            else:
                c_ewz = "pos" if e_v >= 0 else "neg"
                st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_m["last"]:.2f}</div><div class="var {c_ewz}">{e_v:+.2f}%</div></div>', unsafe_allow_html=True)

            # --- BLOCO 6: TRAVA ---
            st.markdown(f'<div class="trava-orange">TRAVA 16H: {s_at:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
