import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "fraldao": 15.0, # Diferença para compor o Futuro B3
        "notas_mural": "AGUARDANDO ATUALIZAÇÃO...",
        "notas": "MURAL: ATIVO",
        "notas2": "INFORMATIVO: OPERACIONAL"
    }

v_global = get_global_vars()

# 3. CONTROLE DE ACESSO (Omitido para brevidade, manter o que já existe no seu)
if 'auth' not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    # ... (Mantenha seu bloco de login aqui)
    st.stop()

# 4. CSS (AJUSTADO PARA DISCREÇÃO E PISCANTE)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 12px; font-weight: 700; letter-spacing: 2px; }
    
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    
    /* PREÇO B3 DISCRETO */
    .v-b3-small { font-size: 18px; color: #aaa; font-family: 'Chakra Petch'; font-weight: 700; }

    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; }
    .v-peq { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .v-extra { font-size: 12px; font-family: 'Chakra Petch'; font-weight: 400; color: #ffff00; opacity: 0.6; }

    /* SINAL MICRO */
    .micro-container { text-align: right; padding: 2px 15px 15px 0; font-family: 'Chakra Petch'; font-size: 10px; font-weight: 700; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    .blink-text { animation: blinker 0.7s linear infinite; }

    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; min-height: 120px; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 160px; background: #050505; border-top: 1px solid #222; z-index: 9999; display: flex; flex-direction: column; align-items: center; justify-content: center;}
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
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
    
    if s_m["last"] > 0:
        spot = s_m["last"]
        # CALCULO DO FUTURO B3 (SINTÉTICO)
        dol_b3 = spot + (v_global["fraldao"] / 1000)
        
        spr = d_m["var"] - e_m["var"]
        pari_val = v_global["ajuste"] * (1 + (spr/100))
        equilibrio = round((v_global["ref"] + 0.0220) * 2000) / 2000
        
        # SINAL MICRO BASEADO NO PREÇO B3
        diff_pts = (dol_b3 - equilibrio) * 1000
        blink_class = ""
        if diff_pts >= 22: mic_msg, mic_clr, blink_class = "DÓLAR MUITO CARO (B3)", "#ff0000", "blink-text"
        elif diff_pts >= 11: mic_msg, mic_clr, blink_class = "DÓLAR CARO (B3)", "#ff6600", "blink-text"
        elif diff_pts <= -22: mic_msg, mic_clr, blink_class = "DÓLAR MUITO BARATO (B3)", "#00ff00", "blink-text"
        elif diff_pts <= -11: mic_msg, mic_clr, blink_class = "DÓLAR BARATO (B3)", "#00cc66", "blink-text"
        else: mic_msg, mic_clr, blink_class = "DÓLAR CONSOLIDADO", "#555555", ""

        with ui_area.container():
            # Painel ADM (Omitido aqui, manter o seu com o campo Fraldão)
            
            st.markdown('<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR PRO</span></div></div>', unsafe_allow_html=True)
            
            # PARIDADE E EQUILIBRIO
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{pari_val:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO B3 DISCRETO (O preço que manda no sinal)
            st.markdown(f'<div class="d-row" style="padding: 5px 15px;"><div class="d-label" style="opacity:0.5">DÓLAR B3 (TELA)</div><div class="v-b3-small">{dol_b3:.4f}</div></div>', unsafe_allow_html=True)

            # REGIÃO DE CORREÇÃO VERTICAL
            st.markdown(f"""
            <div class="d-row" style="padding-top:10px; border-bottom: none; align-items: flex-start;">
                <div class="d-label" style="opacity:0.6; margin-top:5px;">REGIÃO DE CORREÇÃO</div>
                <div class="sub-grid">
                    <div class="sub-item" style="display: flex; flex-direction: column;">
                        <span class="v-peq">{(equilibrio - 0.0110):.4f}</span>
                        <span class="v-extra">{(equilibrio - 0.0220):.4f}</span>
                    </div>
                    <div class="sub-item" style="display: flex; flex-direction: column;">
                        <span class="v-peq">{(equilibrio + 0.0110):.4f}</span>
                        <span class="v-extra">{(equilibrio + 0.0220):.4f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # SINAL MICRO (PISCANTE CONFORME PREÇO B3)
            st.markdown(f'<div class="micro-container"><span class="{blink_class}" style="color:{mic_clr}">{mic_msg}</span></div>', unsafe_allow_html=True)

            # MURAL E RODAPÉ (Manter seu original aqui)
            st.markdown(f'<div class="note-box"><div style="color:#999; font-size:13px;">{v_global["notas_mural"]}</div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
