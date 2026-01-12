import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas_mural": "AGUARDANDO ATUALIZAÇÃO...",
        "notas": "MURAL ATIVO",
        "notas2": "SISTEMA OPERACIONAL"
    }

v_global = get_global_vars()

# 2. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("CHAVE", type="password")
        if st.button("ENTRAR"):
            if senha in ["admin123", "trader123"]:
                st.session_state.auth = True
                st.session_state.user_type = "ADM" if senha == "admin123" else "USER"
                st.rerun()
    st.stop()

# 3. CSS (REVISADO)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, footer, label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; }
    .t-header { text-align: center; padding: 20px 0; border-bottom: 1px solid #222; }
    .t-bold { color: #fff; font-weight: 900; letter-spacing: 3px; }
    .s-container { text-align: center; padding: 12px 0; margin-bottom: 5px; }
    .s-text { font-size: 13px; font-weight: 900; letter-spacing: 2px; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; }
    .d-value { font-size: 26px; font-family: 'Chakra Petch'; font-weight: 700; }
    .sub-grid { display: flex; gap: 12px; justify-content: flex-end; }
    .v-peq { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .note-box { background: #050505; border-top: 1px solid #111; padding: 20px; min-height: 100px; }
    .note-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 150px; background: #050505; border-top: 1px solid #222; text-align: center; z-index: 100; }
</style>
""", unsafe_allow_html=True)

def get_clean_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        last = float(df['Close'].iloc[-1])
        prev = float(yf.Ticker(ticker).fast_info.previous_close)
        return {"last": last, "var": ((last-prev)/prev*100)}
    except: return {"last": 0.0, "var": 0.0}

ui_area = st.empty()
while True:
    d_m = get_clean_data("DX-Y.NYB")
    e_m = get_clean_data("EWZ")
    s_m = get_clean_data("BRL=X")
    
    if d_m["last"] > 0:
        spot = s_m["last"]
        spr = d_m["var"] - e_m["var"]
        paridade = v_global["ajuste"] * (1 + (spr/100))
        equilibrio = round((v_global["ref"] + 0.0220) * 2000) / 2000
        
        # LOGICA MACRO (PRECIFICAÇÃO)
        if spot < (paridade - 0.0015): msg, clr = "● PRECIFICAÇÃO DE ALTA", "#00ff00"
        elif spot > (paridade + 0.0015): msg, clr = "● PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: msg, clr = "● PRECIFICAÇÃO NEUTRA", "#ffff00"
            
        # LOGICA MICRO (ALERTAS DISCRETOS)
        diff = (spot - equilibrio) * 1000
        if diff >= 22: mic_txt, mic_clr = "MICRO: MUITO CARO (+22)", "#ff0000"
        elif diff >= 11: mic_txt, mic_clr = "MICRO: CARO (+11)", "#ff6600"
        elif diff <= -22: mic_txt, mic_clr = "MICRO: MUITO BARATO (-22)", "#00ff00"
        elif diff <= -11: mic_txt, mic_clr = "MICRO: BARATO (-11)", "#00cc66"
        else: mic_txt, mic_clr = "MICRO: ESTÁVEL", "#666666"

        with ui_area.container():
            if st.session_state.user_type == "ADM":
                with st.expander("AJUSTES"):
                    v_global["ajuste"] = st.number_input("PARIDADE", value=v_global["ajuste"], format="%.4f")
                    v_global["ref"] = st.number_input("REF", value=v_global["ref"], format="%.4f")
                    v_global["notas_mural"] = st.text_area("AGENDA", value=v_global["notas_mural"])
                    if st.button("SALVAR"): st.rerun()

            # CABEÇALHO
            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR PRO</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {clr}77"><div class="s-text" style="color:{clr}">{msg}</div></div>', unsafe_allow_html=True)
            
            # PREÇOS PRINCIPAIS
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{paridade:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)

            # REGIÃO DE CORREÇÃO (4 NÍVEIS)
            st.markdown(f"""
            <div class="d-row" style="border-bottom:none; padding-bottom:5px;">
                <div class="d-label" style="opacity:0.6;">REGIÃO DE CORREÇÃO</div>
                <div class="sub-grid">
                    <div class="sub-item"><span class="v-peq">{(equilibrio - 0.0220):.4f}</span></div>
                    <div class="sub-item"><span class="v-peq">{(equilibrio - 0.0110):.4f}</span></div>
                    <div class="sub-item"><span class="v-peq">{(equilibrio + 0.0110):.4f}</span></div>
                    <div class="sub-item"><span class="v-peq">{(equilibrio + 0.0220):.4f}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ALERTA MICRO DISCRE
