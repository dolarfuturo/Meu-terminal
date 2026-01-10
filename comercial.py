import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMUX DOLAR", layout="wide")

if 'ref_base' not in st.session_state:
    st.session_state.ref_base = 0.0

# 2. ESTILO CSS - FORMATO TERMUX / LINUX CONSOLE
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    
    * { 
        font-family: 'Fira Code', 'Courier New', monospace !important; 
        text-transform: uppercase; 
    }
    
    .stApp { 
        background-color: #0a0a0a; 
        color: #00FF00; 
    }

    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 900px !important; margin: auto; padding-bottom: 80px; }
    
    /* CABEÇALHO ESTILO CONSOLE */
    .terminal-header { 
        color: #00FF00;
        font-size: 14px;
        margin-bottom: 30px;
        border-left: 5px solid #00FF00;
        padding-left: 15px;
        text-align: left;
    }

    /* LINHAS DE DADOS */
    .data-row { 
        display: flex; justify-content: space-between; align-items: center; 
        padding: 15px 0; border-bottom: 1px solid #1a1a1a;
    }
    .data-label { 
        font-size: 13px; color: #00FF00; font-weight: 700; 
    }
    .data-label::before { content: "$ "; color: #888; } /* Prompt de comando */

    .data-value { 
        font-size: 34px; font-weight: 700; text-align: right; color: #00FF00;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
    
    /* SUB-GRIDS */
    .sub-grid { display: flex; gap: 20px; justify-content: flex-end; width: 65%; }
    .sub-item { text-align: right; min-width: 110px; }
    .sub-label { font-size: 10px; color: #008800; display: block; margin-bottom: 2px; }
    .sub-val { font-size: 26px; font-weight: 700; color: #00FF00; }

    /* CORES ESPECÍFICAS (Sutis para não perder o estilo Termux) */
    .c-pari { color: #00FF00 !important; }
    .c-equi { color: #00FF00 !important; border-bottom: 1px dashed #00FF00; }
    .c-max { color: #00FF00 !important; opacity: 0.9; } 
    .c-min { color: #00FF00 !important; opacity: 0.7; } 

    /* RODAPÉ TICKER TERMUX */
    .footer-bar {
        position: fixed; bottom: 0; left: 0; width: 100%; height: 40px;
        background: #000000; border-top: 2px solid #00FF00;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 20px; font-size: 12px; z-index: 9999;
    }
    .ticker-wrap { flex-grow: 1; overflow: hidden; white-space: nowrap; margin: 0 30px; }
    .ticker { display: inline-block; animation: marquee 35s linear infinite; color: #00FF00; }
    @keyframes marquee {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-200%); }
    }
    .pulse { animation: pulse-green 1.5s infinite; color: #00FF00; font-weight: bold; }
    @keyframes pulse-green { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

def round_to_half_tick(price):
    return round(price * 2000) / 2000

# 3. CONTROLES (ESTILO POPUP)
with st.popover("⚙️ [SET_CONFIG]"):
    v_ajuste = st.number_input("AJUSTE ANTERIOR", value=5.4000, format="%.4f")
    st.session_state.ref_base = st.number_input("REFERENCIAL", value=st.session_state.ref_base, format="%.4f")

def get_market_data():
    try:
        tkrs_list = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X", "USDJPY=X", "GBPUSD=X"]
        data = {}
        for t in tkrs_list:
            ticker_obj = yf.Ticker(t)
            info = ticker_obj.fast_info
            last = info.last_price
            prev = info.previous_close
            data[t] = {"p": last, "v": ((last - prev) / prev) * 100}
        spread = data["DX-Y.NYB"]["v"] - data["EWZ"]["v"]
        return data, spread
    except: return None, 0.0

placeholder = st.empty()

while True:
    market, spread = get_market_data()
    if market:
        spot = market["BRL=X"]["p"]
        paridade = v_ajuste * (1 + (spread/100))
        ref = st.session_state.ref_base
        
        # PONTOS
        ponto_equi = round_to_half_tick(ref + 0.0220)
        f_max, f_jus, f_min = [round_to_half_tick(spot + x) for x in [0.0420, 0.0310, 0.0220]]
        t_max, t_jus, t_min = [round_to_half_tick(ref + x) for x in [0.0420, 0.0310, 0.0220]]

        with placeholder.container():
            st.markdown(f'<div class="terminal-header">~/TERMUX/DOLAR_BOT<br>STATUS: ACTIVE<br>LOCAL_TIME: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)

            # PARIDADE
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE_GLOBAL</div><div class="data-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=True)
            
            # EQUILIBRIO
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO_REF</div><div class="data-value c-equi">{ponto_equi:.4f}</div></div>', unsafe_allow_html=True)

            # PREÇO JUSTO
            st.markdown(f"""
            <div class="data-row">
                <div class="data-label">PRECO_JUSTO_SPOT</div>
                <div class="sub-grid">
                    <div class="sub-item"><span class="sub-label">MIN</span><span class="sub-val">{f_min:.4f}</span></div>
                    <div class="sub-item"><span class="sub-label">MID</span><span class="sub-val">{f_jus:.4f}</span></div>
                    <div class="sub-item"><span class="sub-label">MAX</span><span class="sub-val">{f_max:.4f}</span></div>
                </div>
            </div>""", unsafe_allow_html=True)

            # INSTITUCIONAL
            if ref > 0:
                st.markdown(f"""
                <div class="data-row">
                    <div class="data-label">REF_INSTITUCIONAL</div>
                    <div class="sub-grid">
                        <div class="sub-item"><span class="sub-label">MIN</span><span class="sub-val">{t_min:.4f}</span></div>
                        <div class="sub-item"><span class="sub-label">MID</span><span class="sub-val">{t_jus:.4f}</span></div>
                        <div class="sub-item"><span class="sub-label">MAX</span><span class="sub-val">{t_max:.4f}</span></div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # RODAPÉ ESTILO TERMINAL
            agora = datetime.now().strftime("%H:%M:%S")
            st.markdown(f"""
            <div class="footer-bar">
                <div style="min-width: 90px;"><span class="pulse">●</span> RUNNING</div>
                <div class="ticker-wrap">
                    <div class="ticker">
                        DXY: {market['DX-Y.NYB']['p']:.2f} ({market['DX-Y.NYB']['v']:+.2f}%) | 
                        EWZ: {market['EWZ']['p']:.2f} ({market['EWZ']['v']:+.2f}%) | 
                        EUR/USD: {market['EURUSD=X']['p']:.4f} | 
                        JPY/USD: {market['USDJPY=X']['p']:.2f} | 
                        SPREAD: {spread:+.2f}%
                    </div>
                </div>
                <div style="min-width: 90px; text-align: right;">{agora}</div>
            </div>""", unsafe_allow_html=True)

    time.sleep(2)
