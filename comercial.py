import streamlit as st
import yfinance as yf
import time

# 1. SETUP
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# 2. BANCO DE DADOS EM MEMÓRIA (COMPARTILHADO)
@st.cache_resource
def get_shared_state():
    return {"ajuste": 5.4000, "ref": 5.4000}

v_global = get_shared_state()

# 3. LÓGICA DE LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_type = None

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:white; text-align:center; padding-top:50px;'>SISTEMA PRIVADO</h2>", unsafe_allow_html=True)
    
    # Centralizando o box de login
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        senha = st.text_input("CHAVE DE ACESSO:", type="password")
        if st.button("ENTRAR NO SISTEMA"):
            if senha == "admin123":
                st.session_state.auth = True
                st.session_state.user_type = "ADM"
                st.rerun()
            elif senha == "trader123":
                st.session_state.auth = True
                st.session_state.user_type = "USER"
                st.rerun()
    st.stop()

# 4. BARRA LATERAL (ENGRENAGEM) - SÓ APARECE PARA ADM
if st.session_state.user_type == "ADM":
    with st.sidebar:
        st.header("⚙️ CONFIGURAÇÃO GLOBAL")
        v_global["ajuste"] = st.number_input("PARIDADE (AJUSTE):", value=v_global["ajuste"], format="%.4f", step=0.0001)
        v_global["ref"] = st.number_input("REF. INSTITUCIONAL:", value=v_global["ref"], format="%.4f", step=0.0001)
        st.write("---")
        if st.button("SAIR"):
            st.session_state.auth = False
            st.rerun()
else:
    # ESCONDE A ENGRENAGEM PARA O CLIENTE
    st.markdown("<style>[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)

# 5. CSS DO TERMINAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    
    /* ESCONDE ELEMENTOS MAS MANTÉM A ENGRENAGEM PARA ADM */
    .stAppDeployButton, footer, [data-testid="stToolbar"] { display: none !important; }
    
    /* SE FOR ADM, O HEADER FICA TRANSPARENTE PARA MOSTRAR A SETA. SE NÃO, SOME TUDO. */
    header { 
        background-color: rgba(0,0,0,0) !important; 
        color: white !important;
    }

    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }

    .t-header { text-align: center; padding: 25px 0 5px 0; border-bottom: 1px solid rgba(255,255,255,0.15); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 12px; font-weight: 700; letter-spacing: 2px; }

    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 22px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF !important; width: 45%; font-weight: 900; text-transform: uppercase; }
    .d-value { font-size: 26px; width: 55%; text-align: right; font-family: 'Chakra Petch', sans-serif; font-weight: 700; color: #eee; }
    
    .sub-grid { display: flex; gap: 12px; justify-content: flex-end; width: 55%; }
    .sub-l { font-size: 8px; color: #FFFFFF !important; display: block; font-weight: 400; }
    .sub-v { font-size: 17px; font-family: 'Chakra Petch', sans-serif; font-weight: 700; }

    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    
    .f-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height:
