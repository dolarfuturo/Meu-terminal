import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO DO TERMINAL
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_global_params():
    return {"ajuste": 5.4000, "ref": 5.4000}

params = get_global_params()

# 2. LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    senha = st.text_input("CHAVE:", type="password")
    if st.button("ACESSAR"):
        if senha in ["admin123", "trader123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. CSS - ESTILO INDUSTRIAL QUADRADO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton, [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding-top: 0rem !important; max-width: 100% !important; }

    /* TITULO COM LINHA FINA */
    .t-header { text-align: center; padding: 25px 0 5px 0; border-bottom: 1px solid rgba(255,255,255,0.2); }
    .t-title { color: #666; font-size: 14px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    
    /* STATUS COM PONTO E LINHA COLORIDA */
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 13px; font-weight: 700; letter-spacing: 2px; }

    /* DADOS - FONTE CHAKRA QUADRADA NÍTIDA */
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 25px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 10px; color: #555; width: 40%; }
    .d-value { font-size: 32px; width: 60%; text-align: right; font-family: 'Chakra Petch', sans-serif; font-weight: 700; color: #eee; }
    
    .sub-grid { display: flex; gap: 10px; justify-content: flex-end; width: 60%; }
    .sub-l { font-size: 8px; color: #444; display: block; }
    .sub-v { font-size: 19px; font-family: 'Chakra Petch', sans-serif; font-weight: 700; }

    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    
    /* RODAPÉ: SETAS + TICKER INFINITO */
    .f-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 85px; 
        background: #050505; border-top: 1px solid #222; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999;
    }
    .f-arrows { font-size: 18px; margin-bottom: 5px; letter-spacing: 5px; }
    
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; position: relative; }
    .tk-move { display: inline-block; white-space: nowrap; animation: slide 20s linear infinite; }
    
    .tk-item { padding-right: 80px; display: inline-block; font-family: 'Chakra Petch', sans-serif; font-size: 13px; }
    .tk-n { color: #fff; font-weight: bold; }
    .tk-up { color: #00aa55; }
    .tk-down { color: #aa3333; }

    @keyframes slide {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
</style>
""", unsafe_allow_html=True)

# 4. CAPTURA DE DADOS
def get_data():
    try:
        tkrs = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X"]
        d = {}
        for t in tkrs:
            ticker = yf.Ticker(t)
            px = ticker.fast_info['last_price']
            pc = ticker.fast_info['previous_close']
            d[t] = {"p": px, "v": ((px - pc) / pc) * 100}
        return d, d["DX-Y.NYB"]["v"] - d["EWZ"]["v"]
    except:
        return None, 0.0

# 5. LOOP PRINCIPAL
placeholder = st.empty()

while True:
    m, spr = get_data()
    if m:
        spot = m["BRL=X"]["p"]
        justo = round((spot + 0.0310) * 2000) / 2000
        diff = spot - justo
        
        # CORES FOSCAS (PADRÃO: BARATO=VERMELHO, CARO=VERDE)
        if diff < -0.0015:
            msg, clr, arr = "● DOLAR BARATO", "#aa3333", "▼ ▼ ▼ ▼ ▼"
        elif diff > 0.0015:
            msg, clr, arr = "● DOLAR CARO", "#00aa55", "▲ ▲ ▲ ▲ ▲"
        else:
            msg, clr, arr = "● DOLAR NEUTRO", "#aaaa00", "— — — — —"

        with placeholder.container():
            # TOPO
            st.markdown(f"""
                <div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>
                <div class="s-container" style="border-bottom: 2px solid {clr}99"><div class="s-text" style="color:{clr}">{msg}</div></div>
            """, unsafe_allow_html=True)
            
            # DADOS
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{(params["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILIBRIO</div><div class="d-value c-equi">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="d-row">
                    <div class="d-label">PREÇO JUSTO</div>
                    <div class="sub-grid">
                        <div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((spot+0.0220)*2000)/2000):.4f}</span></div>
                        <div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{justo:.4f}</span></div>
                        <div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((spot+0.0420)*2000)/2000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="d-row" style="border-bottom:none;">
                    <div class="d-label">REF. INSTITUCIONAL</div>
                    <div class="sub-grid">
                        <div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((params["ref"]+0.0220)*2000)/2000):.4f}</span></div>
                        <div class="sub-item"><span class="sub-label">JUS</span><span class="sub-v c-jus">{(round((params["ref"]+0.0310)*2000)/2000):.4f}</span></div>
                        <div class="sub-item"><span class="sub-label">MAX</span><span class="sub-v c-max">{(round((params["ref"]+0.0420)*2000)/2000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # TICKER INFINITO
            def f_tk(tk, n):
                v = m[tk]['v']
                return f"<span class='tk-item'><span class='tk-n'>{n} {m[tk]['p']:.2f}</span> <span class='{'tk-up' if v >= 0 else 'tk-down'}'>({v:+.2f}%)</span></span>"

            conteudo = f"{f_tk('DX-Y.NYB','DXY')}{f_tk('EWZ','EWZ')}{f_tk('EURUSD=X','EUR/USD')}<span class='tk-item'><span class='tk-n'>SPREAD</span> <span class='tk-up'>{spr:+.2f}%</span></span>"
            
            st.markdown(f"""
                <div class="f-bar">
                    <div class="f-arrows" style="color:{clr}">{arr}</div>
                    <div class="tk-wrap"><div class="tk-move">{conteudo}{conteudo}</div></div>
                </div>
            """, unsafe_allow_html=True)
            
    time.sleep(2)
