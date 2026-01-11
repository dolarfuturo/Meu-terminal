import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# 1. SETUP INICIAL
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False
if 'v_aj' not in st.session_state: st.session_state.v_aj = 5.4000
if 'v_rf' not in st.session_state: st.session_state.v_rf = 5.4000
if 'msg' not in st.session_state: st.session_state.msg = "SEM NOTÍCIAS DE IMPACTO NO MOMENTO"

# 2. LOGIN LIMPO
if not st.session_state.auth:
    st.markdown("<style>.stApp{background:#000;}</style>", unsafe_allow_html=True)
    pw = st.text_input("CHAVE:", type="password")
    if st.button("ACESSAR"):
        if pw in ["admin123", "cliente123"]:
            st.session_state.auth = True
            st.session_state.perfil = "admin" if pw == "admin123" else "cli"
            st.rerun()
    st.stop()

# 3. CSS BLINDADO (LINHA ÚNICA PARA EVITAR ERRO)
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700;800&display=swap'); * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; } .stApp { background: #000; color: #fff; } header, [data-testid="stHeader"] { display: none !important; } .block-container { padding: 1rem !important; max-width: 900px !important; margin: auto; } [data-testid="stPopover"] { position: fixed; top: 0; right: 0; opacity: 0; z-index: 99; } .row { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #111; } .lbl { font-size: 11px; font-weight: 800; color: #fff; } .val { font-size: 32px; font-weight: 800; } .grid { display: flex; gap: 20px; } .s-lbl { font-size: 10px; color: #fff; font-weight: 800; display: block; margin-bottom: 2px; } .s-val { font-size: 22px; font-weight: 800; } .bar-bg { width: 100%; height: 4px; background: #111; margin-top: 5px; } .bar-f { height: 100%; transition: 0.5s; } .badge { font-size: 9px; padding: 2px 5px; border-radius: 2px; margin-left: 5px; font-weight: 800; } .ft { position: fixed; bottom: 0; left: 0; width: 100%; background: #080808; padding: 10px; border-top: 1px solid #222; font-size: 10px; text-align: center; z-index: 999; }</style>""", unsafe_allow_html=True)

# 4. PAINEL ADMIN
if st.session_state.perfil == "admin":
    with st.popover(" "):
        st.session_state.v_aj = st.number_input("AJUSTE", value=st.session_state.v_aj, format="%.4f")
        st.session_state.v_rf = st.number_input("REF", value=st.session_state.v_rf, format="%.4f")
        st.session_state.msg = st.text_input("AVISO", value=st.session_state.msg)

def get_data():
    try:
        tkrs = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X", "USDJPY=X"]
        d = {}
        for s in tkrs:
            i = yf.Ticker(s).fast_info
            p = i['last_price']
            v = ((p - i['previous_close']) / i['previous_close']) * 100
            d[s] = {"p": p, "v": v}
        return d, d["DX-Y.NYB"]["v"] - d["EWZ"]["v"]
    except: return None, 0

scr = st.empty()
while True:
    m, spr = get_data()
    if m:
        s_p = m["BRL=X"]["p"]; r_f = st.session_state.v_rf
        jst = (round((s_p + 0.0310) * 2000) / 2000)
        p_v = max(0, min(100, (spr + 2) * 25)); p_c = "#f44" if spr > 0 else "#0f8"
        dif = s_p - jst
        if dif > 0.015: b_t, b_c = "CARO", "#f44"
        elif dif < -0.015: b_t, b_c = "BARATO", "#0f8"
        else: b_t, b_c = "NEUTRO", "#333"

        with scr.container():
            st.markdown(f'<div style="text-align:center; letter-spacing:8px; color:#222; margin-bottom:20px;">TERMINAL <b>DOLAR</b></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="row"><div class="lbl">PRESSÃO GLOBAL</div><div class="val" style="color:#fb0;">{spr:+.2f}%<div class="bar-bg"><div class="bar-f" style="width:{p_v}%; background:{p_c};"></div></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="row"><div class="lbl">SPOT <span class="badge" style="background:{b_c}; color:#fff;">{b_t}</span></div><div class="val">{s_p:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="row"><div class="lbl">EQUILIBRIO</div><div class="val" style="color:#0ff;">{(round((r_f+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="row"><div class="lbl">PREÇO JUSTO</div><div class="grid"><div style="text-align:right;"><span class="s-lbl">MINIMA</span><span class="s-val" style="color:#f44;">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div style="text-align:right;"><span class="s-lbl">JUSTO</span><span class="s-val" style="color:#08f;">{jst:.4f}</span></div><div style="text-align:right;"><span class="s-lbl">MAXIMA</span><span class="s-val" style="color:#0f8;">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="row"><div class="lbl">REF. INST.</div><div class="grid"><div style="text-align:right;"><span class="s-lbl">MINIMA</span><span class="s-val" style="color:#f44;">{(round((r_f+0.0220)*2000)/2000):.4f}</span></div><div style="text-align:right;"><span class="s-lbl">JUSTO</span><span class="s-val" style="color:#08f;">{(round((r_f+0.0310)*2000)/2000):.4f}</span></div><div style="text-align:right;"><span class="s-lbl">MAXIMA</span><span class="s-val" style="color:#0f8;">{(round((r_f+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ft"><div style="color:#fb0; margin-bottom:5px;">⚠️ {st.session_state.msg}</div>LIVE | DXY {m["DX-Y.NYB"]["p"]:.2f} | EWZ {m["EWZ"]["p"]:.2f} | {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    time.sleep(2)
