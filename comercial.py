import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

if 'ref_base' not in st.session_state:
    st.session_state.ref_base = 0.0

# 2. ESTILO CSS (CORRIGIDO E OTIMIZADO)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 0.5rem !important; max-width: 850px !important; margin: auto; padding-bottom: 80px; }
    
    .terminal-header { 
        text-align: center; font-size: 14px; letter-spacing: 8px; color: #666; 
        border-bottom: 1px solid #222; padding-bottom: 10px; margin-bottom: 20px;
    }
    .terminal-title { color: #FFFFFF; font-weight: 700; }

    .alerta-wrap { display: flex; justify-content: center; height: 35px; margin-bottom: 20px; }
    .status-tag { font-size: 13px; font-weight: bold; letter-spacing: 2px; padding: 5px 25px; border: 1px solid #333; }
    .caro { color: #00FF80; border-color: #00FF80; background: rgba(0, 255, 128, 0.05); }
    .barato { color: #FF4B4B; border-color: #FF4B4B; background: rgba(255, 75, 75, 0.05); }

    .data-row { 
        display: flex; justify-content: space-between; align-items: center; 
        padding: 18px 0; border-bottom: 1px solid #111;
    }
    .data-label { font-size: 11px; color: #FFFFFF; font-weight: 700; letter-spacing: 2px; width: 35%; }
    .data-value { font-size: 32px; font-weight: 700; width: 65%; text-align: right; }
    
    .sub-grid { display: flex; gap: 25px; justify-content: flex-end; width: 65%; }
    .sub-item { text-align: right; min-width: 105px; }
    .sub-label { font-size: 9px; color: #555; display: block; margin-bottom: 4px; font-weight: 700; }
    .sub-val { font-size: 24px; font-weight: 700; }

    .c-pari { color: #FFB900; }
    .c-equi { color: #00FFFF; }
    .c-max { color: #00FF80; } 
    .c-min { color: #FF4B4B; } 
    .c-jus { color: #0080FF; }

    /* RODAPÉ E TICKER ANIMADO */
    .footer-bar {
        position: fixed; bottom: 0; left: 0; width: 100%; height: 40px;
        background: #080808; border-top: 1px solid #333;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 20px; font-size: 11px; z-index: 9999;
    }
    .ticker-wrap { flex-grow: 1; overflow: hidden; white-space: nowrap; margin: 0 30px; }
    .ticker { display: inline-block; animation: marquee 30s linear infinite; }
    @keyframes marquee {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-180%); }
    }
    .up { color: #00FF80; } .down { color: #FF4B4B; }
    .pulse { animation: pulse-green 2s infinite; color: #00FF80; font-weight: bold; }
    @keyframes pulse-green { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# FUNÇÃO DE ARREDONDAMENTO MEIO PONTO (X.XXX0 ou X.XXX5)
def round_to_half_tick(price):
    return round(price * 2000) / 2000

# 3. PAINEL DE CONTROLE
with st.popover("⚙️ CONFIG"):
    v_ajuste = st.number_input("AJUSTE ANTERIOR", value=5.4000, format="%.4f")
    st.session_state.ref_base = st.number_input("REFERENCIAL", value=st.session_state.ref_base, format="%.4f")

def get_market_data():
    try:
        tkrs = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X", "USDJPY=X", "GBPUSD=X"]
        df = yf.download(tkrs, period="2d", interval="1m", progress=False)
        res = {}
        for t in tkrs:
            last = df['Close'][t].iloc[-1]
            prev = yf.Ticker(t).fast_info.previous_close
            res[t] = {"p": last, "v": ((last - prev) / prev) * 100}
        sprd = res["DX-Y.NYB"]["v"] - res["EWZ"]["v"]
        return res, sprd
    except: return None, 0.0

placeholder = st.empty()

while True:
    market, spread = get_market_data()
    if market:
        spot = market["BRL=X"]["p"]
        paridade = v_ajuste * (1 + (spread/100))
        
        # CÁLCULOS (BASE REFERENCIAL)
        ref = st.session_state.ref_base
        ponto_equi = round_to_half_tick(ref + 0.0220)
        
        # JUSTO (SPOT)
        f_max, f_jus, f_min = [round_to_half_tick(spot + x) for x in [0.0420, 0.0310, 0.0220]]
        # INSTITUCIONAL (REF)
        t_max, t_jus, t_min = [round_to_half_tick(ref + x) for x in [0.0420, 0.0310, 0.0220]]

        with placeholder.container():
            st.markdown('<div class="terminal-header">TERMINAL <span class="terminal-title">DOLAR</span></div>', unsafe_allow_html=True)

            # ALERTAS
            st.markdown('<div class="alerta-wrap">', unsafe_allow_html=True)
            if ref > 0:
                if spot >= t_max: st.markdown('<div class="status-tag caro">DOLAR CARO</div>', unsafe_allow_html=True)
                elif spot <= t_min: st.markdown('<div class="status-tag barato">DOLAR BARATO</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # PARIDADE E EQUILIBRIO
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO (REF)</div><div class="data-value c-equi">{ponto_equi:.4f}</div></div>', unsafe_allow_html=True)

            # PREÇO JUSTO
            st.markdown(f"""
            <div class="data-row">
                <div class="data-label">PREÇO JUSTO (SPOT)</div>
                <div class="sub-grid">
                    <div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{f_min:.4f}</span></div>
                    <div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{f_jus:.4f}</span></div>
                    <div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{f_max:.4f}</span></div>
                </div>
            </div>""", unsafe_allow_html=True)

            # INSTITUCIONAL
            if ref > 0:
                st.markdown(f"""
                <div class="data-row">
                    <div class="data-label">REFERENCIAL FIXO</div>
                    <div class="sub-grid">
                        <div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{t_min:.4f}</span></div>
                        <div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{t_jus:.4f}</span></div>
                        <div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{t_max:.4f}</span></div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # RODAPÉ TICKER (DXY, EWZ, EUR, JPY, GBP)
            def tk_fmt(s, n):
                v = market[s]["v"]
                c = "up" if v > 0 else "down"
                return f"{n} {market[s]['p']:.2f} <span class='{c}'>({v:+.2f}%)</span>"

            agora = datetime.now().strftime("%H:%M:%S")
            st.markdown(f"""
            <div class="footer-bar">
                <div style="min-width: 80px;"><span class="pulse">●</span> LIVE</div>
                <div class="ticker-wrap">
                    <div class="ticker">
                        {tk_fmt("DX-Y.NYB","DXY")} &nbsp;&nbsp; | &nbsp;&nbsp; {tk_fmt("EWZ","EWZ")} &nbsp;&nbsp; | &nbsp;&nbsp; 
                        {tk_fmt("EURUSD=X","EUR/USD")} &nbsp;&nbsp; | &nbsp;&nbsp; {tk_fmt("USDJPY=X","USD/JPY")} &nbsp;&nbsp; | &nbsp;&nbsp; 
                        {tk_fmt("GBPUSD=X","GBP/USD")} &nbsp;&nbsp; | &nbsp;&nbsp; VOLATILIDADE SPREAD: {spread:+.2f}%
                    </div>
                </div>
                <div style="min-width: 80px; text-align: right; color: #666;">{agora}</div>
            </div>""", unsafe_allow_html=True)

    time.sleep(2)
