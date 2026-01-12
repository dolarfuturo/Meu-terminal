import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL DOLAR PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
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

# 4. CSS DO TERMINAL (COMPLETO E AJUSTADO)
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
    
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .sub-l { font-size: 8px; color: #888; display: block; margin-bottom: 2px; }

    /* GRID CORREÇÃO EM COLUNAS VERTICAIS */
    .corr-container { display: flex; gap: 25px; justify-content: flex-end; width: 60%; text-align: right; }
    .corr-col { display: flex; flex-direction: column; gap: 2px; }
    .v-peq { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .v-extra { font-size: 12px; font-family: 'Chakra Petch'; font-weight: 400; color: #ffff00; opacity: 0.6; }

    /* SINAL MICRO PISCANTE */
    .micro-box { text-align: right; padding: 2px 15px 15px 15px; font-family: 'Chakra Petch'; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
    .piscante { animation: blink 0.7s infinite; }
    
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }

    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; min-height: 120px; }
    .note-title { font-size: 9px; color: #444; letter-spacing: 2px; margin-bottom: 8px; font-weight: 900; border-bottom: 1px solid #111; padding-bottom: 4px; }
    .note-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; line-height: 1.5; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 160px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE DADOS
def get_clean_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
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
    
    if s_m["last"] > 0:
        spot = s_m["last"]
        spr = d_m["var"] - e_m["var"]
        paridade = v_global["ajuste"] * (1 + (spr/100))
        equilibrio = round((v_global["ref"] + 0.0220) * 2000) / 2000
        
        # MACRO
        if spot < (paridade - 0.0015): m_msg, m_clr = "● PRECIFICAÇÃO DE ALTA", "#00aa55"
        elif spot > (paridade + 0.0015): m_msg, m_clr = "● PRECIFICAÇÃO DE BAIXA", "#aa3333"
        else: m_msg, m_clr = "● PRECIFICAÇÃO NEUTRA", "#aaaa00"
            
        # MICRO
        diff_pts = (spot - equilibrio) * 1000
        is_piscando = ""
        if diff_pts >= 22: mic_txt, mic_clr, is_piscando = "DÓLAR MUITO CARO", "#ff0000", "piscante"
        elif diff_pts >= 11: mic_txt, mic_clr, is_piscando = "DÓLAR CARO", "#ff6600", "piscante"
        elif diff_pts <= -22: mic_txt, mic_clr, is_piscando = "DÓLAR MUITO BARATO", "#00ff00", "piscante"
        elif diff_pts <= -11: mic_txt, mic_clr, is_piscando = "DÓLAR BARATO", "#00cc66", "piscante"
        else: mic_txt, mic_clr, is_piscando = "DÓLAR CONSOLIDADO", "#555555", ""

        with ui_area.container():
            if st.session_state.user_type == "ADM":
                with st.expander("PAINEL ADM"):
                    with st.form("adm"):
                        c1, c2 = st.columns(2)
                        v_global["ajuste"] = c1.number_input("PARIDADE", value=v_global["ajuste"], format="%.4f")
                        v_global["ref"] = c2.number_input("REF INST", value=v_global["ref"], format="%.4f")
                        v_global["notas_mural"] = st.text_area("MORNING CALL", value=v_global["notas_mural"])
                        v_global["notas"] = st.text_input("RODAPÉ 1", value=v_global["notas"])
                        if st.form_submit_button("SALVAR"): st.rerun()

            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR PRO</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {m_clr}77"><div class="s-text" style="color:{m_clr}">{m_msg}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row"><div class="data-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="data-label">PREÇO EQUILÍBRIO</div><div class="d-value c-equi">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)

            # REGIÃO DE CORREÇÃO VERTICAL
            st.markdown(f"""
            <div class="d-row" style="padding-top:10px; border-bottom: none; align-items: flex-start;">
                <div class="d-label" style="opacity:0.6; margin-top:5px;">REGIÃO DE CORREÇÃO</div>
                <div class="corr-container">
                    <div class="corr-col">
                        <span class="v-peq">{(equilibrio - 0.0110):.4f}</span>
                        <span class="v-extra">{(equilibrio - 0.0220):.4f}</span>
                    </div>
                    <div class="corr-col">
                        <span class="v-peq">{(equilibrio + 0.0110):.4f}</span>
                        <span class="v-extra">{(equilibrio + 0.0220):.4f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # SINAL MICRO
            st.markdown(f'<div class="micro-box {is_piscando}" style="color:{mic_clr}">{mic_txt}</div>', unsafe_allow_html=True)

            # MURAL
            st.markdown(f'<div class="note-box"><div class="note-title">MORNING CALL & AGENDA</div><div class="note-content">{v_global["notas_mural"].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)

            # TICKER RODAPÉ
            def f_tk(n, d):
                c = "#00aa55" if d["var"] >= 0 else "#aa3333"
                return f"<span class='tk-item'><b>{n}</b> {d['last']:.4f} <span style='color:{c}'>({d['var']:+.2f}%)</span></span>"
            
            btk = f"{f_tk('SPOT', s_m)} {f_tk('DXY', d_m)} {f_tk('EWZ', e_m)}"
            st.markdown(f'<div class="f-bar"><div style="color:#ffff99; font-size:11px;">{v_global["notas"]}</div><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
