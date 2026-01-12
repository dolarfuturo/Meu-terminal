import streamlit as st
import yfinance as yf
import time

# 1. SETUP INICIAL
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL (SINCRONIZAÇÃO ENTRE TODOS OS DISPOSITIVOS)
@st.cache_resource
def get_shared_state():
    return {"ajuste": 5.4000, "ref": 5.4000}

v_global = get_shared_state()

# 3. GESTÃO DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_type = None

# TELA DE LOGIN
if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:white; text-align:center; padding-top:50px;'>TERMINAL PRIVADO</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        senha = st.text_input("CHAVE DE ACESSO:", type="password", key="main_login")
        if st.button("ACESSAR SISTEMA"):
            if senha == "admin123":
                st.session_state.auth = True
                st.session_state.user_type = "ADM"
                st.rerun()
            elif senha == "trader123":
                st.session_state.auth = True
                st.session_state.user_type = "USER"
                st.rerun()
    st.stop()

# 4. BARRA LATERAL (CONTROLADA PELA SETA NO TOPO - SÓ ADM)
if st.session_state.user_type == "ADM":
    with st.sidebar:
        st.header("⚙️ PAINEL MASTER")
        v_global["ajuste"] = st.number_input("PARIDADE (AJUSTE):", value=v_global["ajuste"], format="%.4f", step=0.0001)
        v_global["ref"] = st.number_input("REF. INSTITUCIONAL:", value=v_global["ref"], format="%.4f", step=0.0001)
        st.write("---")
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()
else:
    # ESCONDE A BARRA LATERAL PARA O CLIENTE
    st.markdown("<style>[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)

# 5. CSS DO TERMINAL (LIMPEZA DE ICONES E ESTILO)
# Criamos a string do CSS separada para evitar erros de unterminated string
css_style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    
    /* LIMPEZA DO TOPO */
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer {{ display: none !important; }}
    
    /* MOSTRA A SETA APENAS SE FOR ADM */
    header {{ 
        background: transparent !important; 
        display: {"block" if st.session_state.user_type == "ADM" else "none"} !important; 
    }}

    .stApp {{ background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }}
    .block-container {{ padding: 0rem !important; max-width: 100% !important; }}

    .t-header {{ text-align: center; padding: 25px 0 5px 0; border-bottom: 1px solid rgba(255,255,255,0.15); }}
    .t-title {{ color: #555; font-size: 13px; letter-spacing: 4px; }}
    .t-bold {{ color: #fff; font-weight: 900; }}
    
    .s-container {{ text-align: center; padding: 10px 0; margin-bottom: 5px; }}
    .s-text {{ font-size: 12px; font-weight: 700; letter-spacing: 2px; }}

    .d-row {{ display: flex; justify-content: space-between; align-items: center; padding: 22px 15px; border-bottom: 1px solid #111; }}
    .d-label {{ font-size: 11px; color: #FFFFFF; font-weight: 900; text-transform: uppercase; }}
    .d-value {{ font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }}
    
    .sub-grid {{ display: flex; gap: 12px; justify-content: flex-end; }}
    .sub-l {{ font-size: 8px; color: #FFFFFF; display: block; font-weight: 400; }}
    .sub-v {{ font-size: 17px; font-family: 'Chakra Petch'; font-weight: 700; }}

    .c-pari {{ color: #cc9900; }} .c-equi {{ color: #00cccc; }} .c-max {{ color: #00cc66; }} .c-min {{ color: #cc3333; }} .c-jus {{ color: #0066cc; }}
    
    .f-bar {{ 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 80px; 
        background: #050505; border-top: 1px solid #222; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999;
    }}
    .f-arrows {{ font-size: 16px; margin-bottom: 4px; letter-spacing: 5px; }}
    .tk-wrap {{ width: 100%; overflow: hidden; white-space: nowrap; }}
    .tk-move {{ display: inline-block; white-space: nowrap; animation: slide 25s linear infinite; }}
    .tk-item {{ padding-right: 80px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; }}
    
    @keyframes slide {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# 6. MOTOR DE DADOS
def get_data():
    try:
        tkrs = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X"]
        res = {}
        for t in tkrs:
            ticker = yf.Ticker(t)
            inf = ticker.fast_info
            res[t] = {"p": inf['last_price'], "v": ((inf['last_price'] - inf['previous_close']) / inf['previous_close']) * 100}
        return res, res["DX-Y.NYB"]["v"] - res["EWZ"]["v"]
    except: return None, 0.0

main_display = st.empty()

# LOOP INFINITO
while True:
    m, spr = get_data()
    if m:
        spot = m["BRL=X"]["p"]
        justo = round((spot + 0.0310) * 2000) / 2000
        diff = spot - justo
        
        if diff < -0.0015: msg, clr, arr = "● DOLAR BARATO", "#aa3333", "▼ ▼ ▼ ▼ ▼"
        elif diff > 0.0015: msg, clr, arr = "● DOLAR CARO", "#00aa55", "▲ ▲ ▲ ▲ ▲"
        else: msg, clr, arr = "● DOLAR NEUTRO", "#aaaa00", "— — — — —"

        with main_display.container():
            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {clr}77"><div class="s-text" style="color:{clr}">{msg}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{(v_global["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value c-equi">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{justo:.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row" style="border-bottom:none;"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{(round((v_global["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((v_global["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            def f_tk(tk, name):
                v = m[tk]['v']
                c = "#00aa55" if v >= 0 else "#aa3333"
                return f"<span class='tk-item'><b style='color:#fff'>{name} {m[tk]['p']:.2f}</b> <span style='color:{c}'>({v:+.2f}%)</span></span>"

            cont = f"{f_tk('DX-Y.NYB','DXY')}{f_tk('EWZ','EWZ')}{f_tk('EURUSD=X','EUR/USD')}<span class='tk-item'><b style='color:#fff'>SPREAD</b> <b style='color:#00aa55'>{spr:+.2f}%</b></span>"
            st.markdown(f'<div class="f-bar"><div class="f-arrows" style="color:{clr}">{arr}</div><div class="tk-wrap"><div class="tk-move">{cont}{cont}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
