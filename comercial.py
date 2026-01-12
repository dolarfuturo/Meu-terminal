import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL DOLAR PRO", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas_mural": "AGUARDANDO ATUALIZAÇÃO...",
        "notas": "MURAL: ATIVO",
        "notas2": "INFORMATIVO: OPERACIONAL"
    }

v_global = get_global_vars()

# 2. CSS (AJUSTADO PARA COLUNAS NA CORREÇÃO E TEXTO PISCANTE)
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
    
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    
    /* GRID CORREÇÃO EM COLUNAS */
    .corr-container { display: flex; gap: 20px; justify-content: flex-end; width: 60%; text-align: center; }
    .corr-col { display: flex; flex-direction: column; gap: 5px; }
    .v-peq { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }

    /* SINAL MICRO */
    .micro-box { text-align: right; padding: 5px 15px; font-family: 'Chakra Petch'; font-size: 10px; font-weight: 700; text-transform: uppercase; }
    
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .piscante { animation: blink 0.8s infinite; }
    
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; min-height: 120px; }
    .note-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; line-height: 1.5; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 160px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
</style>
""", unsafe_allow_html=True)

def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        last = float(df['Close'].iloc[-1])
        prev = float(yf.Ticker(ticker).fast_info.previous_close)
        return {"last": last, "var": ((last-prev)/prev*100)}
    except: return {"last": 0.0, "var": 0.0}

ui_area = st.empty()
while True:
    d_m = get_market_data("DX-Y.NYB")
    e_m = get_market_data("EWZ")
    s_m = get_market_data("BRL=X")
    
    if s_m["last"] > 0:
        spot = s_m["last"]
        spr = d_m["var"] - e_m["var"]
        paridade = v_global["ajuste"] * (1 + (spr/100))
        equilibrio = round((v_global["ref"] + 0.0220) * 2000) / 2000
        
        # MACRO
        if spot < (paridade - 0.0015): m_msg, m_clr = "● PRECIFICAÇÃO DE ALTA", "#00aa55"
        elif spot > (paridade + 0.0015): m_msg, m_clr = "● PRECIFICAÇÃO DE BAIXA", "#aa3333"
        else: m_msg, m_clr = "● PRECIFICAÇÃO NEUTRA", "#aaaa00"
            
        # MICRO LÓGICA
        diff_pts = (spot - equilibrio) * 1000
        is_piscando = ""
        if diff_pts >= 22: mic_txt, mic_clr, is_piscando = "DÓLAR MUITO CARO", "#ff0000", "piscante"
        elif diff_pts >= 11: mic_txt, mic_clr, is_piscando = "DÓLAR CARO", "#ff6600", "piscante"
        elif diff_pts <= -22: mic_txt, mic_clr, is_piscando = "DÓLAR MUITO BARATO", "#00ff00", "piscante"
        elif diff_pts <= -11: mic_txt, mic_clr, is_piscando = "DÓLAR BARATO", "#00cc66", "piscante"
        else: mic_txt, mic_clr, is_piscando = "DÓLAR CONSOLIDADO", "#555555", ""

        with ui_area.container():
            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR PRO</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {m_clr}77"><div class="s-text" style="color:{m_clr}">{m_msg}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO EQUILÍBRIO</div><div class="d-value c-equi">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)

            # REGIÃO DE CORREÇÃO EM COLUNAS
            st.markdown(f"""
            <div class="d-row" style="padding-top:10px; border-bottom: none; align-items: flex-start;">
                <div class="d-label" style="opacity:0.6; margin-top:5px;">REGIÃO DE CORREÇÃO</div>
                <div class="corr-container">
                    <div class="corr-col">
                        <span class="v-peq">{(equilibrio - 0.0110):.4f}</span>
                        <span class="v-peq" style="opacity:0.7; font-size:13px;">{(equilibrio - 0.0220):.4f}</span>
                    </div>
                    <div class="corr-col">
                        <span class="v-peq">{(equilibrio + 0.0110):.4f}</span>
                        <span class="v-peq" style="opacity:0.7; font-size:13px;">{(equilibrio + 0.0220):.4f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # SINAL MICRO (TEXTO E ANIMAÇÃO)
            st.markdown(f'<div class="micro-box {is_piscando}" style="color:{mic_clr}">{mic_txt}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="note-box"><div class="note-content">{v_global["notas_mural"].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="f-bar"><div style="color:#ffff99; font-size:11px;">{v_global["notas"]}</div><div style="color:#555; font-size:10px;">{v_global["notas2"]}</div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
