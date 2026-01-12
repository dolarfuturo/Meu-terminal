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

# 3. CSS TÉCNICO (FONTE ORBITRON)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton, [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif !important; }
    .block-container { padding-top: 0rem !important; max-width: 100% !important; }

    /* CABEÇALHO: TERMINAL DOLAR + LINHA NEUTRA */
    .terminal-title-section { text-align: center; padding: 25px 0 5px 0; border-bottom: 2px solid #fff; }
    .header-title { color: #888; font-size: 16px; letter-spacing: 3px; }
    .bold-white { color: #fff; font-weight: 900; }
    
    /* STATUS COM PONTO E LINHA COLORIDA */
    .status-container { text-align: center; padding: 10px 0; margin-bottom: 10px; }
    .status-text { font-size: 14px; font-weight: 900; letter-spacing: 2px; padding-bottom: 5px; }

    /* LINHAS DE DADOS */
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 32px 15px; border-bottom: 1px solid #111; }
    .data-label { font-size: 10px; color: #aaa; width: 40%; font-weight: 700; }
    .data-value { font-size: 34px; width: 60%; text-align: right; font-weight: 900; letter-spacing: -1px; }
    
    .sub-grid { display: flex; gap: 10px; justify-content: flex-end; width: 60%; }
    .sub-label { font-size: 8px; color: #555; display: block; margin-bottom: 3px; font-weight: bold; }
    .sub-val { font-size: 20px; font-weight: 700; }

    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    
    /* RODAPÉ: SETAS ACIMA DO TICKER */
    .footer-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 75px; 
        background: #050505; border-top: 1px solid #333; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999;
    }
    .footer-arrows { font-size: 20px; font-weight: 900; margin-bottom: 5px; }
    .ticker-wrap { width: 100%; overflow: hidden; white-space: nowrap; }
    .ticker { display: inline-block; animation: marquee 25s linear infinite; font-size: 11px; }
    
    .t-name { color: #fff; font-weight: 900; }
    .t-up { color: #00FF80; font-weight: bold; }
    .t-down { color: #FF4B4B; font-weight: bold; }

    @keyframes marquee { 0% { transform: translateX(50%); } 100% { transform: translateX(-200%); } }
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
        
        # DEFINIÇÃO DE CORES (PADRÃO SOLICITADO)
        if diff < -0.0015:
            st_msg, st_clr, st_arrow = "● DOLAR BARATO", "#FF4B4B", "▼ ▼ ▼ ▼ ▼" # Vermelho
        elif diff > 0.0015:
            st_msg, st_clr, st_arrow = "● DOLAR CARO", "#00FF80", "▲ ▲ ▲ ▲ ▲" # Verde
        else:
            st_msg, st_clr, st_arrow = "● DOLAR NEUTRO", "#FFFF00", "— — — — —" # Amarelo

        with placeholder.container():
            # TOPO COM LINHA BRANCA
            st.markdown(f'<div class="terminal-title-section"><div class="header-title">TERMINAL <span class="bold-white">DOLAR</span></div></div>', unsafe_allow_html=True)
            
            # STATUS COM PONTO E LINHA COLORIDA
            st.markdown(f'<div class="status-container" style="border-bottom: 3px solid {st_clr}"><div class="status-text" style="color:{st_clr}">{st_msg}</div></div>', unsafe_allow_html=True)
            
            # DADOS CENTRAIS
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{(params["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MIN</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{p_jus:.4f}</span></div><div class="sub-item"><span class="sub-label">MAX</span><span class="sub-val c-max">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MIN</span><span class="sub-val c-min">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUS</span><span class="sub-val c-jus">{(round((params["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAX</span><span class="sub-val c-max">{(round((params["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # TICKER COM SETAS ACIMA
            def f_t(t, n):
                v = m[t]['v']
                return f"<span class='t-name'>{n} {m[t]['p']:.2f}</span> <span class='{'t-up' if v >= 0 else 't-down'}'>({v:+.2f}%)</span>"

            moedas = f"{f_t('DX-Y.NYB','DXY')} | {f_t('EWZ','EWZ')} | {f_t('EURUSD=X','EUR/USD')} | SPREAD: {spr:+.2f}%"
            
            st.markdown(f"""
                <div class="footer-bar">
                    <div class="footer-arrows" style="color:{st_clr}">{st_arrow}</div>
                    <div class="ticker-wrap"><div class="ticker">{moedas}</div></div>
                </div>
            """, unsafe_allow_html=True)
            
    time.sleep(2)
