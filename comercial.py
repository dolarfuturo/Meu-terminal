import streamlit as st
import yfinance as yf
import time

# 1. SETUP
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL (Sincroniza entre todos os terminais no servidor)
@st.cache_resource
def get_global_vars():
    return {"ajuste": 5.4000, "ref": 5.4000}

v_global = get_global_vars()

# 3. LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_type = None

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:white; text-align:center; padding-top:50px;'>ACESSO RESTRITO</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        senha = st.text_input("CHAVE:", type="password")
        if st.button("LOGAR"):
            if senha == "admin123":
                st.session_state.auth = True
                st.session_state.user_type = "ADM"
                st.rerun()
            elif senha == "trader123":
                st.session_state.auth = True
                st.session_state.user_type = "USER"
                st.rerun()
    st.stop()

# 4. CSS DO TERMINAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    
    /* LIMPEZA TOTAL */
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"] { display: none !important; }

    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }

    /* ESTILO DAS LINHAS */
    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); position: relative; }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 12px; font-weight: 700; letter-spacing: 2px; }

    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 22px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .sub-grid { display: flex; gap: 12px; justify-content: flex-end; }
    .sub-l { font-size: 8px; color: #FFFFFF; display: block; }
    .sub-v { font-size: 17px; font-family: 'Chakra Petch'; font-weight: 700; }

    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 80px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .f-arrows { font-size: 16px; margin-bottom: 4px; letter-spacing: 5px; }
    
    /* AJUSTE DOS INPUTS DE ADM PARA NÃO QUEBRAR O LAYOUT */
    .adm-panel { background: #111; padding: 15px; border-bottom: 2px solid #cc9900; }
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE DADOS
def get_market():
    try:
        tkrs = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X"]
        d = {}
        for t in tkrs:
            tick = yf.Ticker(t)
            inf = tick.fast_info
            d[t] = {"p": inf['last_price'], "v": ((inf['last_price'] - inf['previous_close']) / inf['previous_close']) * 100}
        return d, d["DX-Y.NYB"]["v"] - d["EWZ"]["v"]
    except: return None, 0.0

# 6. INTERFACE DINÂMICA
main_area = st.empty()

while True:
    m, spr = get_market()
    if m:
        spot = m["BRL=X"]["p"]
        justo = round((spot + 0.0310) * 2000) / 2000
        diff = spot - justo
        
        if diff < -0.0015: msg, clr, arr = "● DOLAR BARATO", "#aa3333", "▼ ▼ ▼ ▼ ▼"
        elif diff > 0.0015: msg, clr, arr = "● DOLAR CARO", "#00aa55", "▲ ▲ ▲ ▲ ▲"
        else: msg, clr, arr = "● DOLAR NEUTRO", "#aaaa00", "— — — — —"

        with main_area.container():
            # BOTÃO DE ACESSO NO TOPO (EXCLUSIVO ADM)
            if st.session_state.user_type == "ADM":
                with st.expander("⚙️ CLIQUE PARA AJUSTAR VARIÁVEIS (ADM)"):
                    c1, c2 = st.columns(2)
                    v_global["ajuste"] = c1.number_input("PARIDADE:", value=v_global["ajuste"], format="%.4f", step=0.0001)
                    v_global["ref"] = c2.number_input("REFERÊNCIA:", value=v_global["ref"], format="%.4f", step=0.0001)
                    st.caption("Alterações refletem instantaneamente para todos os usuários.")

            # LAYOUT DO TERMINAL
            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {clr}77"><div class="s-text" style="color:{clr}">{msg}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{(v_global["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value c-equi">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{justo:.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row" style="border-bottom:none;"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{(round((v_global["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((v_global["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # TICKER RODAPÉ
            def f_tk(tk, n):
                v = m[tk]['v']; c = "#00aa55" if v >= 0 else "#aa3333"
                return f"<span style='margin-right:40px;'><b>{n} {m[tk]['p']:.2f}</b> <span style='color:{c}'>({v:+.2f}%)</span></span>"
            
            ticker_html = f"{f_tk('DX-Y.NYB','DXY')} {f_tk('EWZ','EWZ')} {f_tk('EURUSD=X','EUR/USD')} <b>SPREAD {spr:+.2f}%</b>"
            st.markdown(f'<div class="f-bar"><div class="f-arrows" style="color:{clr}">{arr}</div><div style="font-size:12px; font-family:Chakra Petch; white-space:nowrap;">{ticker_html}</div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
