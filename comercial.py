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
        "fraldao": 15.0, # Diferença de pontos para compor o Futuro
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

# 4. CSS DO TERMINAL
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
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; }
    .sub-l { font-size: 8px; color: #888; display: block; margin-bottom: 2px; font-weight: 400; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .v-peq { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .v-extra { font-size: 12px; font-family: 'Chakra Petch'; font-weight: 400; color: #ffff00; opacity: 0.6; margin-top: 2px; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .v-fut-discreto { font-size: 16px; color: #666; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .micro-container { text-align: right; padding: 0 15px 10px 0; font-family: 'Chakra Petch'; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
    @keyframes blinker { 50% { opacity: 0; } }
    .blink-text { animation: blinker 0.8s linear infinite; }

    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; margin-top: 5px; min-height: 120px; }
    .note-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; line-height: 1.5; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 160px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_clean_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, prepost=True)
        t = yf.Ticker(ticker)
        prev = float(t.fast_info.previous_close)
        last = float(df['Close'].iloc[-1]) if not df.empty else prev
        return {"last": last, "var": ((last - prev) / prev * 100)}
    except: return {"last": 0.0, "var": 0.0}

ui_area = st.empty()
while True:
    d_m = get_clean_data("DX-Y.NYB")
    e_m = get_clean_data("EWZ")
    s_m = get_clean_data("BRL=X")
    
    if d_m["last"] > 0:
        spot = s_m["last"]
        # CÁLCULO DÓLAR FUTURO (SEM DELAY)
        dol_futuro = spot + (v_global["fraldao"] / 1000)
        
        spr = d_m["var"] - e_m["var"]
        pari_val = v_global["ajuste"]*(1+(spr/100))
        equilibrio = round((v_global["ref"] + 0.0220) * 2000) / 2000
        
        # LÓGICA MACRO (PELO SPOT)
        if spot < (pari_val - 0.0015): msg, clr, arr = "● PRECIFICAÇÃO DE ALTA", "#00aa55", "▲ ▲ ▲ ▲ ▲"
        elif spot > (pari_val + 0.0015): msg, clr, arr = "● PRECIFICAÇÃO DE BAIXA", "#aa3333", "▼ ▼ ▼ ▼ ▼"
        else: msg, clr, arr = "● PRECIFICAÇÃO NEUTRA", "#aaaa00", "◄ ◄ ◄ ► ► ►"

        # LÓGICA MICRO (GATILHO PELO DÓLAR FUTURO)
        diff_pts = (dol_futuro - equilibrio) * 1000
        blink_class = ""
        if diff_pts >= 22: mic_msg, mic_clr, blink_class = "DÓLAR MUITO CARO", "#ff0000", "blink-text"
        elif diff_pts >= 11: mic_msg, mic_clr, blink_class = "DÓLAR CARO", "#ff6600", "blink-text"
        elif diff_pts <= -22: mic_msg, mic_clr, blink_class = "DÓLAR MUITO BARATO", "#00ff00", "blink-text"
        elif diff_pts <= -11: mic_msg, mic_clr, blink_class = "DÓLAR BARATO", "#00cc66", "blink-text"
        else: mic_msg, mic_clr, blink_class = "DÓLAR CONSOLIDADO", "#555555", ""
            
        with ui_area.container():
            if st.session_state.user_type == "ADM":
                with st.expander("PAINEL ADM"):
                    with st.form("adm_panel"):
                        c1, c2, c3 = st.columns(3)
                        v_global["ajuste"] = c1.number_input("PARIDADE", value=v_global["ajuste"], format="%.4f")
                        v_global["ref"] = c2.number_input("REF INST", value=v_global["ref"], format="%.4f")
                        v_global["fraldao"] = c3.number_input("DIF. FUTURO (PTS)", value=v_global["fraldao"], format="%.1f")
                        v_global["notas_mural"] = st.text_area("MORNING CALL", value=v_global["notas_mural"])
                        if st.form_submit_button("SALVAR"): st.rerun()

            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR PRO</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {clr}77"><div class="s-text" style="color:{clr}">{msg}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{pari_val:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)
            
            # DÓLAR FUTURO (DISCRETO)
            st.markdown(f'<div class="d-row" style="padding: 5px 15px; border-bottom: none;"><div class="d-label" style="color:#444">DÓLAR FUTURO</div><div class="v-fut-discreto">{dol_futuro:.4f}</div></div>', unsafe_allow_html=True)

            # REGIÃO DE CORREÇÃO (COLUNAS VERTICAIS)
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

            # SINAL MICRO (PISCANTE PELO FUTURO)
            st.markdown(f'<div class="micro-container"><span class="{blink_class}" style="color:{mic_clr}">{mic_msg}</span></div>', unsafe_allow_html=True)

            # MURAL
            st.markdown(f'<div class="note-box"><div class="note-content">{v_global["notas_mural"]}</div></div>', unsafe_allow_html=True)
            
            # RODAPÉ (TICKER)
            def f_tk(d, n):
                c = "#00aa55" if d["var"] >= 0 else "#aa3333"
                return f"<span style='padding-right:50px; color:#fff;'><b>{n}</b> {d['last']:.4f} <span style='color:{c}'>({d['var']:+.2f}%)</span></span>"
            btk = f"{f_tk(s_m,'SPOT')} {f_tk(d_m,'DXY')} {f_tk(e_m,'EWZ')}"
            st.markdown(f'<div class="f-bar"><div style="color:{clr}; font-size:16px; letter-spacing:8px;">{arr}</div><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
