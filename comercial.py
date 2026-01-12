import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. CONFIGURAÇÃO INICIAL
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

# 2. O "EXTERMINADOR" DE LOGOS (CSS ULTRA AGRESSIVO)
st.markdown("""
<style>
    /* ESCONDE TUDO O QUE É DO STREAMLIT */
    header, footer, .stDeployButton, [data-testid="stHeader"], [data-testid="stFooter"] { 
        display: none !important; 
        visibility: hidden !important; 
    }
    
    /* REMOVE O ÍCONE DO GITHUB (CONTEÚDO ADICIONAL) */
    [data-testid="stStatusWidget"], .st-emotion-cache-zq5wmm, .st-emotion-cache-10trblm {
        display: none !important;
    }
    
    /* TIRA O OVERLAY DO REBOOT E GITHUB NO CANTO INFERIOR */
    div[data-testid="stStatusWidget"] { display: none !important; }
    #viewer-badge { display: none !important; }
    button[title="View source on GitHub"] { display: none !important; }

    /* MAXIMIZA A TELA */
    .stApp { background-color: #000; color: #fff; }
    .block-container { 
        padding: 1rem !important; 
        max-width: 100% !important; 
        margin-top: -60px !important; /* Puxa para cima para tapar o topo */
    }

    /* ENGENHAGEM INVISÍVEL */
    [data-testid="stPopover"] { position: fixed; top: 0; right: 0; opacity: 0; z-index: 10000; }

    /* ESTILO TERMINAL */
    .terminal-header { text-align: center; font-size: 11px; letter-spacing: 5px; color: #222; margin-bottom: 20px; }
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #111; }
    .data-label { font-size: 10px; color: #fff; font-weight: 700; width: 40%; }
    .data-value { font-size: 30px; font-weight: 700; width: 60%; text-align: right; }
    .sub-grid { display: flex; gap: 10px; justify-content: flex-end; width: 60%; }
    .sub-label { font-size: 8px; color: #fff !important; font-weight: 800; display: block; }
    .sub-val { font-size: 18px; font-weight: 700; }
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }

    /* RODAPÉ LIMPO */
    .footer-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 40px; background: #080808; border-top: 1px solid #222; display: flex; align-items: center; padding: 0 15px; font-size: 10px; z-index: 9999; }
    .ticker-wrap { flex-grow: 1; overflow: hidden; white-space: nowrap; }
    .ticker { display: inline-block; animation: marquee 30s linear infinite; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-400%); } }
</style>
""", unsafe_allow_html=True)

# 3. LOGICA DE DADOS E ADMIN
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
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE</div><div class="data-value c-pari">{(v_aj*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((r_f+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">P. JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MIN</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUS</span><span class="sub-val c-jus">{(round((s_p+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAX</span><span class="sub-val c-max">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">REF. INST</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MIN</span><span class="sub-val c-min">{(round((r_f+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUS</span><span class="sub-val c-jus">{(round((r_f+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAX</span><span class="sub-val c-max">{(round((r_f+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            def f_c(t, n, d=2):
                v = m[t]['v']; c = "color:#00FF80" if v >= 0 else "color:#FF4B4B"
                return f"{n}: {m[t]['p']:.{d}f} <span style='{c}'>({v:+.2f}%)</span>"

            items = f"{f_c('BRL=X','SPOT',4)} | {f_c('DX-Y.NYB','DXY')} | {f_c('EWZ','EWZ')} | SPREAD: {spr:+.2f}%"
            st.markdown(f'<div class="footer-bar"><div class="ticker-wrap"><div class="ticker">{items}</div></div></div>', unsafe_allow_html=True)
    time.sleep(2)
