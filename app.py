import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL (Multiplicadores em Variáveis)
@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "v_min": 1.0020,   
        "v_jus": 1.0041,   
        "v_max": 1.0100,   
        "notas_mural": "AGUARDANDO ATUALIZAÇÃO...",
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

# 4. CSS DO TERMINAL
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
    .indicator-row { display: flex; justify-content: center; align-items: center; gap: 15px; margin-top: 6px; }
    .vies-indicator { font-size: 13px; font-weight: 900; font-family: 'Orbitron'; }
    .media-azul { font-size: 16px; font-weight: 700; font-family: 'Chakra Petch'; color: #0066cc; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; display: flex; flex-direction: column; }
    .sub-l { font-size: 8px; color: #888; margin-bottom: 2px; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .v-peq { font-size: 16px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 140px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; margin-top: 12px; display: flex; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE DATA
def get_clean_data(ticker):
    try:
        t = yf.Ticker(ticker)
        last = t.fast_info.last_price
        prev = t.fast_info.previous_close
        var = ((last - prev) / prev * 100) if prev != 0 else 0
        return {"last": last, "prev": prev, "var": var}
    except: return {"last": 0.0, "prev": 0.0, "var": 0.0}

# 6. RENDERIZAÇÃO
@st.fragment(run_every=1)
def monitor_terminal():
    d_m = get_clean_data("DX-Y.NYB")
    e_m = get_clean_data("EWZ")
    s_m = get_clean_data("BRL=X")
    
    if s_m["last"] > 0:
        spot, prev_close, v_spot = s_m["last"], s_m["prev"], s_m["var"]
        cor_v_spot = "#00cc66" if v_spot >= 0 else "#cc3333"
        spr = d_m["var"] - e_m["var"]
        paridade_global = v_global["ajuste"]*(1+(spr/100))
        
        # CÁLCULOS
        justo = round((spot * v_global["v_jus"]) * 2000) / 2000
        equilibrio = round((v_global["ref"] * v_global["v_min"]) * 2000) / 2000
        
        # NOVA MÉDIA (AJUSTE SOLICITADO)
        media_azul = (spot + justo + paridade_global) / 3

        if spot < (paridade_global - 0.0030): fut_seta, fut_clr = "▲ FUTURO", "#00cc66"
        elif spot > (paridade_global + 0.0030): fut_seta, fut_clr = "▼ FUTURO", "#cc3333"
        else: fut_seta, fut_clr = "● ESTÁVEL", "#444"

        st.markdown(f'<div class="t-header"><div class="pulse-green"></div><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="s-container"><div class="s-text">{spot:.4f} <span class="var-style" style="color:{cor_v_spot}">{v_spot:+.2f}%</span></div><div class="s-subtext">FECH. ANTERIOR: {prev_close:.4f}</div><div class="indicator-row"><span class="vies-indicator" style="color:{fut_clr}">{fut_seta}</span><span class="media-azul">{media_azul:.4f}</span></div></div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{paridade_global:.4f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value c-equi">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="d-value c-jus">{justo:.4f}</div></div>', unsafe_allow_html=True)
        
        # REF INSTITUCIONAL
        st.markdown(f'<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((v_global["ref"]*v_global["v_min"])*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{(round((v_global["ref"]*v_global["v_jus"])*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((v_global["ref"]*v_global["v_max"])*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

        btk = f"SPOT {spot:.4f} | DXY {d_m['last']:.2f} | EWZ {e_m['last']:.2f} | SPREAD {spr:+.2f}%"
        st.markdown(f'<div class="f-bar"><div class="tk-wrap"><div class="tk-move">{btk} &nbsp;&nbsp;&nbsp; {btk}</div></div></div>', unsafe_allow_html=True)

# PAINEL ADM
if st.session_state.user_type == "ADM":
    with st.expander("PAINEL ADM"):
        with st.form("adm"):
            c1, c2 = st.columns(2)
            v_global["ajuste"] = c1.number_input("PARIDADE", value=v_global["ajuste"], format="%.4f")
            v_global["ref"] = c2.number_input("REF INST", value=v_global["ref"], format="%.4f")
            col_v1, col_v2, col_v3 = st.columns(3)
            v_global["v_min"] = col_v1.number_input("Var 1.002", value=v_global["v_min"], format="%.4f")
            v_global["v_jus"] = col_v2.number_input("Var 1.0041", value=v_global["v_jus"], format="%.4f")
            v_global["v_max"] = col_v3.number_input("Var 1.01", value=v_global["v_max"], format="%.4f")
            if st.form_submit_button("SALVAR"): st.rerun()

monitor_terminal()
