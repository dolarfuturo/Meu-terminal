import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# 1. CONFIGURAÇÃO INICIAL
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_global_params():
    return {"ajuste": 5.4000, "ref": 5.4000}

params = get_global_params()

# 2. LOGIN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    senha = st.text_input("CHAVE:", type="password")
    if st.button("ACESSAR"):
        if senha in ["admin123", "trader123"]:
            st.session_state.autenticado = True
            st.rerun()
    st.stop()

# 3. CSS CORRIGIDO (FONTE QUADRADA E SEM ERROS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton, [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    .stApp { background-color: #000; color: #fff; font-family: 'Share Tech Mono', monospace !important; }
    .block-container { padding-top: 0rem !important; max-width: 100% !important; }

    .terminal-header { text-align: center; padding: 30px 0 10px 0; border-bottom: 1px solid #111; }
    .bold-white { color: #fff; font-weight: 900; font-size: 16px; letter-spacing: 5px; }
    
    .status-badge { text-align: center; font-size: 11px; font-weight: 700; margin-top: 8px; letter-spacing: 2px; }

    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 35px 15px; border-bottom: 1px solid #111; }
    .data-label { font-size: 11px; color: #aaa; width: 45%; }
    .data-value { font-size: 32px; width: 55%; text-align: right; font-weight: bold; }
    
    .sub-grid { display: flex; gap: 12px; justify-content: flex-end; width: 55%; }
    .sub-label { font-size: 8px; color: #666; display: block; margin-bottom: 5px; }
    .sub-val { font-size: 19px; font-weight: bold; }

    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    
    .footer-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 70px; 
        background: #080808; border-top: 1px solid #222; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999;
    }
    .instr-text { font-size: 10px; font-weight: bold; margin-bottom: 5px; }
    .ticker-wrap { width: 100%; overflow: hidden; white-space: nowrap; }
    .ticker { display: inline-block; animation: marquee 30s linear infinite; font-size: 10px; color: #444; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-350%); } }
</style>
""", unsafe_allow_html=True)

# 4. LÓGICA DE MERCADO
def get_market_data():
    try:
        t_list = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X"]
        d = {}
        for t in t_list:
            tk = yf.Ticker(t); p = tk.fast_info['last_price']
            hist = tk.history(period="2d"); prev = hist['Close'].iloc[-2]
            d[t] = {"p": p, "v": ((p - prev) / prev) * 100}
        return d, d["DX-Y.NYB"]["v"] - d["EWZ"]["v"]
    except: return None, 0.0

placeholder = st.empty()

while True:
    m, spr = get_market_data()
    if m:
        s_p = m["BRL=X"]["p"]
        p_jus = round((s_p + 0.0310) * 2000) / 2000
        diff = s_p - p_jus
        
        # DEFINIÇÃO DE CORES (VERDE BARATO / VERMELHO CARO)
        if diff < -0.0015:
            st_txt, st_clr, rd_txt = "● DÓLAR BARATO", "#00FF80", "COMPRA: PREÇO ABAIXO DO JUSTO"
        elif diff > 0.0015:
            st_txt, st_clr, rd_txt = "● DÓLAR CARO", "#FF4B4B", "VENDA: PREÇO ACIMA DO JUSTO"
        else:
            st_txt, st_clr, rd_txt = "● DÓLAR NEUTRO", "#888888", "AGUARDAR: MERCADO EM EQUILÍBRIO"

        with placeholder.container():
            st.markdown(f'<div class="terminal-header" style="border-bottom: 2px solid {st_clr}">TERMINAL <span class="bold-white">DOLAR</span><div class="status-badge" style="color:{st_clr}">{st_txt}</div></div>', unsafe_allow_html=True)
            
            # DADOS PRINCIPAIS
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{(params["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO JUSTO
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{p_jus:.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            
            # REF INSTITUCIONAL
            st.markdown(f'<div class="data-row"><div class="data-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{(round((params["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((params["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # TICKER RODAPÉ
            def f_c(t, n):
                v = m[t]['v']; c = "color:#00FF80" if v >= 0 else "color:#FF4B4B"
                return f"{n}: {m[t]['p']:.2f} <span style='{c}'>({v:+.2f}%)</span>"

            moedas = f"DXY: {m['DX-Y.NYB']['p']:.2f} | EWZ: {m['EWZ']['p']:.2f} | EUR/USD: {m['EURUSD=X']['p']:.4f} | SPREAD: {spr:+.2f}%"
            st.markdown(f'<div class="footer-bar"><div class="instr-text" style="color:{st_clr}">{rd_txt}</div><div class="ticker-wrap"><div class="ticker">{moedas}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
