import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL (Sincroniza ajustes e anotações entre todos os usuários)
@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas": "MURAL DE ANOTAÇÕES: AGUARDANDO ATUALIZAÇÃO..."
    }

v_global = get_global_vars()

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_type = None

if not st.session_state.auth:
    st.markdown("""
    <style>
        .stApp { background-color: #000; }
        [data-testid="stHeader"], label { display: none !important; }
        .stButton button { 
            width: 100%; background-color: #222; color: white; 
            border: 1px solid #444; font-family: sans-serif;
            letter-spacing: 2px; margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:150px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="CHAVE DE ACESSO")
        if st.button("ENTRAR"):
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
    
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { 
        display: none !important; 
    }

    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }

    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 12px; font-weight: 700; letter-spacing: 2px; }

    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 22px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; }
    .sub-l { font-size: 8px; color: #888; display: block; margin-bottom: 2px; font-weight: 400; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }

    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }

    /* RODAPÉ REESTRUTURADO */
    .f-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 140px; 
        background: #050505; border-top: 1px solid #222; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; 
    }
    .f-notes { 
        font-family: 'Chakra Petch'; font-size: 11px; color: #ffff99; 
        margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;
        max-width: 90%; text-align: center; font-weight: 400;
    }
    .f-arrows { font-size: 16px; margin: 5px 0; letter-spacing: 8px; }
    .f-line { width: 85%; height: 1px; background: rgba(255,255,255,0.1); }
    
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }

    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
    .stExpander { background: transparent !important; border: none !important; margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE DADOS
def get_market():
    try:
        br_tz = pytz.timezone('America/Sao_Paulo')
        agora_br = datetime.now(br_tz)
        hora_atual = agora_br.hour
        d = {}

        for t in ["BRL=X", "EURUSD=X"]:
            tick = yf.Ticker(t)
            inf = tick.fast_info
            d[t] = {"p": inf['last_price'], "v": ((inf['last_price'] - inf['previous_close']) / inf['previous_close']) * 100}

        tkrs_ny = {"DX-Y.NYB": "DXY", "EWZ": "EWZ"}
        for t, label in tkrs_ny.items():
            tick = yf.Ticker(t)
            if hora_atual >= 8:
                inf = tick.info
                current_p = inf.get('preMarketPrice') or inf.get('regularMarketPrice') or inf.get('previousClose')
                prev_c = inf.get('regularMarketPreviousClose') or inf.get('previousClose')
            else:
                inf = tick.fast_info
                current_p = inf['last_price']
                prev_c = inf['previous_close']
            
            var_pct = ((current_p - prev_c) / prev_c) * 100 if current_p and prev_c else 0.0
            d
