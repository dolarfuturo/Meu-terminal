import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

# CONFIGURAÇÃO DE ACESSO - SENHA ATUALIZADA
SENHA_ADMIN = "admin123"
SENHA_CLIENTE = "trader123"

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.perfil = None
if 'v_ajuste' not in st.session_state: st.session_state.v_ajuste = 5.4000
if 'ref_base' not in st.session_state: st.session_state.ref_base = 5.4000

# 2. TELA DE LOGIN
if not st.session_state.autenticado:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    senha = st.text_input("CHAVE DE ACESSO:", type="password")
    if st.button("ACESSAR"):
        if senha == SENHA_ADMIN:
            st.session_state.autenticado = True
            st.session_state.perfil = "admin"
            st.rerun()
        elif senha == SENHA_CLIENTE:
            st.session_state.autenticado = True
            st.session_state.perfil = "cliente"
            st.rerun()
    st.stop()

# 3. CSS (VISUAL PROFISSIONAL)
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700;800&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000; color: #fff; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 0.5rem !important; max-width: 850px !important; margin: auto; padding-bottom: 80px; }
    [data-testid="stPopover"] { position: fixed; top: 10px; right: 10px; opacity: 0; z-index: 10000; }
    .terminal-header { text-align: center; font-size: 14px; letter-spacing: 8px; color: #333; border-bottom: 1px solid #111; padding-bottom: 10px; margin-bottom: 20px; }
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 0; border-bottom: 1px solid #111; }
    .data-label { font-size: 11px; color: #fff; font-weight: 700; letter-spacing: 2px; width: 35%; }
    .data-value { font-size: 32px; font-weight: 700; width: 65%; text-align: right; }
    .sub-grid { display: flex; gap: 25px; justify-content: flex-end; width: 65%; }
    .sub-item { text-align: right; min-width: 105px; }
    .sub-label { font-size: 10px; color: #fff !important; display: block; margin-bottom: 4px; font-weight: 800; }
    .sub-val { font-size: 24px; font-weight: 700; }
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    .footer-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 40px; background: #080808; border-top: 1px solid #222; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; font-size: 11px; z-index: 9999; }
    .ticker-wrap { flex-grow: 1; overflow: hidden; white-space: nowrap; margin: 0 30px; }
    .ticker { display: inline-block; animation: marquee 35s linear infinite; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-250%); } }
    .up { color: #00FF80; font-weight: bold; }
    .down { color: #FF4B4B; font-weight: bold; }
</style>""", unsafe_allow_html=True)

# 4. PAINEL SECRETO (ADMIN)
if st.session_state.perfil == "admin":
    with st.popover(" "):
        st.session_state.v_ajuste = st.number_input("AJUSTE", value=st.session_state.v_ajuste, format="%.4f")
        st.session_state.ref_base = st.number_input("REFERENCIAL", value=st.session_state.ref_base, format="%.4f")

def get_market_data():
    try:
        t_list = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X", "USDJPY=X"]
        d = {}
        for t in t_list:
            tk = yf.Ticker(t); inf = tk.fast_info; p = inf['last_price']
            v = ((p - i['previous_close']) / i['previous_close']) * 100 if 'i' in locals() else 0 # Proteção
            # Recalculo manual da variação para garantir cor correta
            hist = yf.Ticker(t).history(period="2d")
            prev = hist['Close'].iloc[-2]
            v = ((p - prev) / prev) * 100
            d[t] = {"p": p, "v": v}
        return d, d["DX-Y.NYB"]["v"] - d["EWZ"]["v"]
    except: return None, 0.0

scr = st.empty()
while True:
    m, spr = get_market_data()
    if m:
        s_p = m["BRL=X"]["p"]; r_f = st.session_state.ref_base
        with scr.container():
            st.markdown(f'<div class="terminal-header">TERMINAL <span style="color:#fff">DOLAR</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{(st.session_state.v_ajuste * (1 + (spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((r_f+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{(round((s_p+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">REF. INST.</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((r_f+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{(round((r_f+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((r_f+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            def f_c(t, n, d=2):
                v = m[t]['v']
                c = "up" if v >= 0 else "down"
                return f"{n}: {m[t]['p']:.{d}f} <span class='{c}'>({v:+.2f}%)</span>"

            items = f"{f_c('BRL=X','SPOT',4)} | {f_c('DX-Y.NYB','DXY')} | {f_c('EWZ','EWZ')} | SPREAD: <span class='{'up' if spr >=0 else 'down'}'>{spr:+.2f}%</span>"
            st.markdown(f'<div class="footer-bar"><div>LIVE</div><div class="ticker-wrap"><div class="ticker">{items}</div></div><div>{datetime.now().strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)
    time.sleep(2)
