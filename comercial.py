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

# 3. CSS PROFISSIONAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton, [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    .stApp { background-color: #000; color: #fff; font-family: 'Share Tech Mono', monospace !important; }
    .block-container { padding-top: 0rem !important; max-width: 100% !important; }

    /* TOPO AJUSTADO - SEM SEPARAÇÃO EXCESSIVA */
    .terminal-header { text-align: center; padding: 25px 0 10px 0; border-bottom: 1px solid #111; }
    .header-title { color: #555; font-size: 18px; font-weight: 900; letter-spacing: 2px; }
    .bold-white { color: #fff; margin-left: -5px; } /* Ajuste de proximidade */
    
    .status-arrow { font-size: 24px; font-weight: 900; margin-top: 5px; }

    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 35px 15px; border-bottom: 1px solid #111; }
    .data-label { font-size: 11px; color: #aaa; width: 45%; font-weight: bold; }
    .data-value { font-size: 32px; width: 55%; text-align: right; font-weight: bold; }
    
    .sub-grid { display: flex; gap: 12px; justify-content: flex-end; width: 55%; }
    .sub-label { font-size: 8px; color: #666; display: block; margin-bottom: 5px; font-weight: bold; }
    .sub-val { font-size: 19px; font-weight: bold; }

    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    
    /* TICKER RODAPÉ */
    .footer-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 50px; 
        background: #080808; border-top: 1px solid #222; 
        display: flex; align-items: center; justify-content: center; z-index: 9999;
    }
    .ticker-wrap { width: 100%; overflow: hidden; white-space: nowrap; }
    .ticker { display: inline-block; animation: marquee 30s linear infinite; font-size: 12px; }
    
    .t-name { color: #fff; font-weight: 900; } /* Moedas em Branco Negrito */
    .t-up { color: #00FF80; font-weight: bold; }
    .t-down { color: #FF4B4B; font-weight: bold; }

    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-350%); } }
</style>
""", unsafe_allow_html=True)

# 4. LÓGICA DE DADOS
def get_market_data():
    try:
        t_list = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X"]
        d = {}
        for t in t_list:
            tk = yf.Ticker(t); p = tk.fast_info['last_price']
            prev = tk.fast_info['previous_close']
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
        
        # DEFINIÇÃO DE CORES E SETAS
        if diff < -0.0015:
            st_arrow, st_clr = "▼ ▼ ▼", "#00FF80" # Barato
        elif diff > 0.0015:
            st_arrow, st_clr = "▲ ▲ ▲", "#FF4B4B" # Caro
        else:
            st_arrow, st_clr = "— — —", "#888888" # Neutro

        with placeholder.container():
            st.markdown(f"""
                <div class="terminal-header" style="border-bottom: 2px solid {st_clr}">
                    <div class="header-title">TERMINAL<span class="bold-white">DOLAR</span></div>
                    <div class="status-arrow" style="color:{st_clr}">{st_arrow}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # VALORES CENTRAIS
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{(params["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO JUSTO
            st.markdown(f'<div class="data-row"><div class="data-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{p_jus:.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            
            # REF INSTITUCIONAL
            st.markdown(f'<div class="data-row"><div class="data-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{(round((params["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{(round((params["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # TICKER RODAPÉ FORMATADO
            def f_t(t, n):
                v = m[t]['v']
                c_class = "t-up" if v >= 0 else "t-down"
                return f"<span class='t-name'>{n} {m[t]['p']:.2f}</span> <span class='{c_class}'>({v:+.2f}%)</span>"

            moedas = f"{f_t('DX-Y.NYB','DXY')} | {f_t('EWZ','EWZ')} | {f_t('EURUSD=X','EUR/USD')} | SPREAD: <span class='{'t-up' if spr >=0 else 't-down'}'>{spr:+.2f}%</span>"
            
            st.markdown(f"""
                <div class="footer-bar">
                    <div class="ticker-wrap"><div class="ticker">{moedas}</div></div>
                </div>
            """, unsafe_allow_html=True)
            
    time.sleep(2)
