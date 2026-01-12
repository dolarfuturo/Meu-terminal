import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_global_params():
    return {"ajuste": 5.4000, "ref": 5.4000}

params = get_global_params()
SENHA_ADMIN = "admin123"
SENHA_CLIENTE = "trader123"

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.perfil = None

# LOGIN
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

# 2. CSS AJUSTADO: NÚMEROS MENORES, NEGRITO E INDICADOR DISCRETO
st.markdown("""
<style>
    /* REMOVE LOGOS E INTERFACE STREAMLIT */
    [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton, 
    [data-testid="stStatusWidget"], #viewer-badge, header, footer {
        display: none !important; visibility: hidden !important;
    }
    
    .stApp { background-color: #000; color: #fff; font-family: 'Roboto Mono', monospace !important; }
    .block-container { padding-top: 0rem !important; max-width: 100% !important; }

    /* CABEÇALHO COM DOLAR EM NEGRITO */
    .terminal-header { 
        text-align: center; font-size: 12px; letter-spacing: 6px; color: #444; 
        padding: 30px 0 10px 0; border-bottom: 1px solid #111; 
    }
    .bold-white { color: #fff; font-weight: 900; }

    /* INDICADOR CARO/BARATO DISCRETO */
    .status-badge {
        text-align: center; font-size: 9px; font-weight: 700; margin-top: 5px;
        letter-spacing: 2px;
    }
    .badge-barato { color: #00FFFF; opacity: 0.6; }
    .badge-caro { color: #FF4B4B; opacity: 0.6; }

    /* LINHAS EXPANDIDAS MAS COM NÚMEROS MENORES */
    .data-row { 
        display: flex; justify-content: space-between; align-items: center; 
        padding: 35px 15px; border-bottom: 1px solid #111; 
    }
    
    .data-label { font-size: 10px; color: #aaa; font-weight: 700; width: 45%; }
    .data-value { font-size: 32px; font-weight: 700; width: 55%; text-align: right; }
    
    .sub-grid { display: flex; gap: 12px; justify-content: flex-end; width: 55%; }
    .sub-label { font-size: 8px; color: #666 !important; font-weight: 800; display: block; margin-bottom: 5px; }
    .sub-val { font-size: 19px; font-weight: 700; }
    
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    
    .footer-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 40px; 
        background: #080808; border-top: 1px solid #111; 
        display: flex; align-items: center; padding: 0 20px; z-index: 9999; 
    }
    .ticker { white-space: nowrap; font-size: 10px; animation: marquee 30s linear infinite; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-350%); } }

    [data-testid="stPopover"] { position: fixed; top: 0; right: 0; opacity: 0; }
</style>
""", unsafe_allow_html=True)

# 3. ADMIN
if st.session_state.perfil == "admin":
    with st.popover(" "):
        novo_aj = st.number_input("AJUSTE", value=params["ajuste"], format="%.4f")
        novo_rf = st.number_input("REFERENCIAL", value=params["ref"], format="%.4f")
        if st.button("SALVAR"):
            params["ajuste"] = novo_aj
            params["ref"] = novo_rf
            st.rerun()

def get_market_data():
    try:
        t_list = ["BRL=X", "DX-Y.NYB", "EWZ"]
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
        p_justo = round((s_p + 0.0310) * 2000) / 2000
        
        # Lógica Caro/Barato
        if s_p < p_justo:
            status_html = '<div class="status-badge badge-barato">● DESCONTO (BARATO)</div>'
        else:
            status_html = '<div class="status-badge badge-caro">● ÁGIO (CARO)</div>'

        with scr.container():
            st.markdown(f'<div class="terminal-header">TERMINAL <span class="bold-white">DOLAR</span>{status_html}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{(v_aj*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((r_f+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO JUSTO
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{p_justo:.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            
            # REF INSTITUCIONAL
            st.markdown(f'<div class="data-row"><div class="data-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((r_f+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{(round((r_f+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((r_f+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            items = f"SPOT: {s_p:.4f} | DXY: {m['DX-Y.NYB']['p']:.2f} | SPREAD: {spr:+.2f}%"
            st.markdown(f'<div class="footer-bar"><div class="ticker">{items}</div></div>', unsafe_allow_html=True)
    time.sleep(2)
