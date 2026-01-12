import streamlit as st
import yfinance as yf
import time

# 1. SETUP
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

# 3. CSS - FONTE CHAKRA PETCH (QUADRADA E NÍTIDA) + TICKER INFINITO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton, [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding-top: 0rem !important; max-width: 100% !important; }

    /* CABEÇALHO */
    .terminal-title-section { text-align: center; padding: 25px 0 5px 0; border-bottom: 1px solid rgba(255,255,255,0.2); }
    .header-title { color: #555; font-size: 14px; letter-spacing: 4px; }
    .bold-white { color: #fff; font-weight: 900; }
    
    /* STATUS */
    .status-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .status-text { font-size: 13px; font-weight: 700; letter-spacing: 2px; }

    /* DADOS - FONTE CHAKRA (NÍTIDA E QUADRADA) */
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 25px 15px; border-bottom: 1px solid #111; }
    .data-label { font-size: 10px; color: #666; width: 40%; }
    .data-value { font-size: 32px; width: 60%; text-align: right; font-family: 'Chakra Petch', sans-serif; font-weight: 700; color: #fff; }
    
    .sub-grid { display: flex; gap: 10px; justify-content: flex-end; width: 60%; }
    .sub-label { font-size: 8px; color: #444; display: block; }
    .sub-val { font-size: 19px; font-family: 'Chakra Petch', sans-serif; font-weight: 700; }

    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    
    /* RODAPÉ E TICKER INFINITO */
    .footer-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 85px; 
        background: #050505; border-top: 1px solid #222; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999;
    }
    .footer-arrows { font-size: 18px; margin-bottom: 5px; }
    
    .ticker-wrap { width: 100%; overflow: hidden; white-space: nowrap; position: relative; }
    .ticker-move { display: inline-block; white-space: nowrap; animation: marquee 20s linear infinite; }
    
    .t-item { padding-right: 100px; display: inline-block; font-family: 'Chakra Petch', sans-serif; font-size: 14px; }
    .t-name { color: #fff; font-weight: bold; }
    .t-up { color: #00aa55; }
    .t-down { color: #aa3333; }

    @keyframes marquee {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
</style>
""", unsafe_allow_html=True)

# 4. LÓGICA DE DADOS
def get_market_data():
    try:
        t_list = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X"]
        d = {}
        for t in t_list:
            tk = yf.Ticker(t); info = tk.fast_info
            d[t] = {"p": info['last_price'], "v": ((info['last_price'] - info['previous_close']) / info['previous_close']) * 100}
        return d, d["DX-Y.NYB"]["v"] - d["EWZ"]["v"]
    except: return None, 0.0

placeholder = st.empty()

while True:
    m, spr = get_market_data()
    if m:
        s_p = m["BRL=X"]["p"]
        p_jus = round((s_p + 0.0310) * 2000) / 2000
        diff = s_p - p_jus
        
        if diff < -0.0015:
            st_msg, st_clr, st_arrow = "● DOLAR BARATO", "#aa3333", "▼ ▼ ▼ ▼ ▼"
        elif diff > 0.0015:
            st_msg, st_clr, st_arrow = "● DOLAR CARO", "#00aa55", "▲ ▲ ▲ ▲ ▲"
        else:
            st_msg, st_clr, st_arrow = "● DOLAR NEUTRO", "#aaaa00", "— — — — —"

        with placeholder.container():
            st.markdown(f'<div class="terminal-title-section"><div class="header-title">TERMINAL <span class="bold-white">DOLAR</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="status-container" style="border-bottom: 2px solid {st_clr}66"><div class="status-text" style="color:{st_clr}">{st_msg}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{(params["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MIN</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="
