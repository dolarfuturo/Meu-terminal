import streamlit as st
import yfinance as yf
import time

# 1. SETUP DO TERMINAL
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_params():
    return {"ajuste": 5.4000, "ref": 5.4000}

p = get_params()

# 2. SISTEMA DE LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    senha = st.text_input("CHAVE DE ACESSO:", type="password")
    if st.button("ACESSAR"):
        if senha in ["admin123", "trader123"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. CSS BLINDADO (ESTILO QUADRADO INDUSTRIAL)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    
    header, footer, [data-testid="stHeader"], [data-testid="stFooter"], .stDeployButton {
        display: none !important;
    }
    
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding-top: 0rem !important; max-width: 100% !important; }

    /* TOPO */
    .header-box { text-align: center; padding: 20px 0 5px 0; border-bottom: 1px solid rgba(255,255,255,0.2); }
    .h-title { color: #666; font-size: 14px; letter-spacing: 4px; text-transform: uppercase; }
    .h-bold { color: #fff; font-weight: 900; }
    
    /* STATUS DINÂMICO */
    .status-area { text-align: center; padding: 12px 0; margin-bottom: 5px; }
    .status-txt { font-size: 13px; font-weight: 700; letter-spacing: 2px; }

    /* GRID DE DADOS PRINCIPAIS */
    .row { display: flex; justify-content: space-between; align-items: center; padding: 25px 15px; border-bottom: 1px solid #111; }
    .label { font-size: 10px; color: #555; width: 40%; font-weight: bold; }
    .value { font-size: 30px; width: 60%; text-align: right; font-family: 'Chakra Petch', sans-serif; font-weight: 700; }
    
    /* SUB-VALORES (MIN/JUSTO/MAX) */
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: right; }
    .sub-l { font-size: 8px; color: #444; display: block; margin-bottom: 2px; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch', sans-serif; font-weight: 700; }

    /* CORES */
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    
    /* RODAPÉ E TICKER INFINITO */
    .footer { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 85px; 
        background: #050505; border-top: 1px solid #222; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999;
    }
    .arrows { font-size: 18px; margin-bottom: 5px; font-weight: 900; }
    
    .ticker-container { width: 100%; overflow: hidden; white-space: nowrap; position: relative; }
    .ticker-track { display: inline-block; white-space: nowrap; animation: move 20s linear infinite; }
    
    .t-unit { padding-right: 80px; display: inline-block; font-family: 'Chakra Petch', sans-serif; font-size: 13px; }
    .t-n { color: #fff; font-weight: bold; }
    .t-u { color: #00aa55; font-weight: bold; }
    .t-d { color: #aa3333; font-weight: bold; }

    @keyframes move {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
</style>
""", unsafe_allow_html=True)

# 4. CAPTURA DE DADOS (YFINANCE)
def fetch_mkt():
    try:
        tkrs = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X"]
        d = {}
        for t in tkrs:
            ticker = yf.Ticker(t)
            price = ticker.fast_info['last_price']
            prev = ticker.fast_info['previous_close']
            var = ((price - prev) / prev) * 100
            d[t] = {"p": price, "v": var}
        spread = d["DX-Y.NYB"]["v"] - d["EWZ"]["v"]
        return d, spread
    except:
        return None, 0.0

# 5. LOOP DE ATUALIZAÇÃO
ui = st.empty()

while True:
    data, spr = fetch_mkt()
    if data:
        spot = data["BRL=X"]["p"]
        justo = round((spot + 0.0310) * 2000) / 2000
        diff = spot - justo
        
        # Lógica de Cores (Seu Padrão)
        if diff < -0.0015:
            m, c, a = "● DOLAR BARATO", "#aa3333", "▼ ▼ ▼ ▼ ▼" # Vermelho
        elif diff > 0.0015:
            m, c, a = "● DOLAR CARO", "#00aa55", "▲ ▲ ▲ ▲ ▲" # Verde
        else:
            m, c, a = "● DOLAR NEUTRO", "#aaaa00", "— — — — —" # Amarelo

        with ui.container():
            # CABEÇALHO
            st.markdown(f"""
                <div class="header-box">
                    <div class="h-title">TERMINAL <span class="h-bold">DOLAR</span></div>
                </div>
                <div class="status
