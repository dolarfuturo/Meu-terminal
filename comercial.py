import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DE TELA
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

# LOGIN
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

# 2. CSS ULTRA AGRESSIVO - O "EXTERMINADOR" DE LOGOS E EXPANSOR DE TELA
st.markdown("""
<style>
    /* 1. ELIMINA O ÍCONE DO GITHUB E QUALQUER BOTÃO DO STREAMLIT */
    [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton, 
    [data-testid="stStatusWidget"], #viewer-badge, header, footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* 2. EXPANSÃO VERTICAL PARA CELULAR */
    .stApp { 
        background-color: #000; 
        color: #fff; 
    }
    
    .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 5rem !important;
        max-width: 100% !important;
    }

    /* Aumenta o espaçamento entre os blocos de dados */
    [data-testid="stVerticalBlock"] > div {
        direction: ltr;
    }

    /* 3. ESTILO DO TERMINAL */
    .terminal-header { 
        text-align: center; 
        font-size: 14px; 
        letter-spacing: 10px; 
        color: #222; 
        padding: 40px 0 20px 0; 
        border-bottom: 1px solid #111; 
    }
    
    .data-row { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 45px 15px; /* MUITO MAIS ESPAÇO VERTICAL */
        border-bottom: 1px solid #111; 
    }
    
    .data-label { font-size: 12px; color: #fff; font-weight: 700; width: 40%; }
    .data-value { font-size: 42px; font-weight: 800; width: 60%; text-align: right; }
    
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-label { font-size: 10px; color: #fff !important; font-weight: 800; display: block; margin-bottom: 8px; }
    .sub-val { font-size: 22px; font-weight: 700; }
    
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    
    /* RODAPÉ LIMPO */
    .footer-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 50px; 
        background: #080808; border-top: 1px solid #222; 
        display: flex; align-items: center; padding: 0 20px; z-index: 9999; 
    }
    .ticker { display: inline-block; animation: marquee 30s linear infinite; white-space: nowrap; font-size: 12px; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-350%); } }

    /* ESCONDE O POPOVER (ENGENHAGEM) */
    [data-testid="stPopover"] { position: fixed; top: 0; right: 0; opacity: 0; }
</style>
""", unsafe_allow_html=True)

# 3. ADMIN
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
            
            # PARIDADE
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{(v_aj*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            
            # EQUILIBRIO
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((r_f+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO JUSTO
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{(round((s_p+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            
            # REF INSTITUCIONAL
            st.markdown(f'<div class="data-row"><div class="data-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((r_f+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{(round((r_f+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((r_f+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            def f_c(t, n, d=2):
                v = m[t]['v']; c = "color:#00FF80" if v >= 0 else "color:#FF4B4B"
                return f"{n}: {m[t]['p']:.{d}f} <span style='{c}'>({v:+.2f}%)</span>"

            items = f"{f_c('BRL=X','SPOT',4)} | {f_c('DX-Y.NYB','DXY')} | {f_c('EWZ','EWZ')} | SPREAD: {spr:+.2f}%"
            st.markdown(f'<div class="footer-bar"><div class="ticker-wrap"><div class="ticker">{items}</div></div></div>', unsafe_allow_html=True)
    time.sleep(2)
