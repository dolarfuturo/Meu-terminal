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
        "notas_mural": "AGUARDANDO ATUALIZAÇÃO...",
        "notas": "MURAL: AGUARDANDO...",
        "notas2": "INFORMATIVO: OPERACIONAL ATIVO"
    }

v_global = get_global_vars()

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False

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
    st.stop()

# 4. CSS DO TERMINAL (COM ANIMAÇÃO DE ATUALIZAÇÃO)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    /* ANIMAÇÃO DOS BONECOS (SINAL DE ATUALIZAÇÃO) */
    @keyframes pulse_update {
        0% { transform: scale(1); }
        50% { transform: scale(1.005); opacity: 0.9; }
        100% { transform: scale(1); }
    }
    .update-anim { animation: pulse_update 0.5s ease-in-out; }

    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 18px; font-weight: 700; letter-spacing: 1px; font-family: 'Chakra Petch'; }
    .s-subtext { font-size: 10px; color: #666; font-weight: 400; letter-spacing: 1px; margin-top: 2px; }
    .vies-indicator { font-size: 13px; font-weight: 900; letter-spacing: 2px; margin-top: 6px; font-family: 'Orbitron'; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; display: flex; flex-direction: column; }
    .sub-l { font-size: 8px; color: #888; display: block; margin-bottom: 2px; font-weight: 400; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 130px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE DADOS
def fetch(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False, prepost=True)
        if not data.empty:
            last = float(data['Close'].iloc[-1])
            prev = float(yf.Ticker(ticker).fast_info.previous_close)
            return {"last": last, "var": ((last-prev)/prev*100), "prev": prev}
    except: pass
    return None

last_val = {"BRL=X": {"last": 5.40, "var": 0.0, "prev": 5.40}, "DX-Y.NYB": {"last": 100.0, "var": 0.0}, "EWZ": {"last": 30.0, "var": 0.0}}

# 6. LOOP
ui_area = st.empty()
while True:
    for t in last_val.keys():
        res = fetch(t)
        if res: last_val[t] = res

    s = last_val["BRL=X"]
    spr = last_val["DX-Y.NYB"]["var"] - last_val["EWZ"]["var"]
    paridade = v_global["ajuste"] * (1 + (spr/100))
    
    # Lógica de cores da variação
    var_clr = "#00ff88" if s["var"] >= 0 else "#ff4444"
    
    if s["last"] < (paridade - 0.0030): fut_txt, fut_clr = "▲▲ FUTURO", "#00ff88"
    elif s["last"] > (paridade + 0.0030): fut_txt, fut_clr = "▼▼ FUTURO", "#ff4444"
    else: fut_txt, fut_clr = "● ESTÁVEL", "#444"

    with ui_area.container():
        # DIV COM A ANIMAÇÃO (BONECOS SE MEXENDO)
        st.markdown(f'<div class="update-anim">', unsafe_allow_html=True)
        
        st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
        
        # SPOT BRANCO COM VARIAÇÃO COLORIDA
        st.markdown(f"""
        <div class="s-container">
            <div class="s-text">
                SPOT <span style="color:#fff">{s['last']:.4f}</span> 
                <span style="color:{var_clr}; margin-left:10px;">({s['var']:+.2f}%)</span>
            </div>
            <div class="s-subtext">FECH. ANTERIOR: {s['prev']:.4f}</div>
            <div class="vies-indicator" style="color:{fut_clr}">{fut_txt}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{paridade:.4f}</div></div>', unsafe_allow_html=True)
        
        # PREÇO JUSTO
        st.markdown(f"""
        <div class="d-row">
            <div class="d-label">PREÇO JUSTO</div>
            <div class="sub-grid">
                <div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v" style="color:#ff4444">{(round((s['last']+0.0220)*2000)/2000):.4f}</span></div>
                <div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v" style="color:#0088ff">{(round((s['last']+0.0310)*2000)/2000):.4f}</span></div>
                <div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v" style="color:#00ff88">{(round((s['last']+0.0420)*2000)/2000):.4f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True) # Fim da div de animação

        # Rodapé
        btk = f"<span class='tk-item'><b>SPOT</b> {s['last']:.4f}</span> <span class='tk-item'><b>DXY</b> {last_val['DX-Y.NYB']['last']:.2f}</span>"
        st.markdown(f"""
        <div class="f-bar">
            <div style="font-size:11px; color:#ffff99;">{v_global["notas"]}</div>
            <div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div>
        </div>
        """, unsafe_allow_html=True)

    time.sleep(1)
