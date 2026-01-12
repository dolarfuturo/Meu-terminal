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

# 3. CSS TÉCNICO (FONTES RETRO E QUADRADAS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&family=Orbitron:wght@400;900&display=swap');
    
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton, [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding-top: 0rem !important; max-width: 100% !important; }

    /* CABEÇALHO: LINHA MAIS FINA */
    .terminal-title-section { text-align: center; padding: 25px 0 5px 0; border-bottom: 1px solid rgba(255,255,255,0.3); }
    .header-title { color: #666; font-size: 15px; letter-spacing: 4px; font-family: 'Orbitron'; }
    .bold-white { color: #fff; font-weight: 900; }
    
    /* STATUS: MENOS BRILHO (CORES FOSCAS) */
    .status-container { text-align: center; padding: 10px 0; margin-bottom: 10px; }
    .status-text { font-size: 13px; font-weight: 700; letter-spacing: 2px; opacity: 0.8; }

    /* LINHAS DE DADOS - NÚMEROS ESTILO ANTIGO (VT323) */
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 30px 15px; border-bottom: 1px solid #111; }
    .data-label { font-size: 11px; color: #777; width: 40%; font-family: 'Orbitron'; }
    .data-value { font-size: 42px; width: 60%; text-align: right; font-family: 'VT323', monospace; color: #eee; }
    
    .sub-grid { display: flex; gap: 12px; justify-content: flex-end; width: 60%; }
    .sub-label { font-size: 9px; color: #444; display: block; font-family: 'Orbitron'; }
    .sub-val { font-size: 24px; font-family: 'VT323', monospace; }

    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    
    /* RODAPÉ COM MAIS ESPAÇO ENTRE MOEDAS */
    .footer-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 80px; 
        background: #050505; border-top: 1px solid #222; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999;
    }
    .footer-arrows { font-size: 18px; margin-bottom: 8px; opacity: 0.7; }
    .ticker-wrap { width: 100%; overflow: hidden; white-space: nowrap; }
    .ticker { display: inline-block; animation: marquee 35s linear infinite; font-size: 13px; font-family: 'VT323', monospace; }
    
    .t-item { margin-right: 60px; display: inline-block; } /* ESPAÇAMENTO ENTRE MOEDAS */
    .t-name { color: #fff; font-weight: bold; }
    .t-up { color: #00aa55; }
    .t-down { color: #aa3333; }

    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-300%); } }
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
        
        # CORES FOSCAS (BARATO=VERMELHO / CARO=VERDE / NEUTRO=AMARELO)
        if diff < -0.0015:
            st_msg, st_clr, st_arrow = "● DOLAR BARATO", "#aa3333", "▼ ▼ ▼"
        elif diff > 0.0015:
            st_msg, st_clr, st_arrow = "● DOLAR CARO", "#00aa55", "▲ ▲ ▲"
        else:
            st_msg, st_clr, st_arrow = "● DOLAR NEUTRO", "#aaaa00", "— — —"

        with placeholder.container():
            st.markdown(f'<div class="terminal-title-section"><div class="header-title">TERMINAL <span class="bold-white">DOLAR</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="status-container" style="border-bottom: 2px solid {st_clr}66"><div class="status-text" style="color:{st_clr}">{st_msg}</div></div>', unsafe_allow_html=True)
            
            # BLOCOS DE DADOS COM FONTE VT323
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{(params["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MIN</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{p_jus:.4f}</span></div><div class="sub-item"><span class="sub-label">MAX</span><span class="sub-val c-max">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row" style="border-bottom:none;"><div class="data-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MIN</span><span class="sub-val c-min">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUS</span><span class="sub-val c-jus">{(round((params["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAX</span><span class="sub-val c-max">{(round((params["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # TICKER ESPAÇADO
            def f_t(t, n):
                v = m[t]['v']
                c = "t-up" if v >= 0 else "t-down"
                return f"<span class='t-item'><span class='t-name'>{n} {m[t]['p']:.2f}</span> <span class='{c}'>({v:+.2f}%)</span></span>"

            moedas = f"{f_t('DX-Y.NYB','DXY')}{f_t('EWZ','EWZ')}{f_t('EURUSD=X','EUR/USD')}<span class='t-item'><span class='t-name'>SPREAD</span> <span class='t-up'>{spr:+.2f}%</span></span>"
            
            st.markdown(f"""
                <div class="footer-bar">
                    <div class="footer-arrows" style="color:{st_clr}">{st_arrow}</div>
                    <div class="ticker-wrap"><div class="ticker">{moedas}</div></div>
                </div>
            """, unsafe_allow_html=True)
            
    time.sleep(2)
