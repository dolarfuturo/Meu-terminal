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

# 2. CSS AJUSTADO: FONTE SHARE TECH MONO E CORES SEMÁFORO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton, 
    [data-testid="stStatusWidget"], #viewer-badge {
        display: none !important; visibility: hidden !important;
    }
    
    .stApp { background-color: #000; color: #fff; font-family: 'Share Tech Mono', monospace !important; }
    .block-container { padding-top: 0rem !important; max-width: 100% !important; }

    .terminal-header { 
        text-align: center; font-size: 14px; letter-spacing: 6px; color: #444; 
        padding: 30px 0 10px 0; border-bottom: 1px solid #111; 
    }
    .bold-white { color: #fff; font-weight: 900; }

    /* CORES DO STATUS */
    .status-badge { text-align: center; font-size: 11px; font-weight: 700; margin-top: 8px; letter-spacing: 2px; }
    .status-verde { color: #00FF80; } /* BARATO */
    .status-vermelho { color: #FF4B4B; } /* CARO */
    .status-cinza { color: #888888; } /* NEUTRO */

    .data-row { 
        display: flex; justify-content: space-between; align-items: center; 
        padding: 35px 15px; border-bottom: 1px solid #111; 
    }
    
    .data-label { font-size: 11px; color: #aaa; width: 45%; }
    .data-value { font-size: 30px; width: 55%; text-align: right; }
    
    .sub-grid { display: flex; gap: 12px; justify-content: flex-end; width: 55%; }
    .sub-label { font-size: 8px; color: #666 !important; display: block; margin-bottom: 5px; }
    .sub-val { font-size: 19px; }
    
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    
    .footer-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 50px; 
        background: #080808; border-top: 1px solid #222; 
        display: flex; align-items: center; justify-content: center; z-index: 9999; 
    }
    .instr-text { font-size: 10px; text-align: center; font-weight: bold; }

    [data-testid="stPopover"] { position: fixed; top: 0; right: 0; opacity: 0; }
</style>
""", unsafe_allow_html=True)

# 3. ADMIN
if st.session_state.perfil == "admin":
    with st.popover(" "):
        novo_aj = st.number_input("AJUSTE", value=params["ajuste"], format="%.4f")
        novo_rf = st.number_input("REFERENCIAL", value=params["ref"], format="%.4f")
        if st.button("SALVAR"):
            params["ajuste"] = novo_aj; params["ref"] = novo_rf
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
        
        # LOGICA DE 3 ESTADOS (CARO, NEUTRO, BARATO)
        diff = s_p - p_justo
        margem_neutra = 0.0015 # Faixa de "respiro" para o Neutro
        
        if diff < -margem_neutra:
            status_html = '<div class="status-badge status-verde">● DÓLAR BARATO</div>'
            rodape_text = '<span style="color:#00FF80">COMPRA: PREÇO ABAIXO DO JUSTO.</span>'
            cor_borda = "#00FF80"
        elif diff > margem_neutra:
            status_html = '<div class="status-badge status-vermelho">● DÓLAR CARO</div>'
            rodape_text = '<span style="color:#FF4B4B">VENDA: PREÇO ACIMA DO JUSTO.</span>'
            cor_borda = "#FF4B4B"
        else:
            status_html = '<div class="status-badge status-cinza">● DÓLAR EM EQUILÍBRIO</div>'
            rodape_text = '<span style="color:#888">AGUARDAR: MERCADO EM ZONA NEUTRA.</span>'
            cor_borda = "#333333"

        with scr.container():
            st.markdown(f'<div class="terminal-header" style="border-bottom: 2px solid {cor_borda}">TERMINAL <span class="bold-white">DOLAR</span>{status_html}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{(v_aj*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((r_f+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{p_justo:.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="data-row"><div class="data-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((r_f+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{(round((r_f+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((r_f+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="footer-bar"><div class="instr-text">{rodape_text}</div></div>', unsafe_allow_html=True)
    time.sleep(2)
