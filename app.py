import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "v_min": 1.0020,
        "v_jus": 1.0041,
        "v_max": 1.0100,
        "notas_mural": "RESUMO DA ABERTURA E AGENDA: AGUARDANDO ATUALIZAÇÃO...",
        "notas": "MURAL: AGUARDANDO...",
        "notas2": "INFORMATIVO: OPERACIONAL ATIVO"
    }

v_global = get_global_vars()

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_type = None

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'], label { display: none !important; } .stButton button { width: 100%; background-color: #222; color: white; border: 1px solid #444; margin-top: 20px; }</style>", unsafe_allow_html=True)
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

# 4. CSS DO TERMINAL (COM ANIMAÇÃO DO LED RECUPERADA)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: center; align-items: center; gap: 10px; }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    .pulse-green { width: 8px; height: 8px; background: #00ff00; border-radius: 50%; box-shadow: 0 0 0 rgba(0, 255, 0, 0.4); animation: pulse-green-animation 1.2s infinite; }
    @keyframes pulse-green-animation { 0% { box-shadow: 0 0 0 0px rgba(0, 255, 0, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); } 100% { box-shadow: 0 0 0 0px rgba(0, 255, 0, 0); } }
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 32px; font-weight: 700; font-family: 'Chakra Petch'; color: #ffffff; }
    .var-style { font-size: 20px; margin-left: 12px; font-weight: 400; }
    .s-subtext { font-size: 10px; color: #666; margin-top: 2px; }
    .vies-indicator { font-size: 14px; font-weight: 900; margin-top: 6px; font-family: 'Orbitron'; display: flex; justify-content: center; align-items: center; gap: 15px; }
    .media-azul-val { color: #0066cc; font-family: 'Chakra Petch'; font-size: 20px; font-weight: 700; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 15px; color: #FFFFFF; font-weight: 400; width: 40%; letter-spacing: 1px; }
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; display: flex; flex-direction: column; }
    .sub-l { font-size: 9px; color: #888; margin-bottom: 2px; font-weight: 700; }
    .sub-v { font-size: 20px; font-family: 'Chakra Petch'; font-weight: 700; }
    .d-value { font-size: 28px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; min-height: 120px; }
    .note-title { font-size: 9px; color: #444; letter-spacing: 2px; margin-bottom: 8px; font-weight: 900; border-bottom: 1px solid #111; }
    .note-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; line-height: 1.5; }
    
    /* RODAPÉ FIXO COM LED */
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 140px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .f-notes { font-family: 'Chakra Petch'; font-size: 11px; color: #ffff99; margin-bottom: 3px; text-transform: uppercase; }
    .f-notes2 { font-family: 'Chakra Petch'; font-size: 10px; color: #aaaaaa; margin-bottom: 10px; }
    .f-line { width: 90%; height: 1px; background: rgba(255,255,255,0.08); }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; margin-top: 12px; display: flex; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff
