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

# 4. CSS (MANTIDO E AJUSTADO PARA O SPOT)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .t-header { text-align: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 11px; letter-spacing: 3px; }
    .spot-destaque { font-size: 45px; color: #fff; font-weight: 900; font-family: 'Chakra Petch'; margin-top: -5px; }
    .s-container { text-align: center; padding: 10px 0; }
    .s-text { font-size: 12px; font-weight: 700; letter-spacing: 2px; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; display: flex; flex-direction: column; }
    .sub-l { font-size: 8px; color: #888; display: block; margin-bottom: 2px; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .v-peq { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .v-extra { font-size: 12px; font-family: 'Chakra Petch'; font-weight: 400; color: #ffff00; opacity: 0.6; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 80px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 9999; }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_clean_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d", interval="1m")
        prev = t.fast_info.previous_close
        last = df['Close'].iloc[-1]
        var = ((last - prev) / prev * 100)
        return {"last": last, "prev": prev, "var": var}
    except:
        return {"last": 0.0, "prev": 0.0, "var": 0.0}

ui_area = st.empty()
while True:
    d_m = get_clean_data("DX-Y.NYB")
    e_m = get_clean_data("EWZ")
    s_m = get_clean_data("BRL=X")
    
    if d_m["last"] > 0:
        spot = s_m["last"]
        spr = d_m["var"] - e_m["var"]
        # CÁLCULOS ORIGINAIS MANTIDOS
        justo = round((spot + 0.0310) * 2000) / 2000
        equilibrio = round((v_global["ref"] + 0.0220) * 2000) / 2000
        
        diff = spot - justo
        if diff < -0.0015: msg, clr = "● PRECIFICAÇÃO DE ALTA", "#00aa55"
        elif diff > 0.0015: msg, clr = "● PRECIFICAÇÃO DE BAIXA", "#aa3333"
        else: msg, clr = "● PRECIFICAÇÃO NEUTRA", "#aaaa00"
            
        with ui_area.container():
            if st.session_state.user_type == "ADM":
                with st.expander("PAINEL ADM"):
                    with st.form("adm_panel"):
                        c1, c2 = st.columns(2)
                        v_global["ajuste"] = c1.number_input("PARIDADE", value=v_global["ajuste"], format="%.4f")
                        v_global["ref"] = c2.number_input("REF INST", value=v_global["ref"], format="%.4f")
                        v_global["notas_mural"] = st.text_area("MORNING CALL", value=v_global["notas_mural"])
                        if st.form_submit_button("SALVAR"): st.rerun()

            # HEADER COM SPOT ACRESCENTADO
            st.markdown(f'<div class="t-header"><div class="t-title">DOLAR SPOT</div><div class="spot-destaque">{spot:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {clr}77"><div class="s-text" style="color:{clr}">{msg}</div></div>', unsafe_allow_html=True)
            
            # BLOCO DE PREÇOS (IGUAL AO ORIGINAL)
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{(v_global["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value c-equi">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{justo:.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{(round((v_global["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((v_global["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # REGIÃO DE CORREÇÃO (FREQUÊNCIAS MANTIDAS)
            st.markdown(f"""
            <div class="d-row" style="border-bottom: none;">
                <div class="d-label">REGIÃO DE CORREÇÃO</div>
                <div class="sub-grid">
                    <div class="sub-item"><span class="v-peq">{(equilibrio - 0.0110):.4f}</span><span class="v-extra">{(equilibrio - 0.0220):.4f}</span></div>
                    <div class="sub-item"><span class="v-peq">{(equilibrio + 0.0110):.4f}</span><span class="v-extra">{(equilibrio + 0.0220):.4f}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # RODAPÉ TICKER (REDUZIDO PARA DAR ESPAÇO)
            btk = f"<span class='tk-item'><b>SPOT</b> {spot:.4f}</span> <span class='tk-item'><b>MURAL:</b> {v_global['notas_mural']}</span>"
            st.markdown(f'<div class="f-bar"><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
