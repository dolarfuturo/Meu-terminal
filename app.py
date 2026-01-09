import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL", layout="wide")

# 2. ESTILO CSS (FORÇANDO LAYOUT DA LINHA AMARELA)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin: auto; }
    
    .asset-row { display: flex; gap: 20px; margin-bottom: 4px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 130px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    
    /* LINHA AMARELA DO PRÉ-MERCADO */
    .pre-row { 
        display: flex !important; 
        gap: 20px; 
        margin-top: -2px;
        margin-bottom: 12px; 
        align-items: center; 
        margin-left: 25px; 
        padding: 2px 10px;
        border-left: 2px solid #FFB900;
    }
    .pre-name { width: 135px; font-size: 11px; color: #FFB900; font-weight: bold; }
    .pre-price { width: 130px; font-size: 14px; color: #BBB; }
    .pre-var { font-size: 14px; font-weight: bold; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
    .frp-box { margin-left: 180px; margin-top: -5px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 2px; }
    .frp-item { display: flex; gap: 25px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 15px;">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

# 3. INPUTS
with st.popover("⚙️ PARÂMETROS"):
    v_aj = st.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_ptax_m = st.number_input("PTAX", value=5.3850, format="%.4f")
    st.divider()
    v_max_p = st.number_input("PTS MAX", value=42.0)
    v_jus_p = st.number_input("PTS JUS", value=31.0)
    v_min_p = st.number_input("PTS MIN", value=22.0)

# FUNÇÃO DE CAPTURA QUE NÃO TRAVA
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, prepost=True)
        if df.empty: return {"last": 0.0, "prev": 0.0}
        
        # Pega o último preço fechado (last) e o fechamento de ontem (prev)
        last = float(df['Close'].iloc[-1])
        # Para o DXY e EWZ, precisamos do fechamento anterior real para a variação %
        t = yf.Ticker(ticker)
        prev = float(t.fast_info.previous_close)
        return {"last": last, "prev": prev}
    except:
        return {"last": 0.0, "prev": 0.0}

# 4. LOOP PRINCIPAL
placeholder = st.empty()

while True:
    # NY abre 11:30 Brasília. Antes disso é Pre-Market.
    is_pre = datetime.now().hour < 11 or (datetime.now().hour == 11 and datetime.now().minute < 30)

    with placeholder.container():
        # Captura SPOT com proteção contra erro de Series
        s_raw = yf.download("BRL=X", period="1d", interval="1m", progress=False)
        if not s_raw.empty:
            s_at = float(s_raw['Close'].iloc[-1])
            d_m = get_market_data("DX-Y.NYB")
            e_m = get_market_data("EWZ")

            # Cálculos
            dv = ((d_m["last"] - d_m["prev"]) / d_m["prev"] * 100) if d_m["prev"] > 0 else 0
            ev = ((e_m["last"] - e_m["prev"]) / e_m["prev"] * 100) if e_m["prev"] > 0 else 0
            sprd = dv - ev
            pari = v_aj * (1 + (sprd/100))
            v_s = ((s_at - v_aj) / v_aj * 100)

            # PARIDADE E SPOT
            st.markdown(f'<div class="asset-row"><div class="name">PARIDADE</div><div class="price" style="color:#FFB900">{pari:.4f}</div><div class="var {"pos" if sprd >= 0 else "neg"}">{sprd:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="asset-row"><div class="name">USD/BRL SPOT</div><div class="price">{s_at:.4f}</div><div class="var {"pos" if v_s >= 0 else "neg"}">{v_s:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(s_at+(v_max_p/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(s_at+(v_jus_p/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(s_at+(v_min_p/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            # PTAX
            st.markdown(f'<div class="asset-row"><div class="name">PTAX</div><div class="price" style="color:#00FFFF">{v_ptax_m:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(v_ptax_m+(v_max_p/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(v_ptax_m+(v_jus_p/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(v_ptax_m+(v_min_p/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            # DXY
            st.markdown(f'<div class="asset-row"><div class="name">DXY INDEX</div><div class="price">{d_m["last"]:.2f}</div><div class="var {"pos" if dv >= 0 else "neg"}">{dv:+.2f}%</div></div>', unsafe_allow_html=True)
            
            # EWZ + LÓGICA DO PRÉ-MERCADO
            if is_pre:
                # Mostra linha principal travada no fechamento
                st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_m["prev"]:.2f}</div><div class="var" style="color:#444">0.00%</div></div>', unsafe_allow_html=True)
                # Mostra linha amarela oscilando com o valor do Pre-Market
                st.markdown(f'<div class="pre-row"><div class="pre-name">∟ PRE-MARKET</div><div class="pre-price">{e_m["last"]:.2f}</div><div class="pre-var {"pos" if ev >= 0 else "neg"}">{ev:+.2f}%</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_m["last"]:.2f}</div><div class="var {"pos" if ev >= 0 else "neg"}">{ev:+.2f}%</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="trava-orange">TRAVA 16H: {s_at:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
