import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

# SENHAS
SENHA_ADMIN = "admin123"
SENHA_CLIENTE = "cliente123"

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.perfil = None
if 'v_ajuste' not in st.session_state: st.session_state.v_ajuste = 5.4000
if 'ref_base' not in st.session_state: st.session_state.ref_base = 5.4000
if 'aviso_mercado' not in st.session_state: st.session_state.aviso_mercado = "SEM NOTÍCIAS DE IMPACTO NO MOMENTO"

if not st.session_state.autenticado:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    senha = st.text_input("CHAVE:", type="password")
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

# 2. ESTILO CSS (COM TERMÔMETRO E ALERTAS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700;800&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 0.5rem !important; max-width: 850px !important; margin: auto; padding-bottom: 80px; }
    [data-testid="stPopover"] { position: fixed; top: 10px; right: 10px; opacity: 0; z-index: 10000; }
    
    .status-badge { font-size: 10px; padding: 2px 8px; border-radius: 3px; font-weight: 800; margin-left: 10px; }
    .status-caro { background-color: #FF4B4B; color: white; }
    .status-barato { background-color: #00FF80; color: black; }
    .status-neutro { background-color: #333; color: white; }

    .pressure-bg { width: 100%; height: 4px; background: #111; margin-top: 5px; border-radius: 2px; overflow: hidden; }
    .pressure-fill { height: 100%; transition: width 0.5s ease; }

    .terminal-header { text-align: center; font-size: 14px; letter-spacing: 8px; color: #333; border-bottom: 1px solid #111; padding-bottom: 10px; margin-bottom: 20px; }
    .dolar-strong { color: #FFFFFF; font-weight: 800; }
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 0; border-bottom: 1px solid #111; }
    .data-label { font-size: 11px; color: #FFFFFF; font-weight: 700; letter-spacing: 2px; width: 35%; }
    .data-value { font-size: 32px; font-weight: 700; width: 65%; text-align: right; }
    .sub-grid { display: flex; gap: 25px; justify-content: flex-end; width: 65%; }
    .sub-item { text-align: right; min-width: 105px; }
    .sub-label { font-size: 10px; color: #FFFFFF !important; display: block; margin-bottom: 4px; font-weight: 800; }
    .sub-val { font-size: 24px; font-weight: 700; }
    
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    
    .footer-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 50px; background: #080808; border-top: 1px solid #222; z-index: 9999; padding: 5px 20px; }
    .footer-content { display: flex; justify-content: space-between; align-items: center; font-size: 11px; margin-bottom: 2px; }
    .cal-impact { color: #FFB900; font-weight: 800; font-size: 10px; text-align: center; width: 100%; display: block; }
    
    .ticker-wrap { overflow: hidden; white-space: nowrap; margin: 0 10px; flex-grow: 1; }
    .ticker { display: inline-block; animation: marquee 40s linear infinite; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-250%); } }
</style>
""", unsafe_allow_html=True)

# 3. PAINEL ADMIN
if st.session_state.perfil == "admin":
    with st.popover(" "):
        st.session_state.v_ajuste = st.number_input("AJUSTE", value=st.session_state.v_ajuste, format="%.4f")
        st.session_state.ref_base = st.number_input("REFERENCIAL", value=st.session_state.ref_base, format="%.4f")
        st.session_state.aviso_mercado = st.text_input("AVISO CALENDÁRIO", value=st.session_state.aviso_mercado)

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
        return data, data["DX-Y.NYB"]["v"] - data["EWZ"]["v"]
    except: return None, 0.0

placeholder = st.empty()

while True:
    m, spread = get_market_data()
    if m:
        spot = m["BRL=X"]["p"]
        ref = st.session_state.ref_base
        paridade = st.session_state.v_ajuste * (1 + (spread/100))
        justo = (round((spot + 0.0310) * 2000) / 2000)
        
        # LOGICA CARO/BARATO
        diff = spot - justo
        if diff > 0.015: status_txt, status_cls = "CARO", "status-caro"
        elif diff < -0.015: status_txt, status_cls = "BARATO", "status-barato"
        else: status_txt, status_cls = "NEUTRO", "status-neutro"

        # LOGICA TERMOMETRO (0 a 100%)
        # Normalizando spread de -2% a +2%
        press_val = max(0, min(100, (spread + 2) * 25))
        press_color = "#FF4B4B" if spread > 0 else "#00FF80"

        with placeholder.container():
            st.markdown(f'<div class="terminal-header">TERMINAL <span class="dolar-strong">DOLAR</span></div>', unsafe_allow_html=True)
            
            # LINHA PARIDADE + TERMÔMETRO
            st.markdown(f'''
                <div class="data-row" style="padding-bottom: 5px;">
                    <div class="data-label">PRESSÃO GLOBAL<br><span style="font-size:8px; color:#444;">DXY vs EWZ</span></div>
                    <div class="data-value c-pari" style="font-size:24px;">{spread:+.2f}%
                        <div class="pressure-bg"><div class="pressure-fill" style="width:{press_val}%; background:{press_color};"></div></div>
                    </div>
                </div>''', unsafe_allow_html=True)

            # LINHA PREÇO ATUAL COM ALERTA
            st.markdown(f'''
                <div class="data-row">
                    <div class="data-label">SPOT ATUAL <span class="status-badge {status_cls}">{status_txt}</span></div>
                    <div class="data-value" style="color:#FFF;">{spot:.4f}</div>
                </div>''', unsafe_allow_html=True)

            # PONTOS
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((ref+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{justo:.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="data-row"><div class="data-label">REF. INST.</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class
