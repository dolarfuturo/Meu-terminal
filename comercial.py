import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL PRO", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas_mural": "AGUARDANDO AGENDA...",
        "notas": "MURAL: AGUARDANDO...",
        "notas2": "INFORMATIVO: OPERACIONAL ATIVO"
    }

v_global = get_global_vars()

# 2. CSS (VOLTANDO AO PADRÃO ANTERIOR)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    
    .status-box { display: flex; justify-content: space-around; padding: 10px; background: #050505; border-bottom: 2px solid #111; }
    .status-item { text-align: center; width: 48%; padding: 8px; }
    .s-label { font-size: 8px; color: #555; letter-spacing: 2px; margin-bottom: 4px; font-weight: 900; }
    .s-value { font-size: 12px; font-weight: 900; letter-spacing: 1px; }

    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 22px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 60px; }
    .sub-l { font-size: 7px; color: #444; display: block; margin-bottom: 2px; }
    .sub-v { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }

    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    
    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; min-height: 120px; }
    .note-title { font-size: 9px; color: #444; letter-spacing: 2px; margin-bottom: 8px; font-weight: 900; border-bottom: 1px solid #111; padding-bottom: 4px; }
    .note-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; line-height: 1.5; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 60px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; justify-content: center; z-index: 9999; }
</style>
""", unsafe_allow_html=True)

def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, prepost=True)
        if df.empty: return None
        last = float(df['Close'].iloc[-1])
        prev = float(yf.Ticker(ticker).fast_info.previous_close)
        return {"last": last, "prev": prev, "var": ((last-prev)/prev*100)}
    except: return None

ui_area = st.empty()
while True:
    d_m = get_market_data("DX-Y.NYB")
    e_m = get_market_data("EWZ")
    s_m = get_market_data("BRL=X")
    
    if d_m and s_m:
        spot = s_m["last"]
        spr = d_m["var"] - e_m["var"]
        paridade = v_global["ajuste"] * (1 + (spr/100))
        equilibrio = round((v_global["ref"] + 0.0220) * 2000) / 2000
        
        # LOGICA MACRO
        if spot < (paridade - 0.0015): m_stat, m_clr = "PRECIFICAÇÃO DE ALTA", "#00ff00"
        elif spot > (paridade + 0.0015): m_stat, m_clr = "PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: m_stat, m_clr = "PRECIFICAÇÃO NEUTRA", "#ffff00"
        
        # LOGICA MICRO (PONTOS DO EQUILIBRIO)
        diff_pts = (spot - equilibrio) * 1000
        if diff_pts >= 22: mic_stat, mic_clr = "MICRO: MUITO CARO (+22)", "#ff0000"
        elif diff_pts >= 11: mic_stat, mic_clr = "MICRO: CARO (+11)", "#ff6600"
        elif diff_pts <= -22: mic_stat, mic_clr = "MICRO: MUITO BARATO (-22)", "#00ff00"
        elif diff_pts <= -11: mic_stat, mic_clr = "MICRO: BARATO (-11)", "#00cc66"
        else: mic_stat, mic_clr = "MICRO: SINAL NEUTRO", "#ffff00"

        with ui_area.container():
            # Cabeçalho
            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR PRO</span></div></div>', unsafe_allow_html=True)
            
            # Painel de Sinais
            st.markdown(f"""
            <div class="status-box">
                <div class="status-item" style="border-right: 1px solid #111;">
                    <div class="s-label">TENDÊNCIA MACRO</div>
                    <div class="s-value" style="color:{m_clr}">{m_stat}</div>
                </div>
                <div class="status-item">
                    <div class="s-label">SINAL MICRO</div>
                    <div class="s-value" style="color:{mic_clr}">{mic_stat}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Linhas de Preço
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO EQUILÍBRIO</div><div class="d-value c-equi">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)

            # Região de Correção (Mantendo alinhamento sub-grid)
            st.markdown(f"""
            <div class="d-row" style="padding: 10px 15px;">
                <div class="d-label" style="opacity:0.6;">REGIÃO DE CORREÇÃO</div>
                <div class="sub-grid">
                    <div class="sub-item"><span class="sub-l">-22pts</span><span class="sub-v">{(equilibrio - 0.0220):.4f}</span></div>
                    <div class="sub-item"><span class="sub-l">-11pts</span><span class="sub-v">{(equilibrio - 0.0110):.4f}</span></div>
                    <div class="sub-item"><span class="sub-l">+11pts</span><span class="sub-v">{(equilibrio + 0.0110):.4f}</span></div>
                    <div class="sub-item"><span class="sub-l">+22pts</span><span class="sub-v">{(equilibrio + 0.0220):.4f}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Bloco de Notas (Espaço Preto)
            st.markdown(f"""
            <div class="note-box">
                <div class="note-title">MORNING CALL & AGENDA</div>
                <div class="note-content">{v_global["notas_mural"].replace('\n', '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)

    time.sleep(2)
