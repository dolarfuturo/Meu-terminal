import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. SETUP E MEMÓRIA GLOBAL
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_global_params():
    return {"ajuste": 5.4000, "ref": 5.4000}

params = get_global_params()
SENHA_ADMIN = "admin123"
SENHA_CLIENTE = "trader123"

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.perfil = None

# TELA DE LOGIN
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

# 2. CSS AJUSTADO (EXPANSÃO VERTICAL E LIMPEZA DE LOGOS)
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700;800&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    
    /* LIMPEZA TOTAL DE LOGOS E MENUS */
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton { display: none !important; visibility: hidden !important; }
    [data-testid="stStatusWidget"], #viewer-badge, button[title="View source on GitHub"] { display: none !important; }
    
    .stApp { background-color: #000; color: #fff; }
    
    /* EXPANSÃO DO LAYOUT VERTICAL */
    .block-container { 
        padding-top: 0rem !important; 
        max-width: 900px !important; 
        margin: auto; 
        padding-bottom: 100px !important; 
    }
    
    .terminal-header { text-align: center; font-size: 14px; letter-spacing: 8px; color: #222; border-bottom: 1px solid #111; padding: 25px 0; margin-bottom: 10px; }
    
    /* AUMENTO DO ESPAÇAMENTO ENTRE LINHAS (VERTICAL) */
    .data-row { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 28px 10px; /* Aumentado para expandir no celular */
        border-bottom: 1px solid #111; 
    }
    
    .data-label { font-size: 11px; color: #fff; font-weight: 700; letter-spacing: 1px; width: 40%; }
    .data-value { font-size: 34px; font-weight: 700; width: 60%; text-align: right; }
    
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: right; min-width: 80px; }
    .sub-label { font-size: 9px; color: #fff !important; display: block; margin-bottom: 6px; font-weight: 800; }
    .sub-val { font-size: 20px; font-weight: 700; }
    
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    
    /* RODAPÉ FIXO */
    .footer-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 45px; background: #080808; border-top: 1px solid #222; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; font-size: 10px; z-index: 9999; }
    .ticker-wrap { flex-grow: 1; overflow: hidden; white-space: nowrap; margin: 0 20px; }
    .ticker { display: inline-block; animation: marquee 30s linear infinite; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-300%); } }
    
    /* ENGENHAGEM INVISÍVEL */
    [data-testid="stPopover"] { position: fixed; top: 0; right: 0; opacity: 0; z-index: 10000; }
</style>""", unsafe_allow_html=True)

# 3. PAINEL ADMIN
if st.session_state.perfil == "admin":
    with st.popover(" "):
        novo_aj = st.number_input("AJUSTE", value=params["ajuste"], format="%.4f")
        novo_rf = st.number_input("REFERENCIAL", value=params["ref"], format="%.4f")
        if st.button("SALVAR PARA TODOS"):
            params["ajuste"] = novo_aj
            params["ref"] = novo_rf
            st.rerun()

def get_market_data():
    try:
        t_list = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X"]
        d = {}
        for t in t_list:
            tk = yf.Ticker(t); p = tk.fast_info['last_price']
            hist = tk.history(period="2d"); prev = hist['Close'].iloc[-2]
            v = ((p - prev) / prev) * 100
            d[t] = {"p": p, "v": v}
        return d, d["DX-Y.NYB"]["v"] - d["EWZ"]["v"]
    except: return None, 0.0

scr = st.empty()
while True:
    m, spr = get_market_data()
    if m:
        s_p = m["BRL=X"]["p"]; v_aj = params["ajuste"]; r_f = params["ref"]
        with scr.container():
            st.markdown('<div class="terminal-header">TERMINAL DOLAR</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{(v_aj * (1 + (spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((r_f+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO JUSTO
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{(round((s_p+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            
            # REF INSTITUCIONAL (NOME ATUALIZADO)
            st.markdown(f'<div class="data-row"><div class="data-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((r_f+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{(round((r_f+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((r_f+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            def f_c(t, n, d=2):
                v = m[t]['v']; c = "color:#00FF80" if v >= 0 else "color:#FF4B4B"
                return f"{n}: {m[t]['p']:.{d}f} <span style='{c}'>({v:+.2f}%)</span>"

            items = f"{f_c('BRL=X','SPOT',4)} | {f_c('DX-Y.NYB','DXY')} | {f_c('EWZ','EWZ')} | SPREAD: {spr:+.2f}%"
            st.markdown(f'<div class="footer-bar"><div class="ticker-wrap"><div class="ticker">{items}</div></div></div>', unsafe_allow_html=True)
    time.sleep(2)
