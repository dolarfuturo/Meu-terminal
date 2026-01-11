import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO E ACESSO
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

# SENHAS
SENHA_ADMIN = "admin123"
SENHA_CLIENTE = "cliente123"

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.perfil = None

if not st.session_state.autenticado:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    st.title("🔒 ACESSO AO TERMINAL")
    senha = st.text_input("INSIRA SUA CHAVE:", type="password")
    if st.button("ENTRAR"):
        if senha == SENHA_ADMIN:
            st.session_state.autenticado = True
            st.session_state.perfil = "admin"
            st.rerun()
        elif senha == SENHA_CLIENTE:
            st.session_state.autenticado = True
            st.session_state.perfil = "cliente"
            st.rerun()
        else:
            st.error("CHAVE INVÁLIDA")
    st.stop()

if 'v_ajuste' not in st.session_state: st.session_state.v_ajuste = 5.4000
if 'ref_base' not in st.session_state: st.session_state.ref_base = 5.4000

# 2. ESTILO CSS (CORRIGIDO PARA EVITAR ERROS DE STRING)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700;800&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 0.5rem !important; max-width: 850px !important; margin: auto; padding-bottom: 80px; }
    [data-testid="stPopover"] { position: fixed; top: 10px; right: 10px; opacity: 0; transition: opacity 0.3s; z-index: 10000; }
    [data-testid="stPopover"]:hover { opacity: 0.2; }
    .terminal-header { text-align: center; font-size: 14px; letter-spacing: 8px; color: #333; border-bottom: 1px solid #111; padding-bottom: 10px; margin-bottom: 20px; }
    .dolar-strong { color: #FFFFFF; font-weight: 800; }
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 0; border-bottom: 1px solid #111; }
    .data-label { font-size: 11px; color: #FFFFFF; font-weight: 700; letter-spacing: 2px; width: 35%; }
    .data-value { font-size: 32px; font-weight: 700; width: 65%; text-align: right; }
    .sub-grid { display: flex; gap: 25px; justify-content: flex-end; width: 65%; }
    .sub-item { text-align: right; min-width: 105px; }
    .sub-label { font-size: 9px; color: #444; display: block; margin-bottom: 4px; font-weight: 700; }
    .sub-val { font-size: 24px; font-weight: 700; }
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    .footer-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 40px; background: #080808; border-top: 1px solid #222; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; font-size: 11px; z-index: 9999; }
    .ticker-wrap { flex-grow: 1; overflow: hidden; white-space: nowrap; margin: 0 30px; }
    .ticker { display: inline-block; animation: marquee 35s linear infinite; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-250%); } }
    .up { color: #00FF80; } .down { color: #FF4B4B; }
    .pulse { animation: pulse-green 2s infinite; color: #00FF80; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. POPOVER (ADMIN APENAS)
if st.session_state.perfil == "admin":
    with st.popover(" "):
        st.session_state.v_ajuste = st.number_input("AJUSTE", value=st.session_state.v_ajuste, format="%.4f")
        st.session_state.ref_base = st.number_input("REFERENCIAL", value=st.session_state.ref_base, format="%.4f")

def round_to_half_tick(price):
    return round(price * 2000) / 2000

def get_market_data():
    try:
        tkrs = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X", "USDJPY=X"]
        data = {}
        for t in tkrs:
            tk = yf.Ticker(t)
            inf = tk.fast_info
            p = inf['last_price']
            v = ((p - inf['previous_close']) / inf['previous_close']) * 100
            data[t] = {"p": p, "v": v}
        spread = data["DX-Y.NYB"]["v"] - data["EWZ"]["v"]
        return data, spread
    except: return None, 0.0

placeholder = st.empty()

while True:
    m, spread = get_market_data()
    if m:
        spot = m["BRL=X"]["p"]
        paridade = st.session_state.v_ajuste * (1 + (spread/100))
        ref = st.session_state.ref_base
        equi = round_to_half_tick(ref + 0.0220)
        f_max, f_jus, f_min = [round_to_half_tick(spot + x) for x in [0.0420, 0.0310, 0.0220]]
        t_max, t_jus, t_min = [round_to_half_tick(ref + x) for x in [0.0420, 0.0310, 0.0220]]

        with placeholder.container():
            st.markdown('<div class="terminal-header">TERMINAL <span class="dolar-strong">DOLAR</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{equi:.4f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f"""<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid">
                <div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{f_min:.4f}</span></div>
                <div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{f_jus:.4f}</span></div>
                <div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{f_max:.4f}</span></div>
            </div></div>""", unsafe_allow_html=True)

            st.markdown(f"""<div class="data-row"><div class="data-label">REFERENCIAL INSTITUCIONAL</div><div class="sub-grid">
                <div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{t_min:.4f}</span></div>
                <div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{t_jus:.4f}</span></div>
                <div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{t_max:.4f}</span></div>
            </div></div>""", unsafe_allow_html=True)

            def f_tk(s, n, d=2):
                v = m[s]['v']
                c = "up" if v > 0 else "down"
                return f"{n}: {m[s]['p']:.{d}f} <span class='{c}'>{v:+.2f}%</span>"

            agora = datetime.now().strftime("%H:%M:%S")
            st.markdown(f'<div class="footer-bar"><div style="min-width: 80px;"><span class="pulse">●</span> LIVE</div><div class="ticker-wrap"><div class="ticker">{f_tk("DX-Y.NYB","DXY")} | {f_tk("EWZ","EWZ")} | {f_tk("EURUSD=X","EURUSD",4)} | {f_tk("USDJPY=X","USDJPY")} | SPREAD: {spread:+.2f}%</div></div><div style="min-width: 80px; text-align: right; color: #444;">{agora}</div></div>', unsafe_allow_html=True)
    time.sleep(2)
