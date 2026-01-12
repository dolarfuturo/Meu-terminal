import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
if "ajuste" not in st.session_state:
    st.session_state.ajuste = 5.4000
    st.session_state.ref = 5.4000
    st.session_state.fraldao = 15.0
    st.session_state.notas_mural = "RESUMO DA ABERTURA E AGENDA: AGUARDANDO..."

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'], label { display: none !important; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:150px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="CHAVE DE ACESSO")
        if st.button("ENTRAR"):
            if senha == "admin123":
                st.session_state.auth = True
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
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .v-fut-discreto { font-size: 16px; color: #666; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .sub-grid { display: flex; gap: 20px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; display: flex; flex-direction: column; min-width: 85px; }
    .v-peq { font-size: 16px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .v-extra { font-size: 13px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; opacity: 0.5; margin-top: 4px; }

    .micro-container { text-align: right; padding: 0 15px 15px 0; font-family: 'Chakra Petch'; font-size: 10px; font-weight: 700; }
    @keyframes blinker { 50% { opacity: 0; } }
    .blink-text { animation: blinker 0.8s linear infinite; }
    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; min-height: 120px; }
    .note-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

def get_clean_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        return float(df['Close'].iloc[-1]) if not df.empty else 0.0
    except: return 0.0

# 5. LOOP DE EXECUÇÃO
ui_area = st.empty()
while True:
    spot = get_clean_data("BRL=X")
    
    if spot > 0:
        # CÁLCULO DÓLAR FUTURO (USA O FRALDÃO DO ADM)
        dol_futuro = spot + (st.session_state.fraldao / 1000)
        equilibrio = round((st.session_state.ref + 0.0220) * 2000) / 2000
        
        # GATILHO DO SINAL MICRO (FUTURO VS EQUILÍBRIO)
        diff_pts = (dol_futuro - equilibrio) * 1000
        blink_class = ""
        if diff_pts >= 22: mic_msg, mic_clr, blink_class = "DÓLAR MUITO CARO", "#ff0000", "blink-text"
        elif diff_pts >= 11: mic_msg, mic_clr, blink_class = "DÓLAR CARO", "#ff6600", "blink-text"
        elif diff_pts <= -22: mic_msg, mic_clr, blink_class = "DÓLAR MUITO BARATO", "#00ff00", "blink-text"
        elif diff_pts <= -11: mic_msg, mic_clr, blink_class = "DÓLAR BARATO", "#00cc66", "blink-text"
        else: mic_msg, mic_clr, blink_class = "DÓLAR CONSOLIDADO", "#444444", ""

        with ui_area.container():
            with st.expander("PAINEL ADM"):
                with st.form("adm_panel"):
                    c1, c2 = st.columns(2)
                    st.session_state.ref = c1.number_input("REFERÊNCIA", value=st.session_state.ref, format="%.4f")
                    st.session_state.fraldao = c2.number_input("FRALDÃO (PONTOS)", value=st.session_state.fraldao)
                    st.session_state.notas_mural = st.text_area("NOTAS MURAL", value=st.session_state.notas_mural)
                    if st.form_submit_button("ATUALIZAR"): st.rerun()

            st.markdown('<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR PRO</span></div></div>', unsafe_allow_html=True)
            
            # BLOCO PRINCIPAL
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO FUTURO DISCRETO
            st.markdown(f'<div class="d-row" style="border-bottom:none; padding: 5px 15px;"><div class="d-label" style="color:#333">DÓLAR FUTURO</div><div class="v-fut-discreto">{dol_futuro:.4f}</div></div>', unsafe_allow_html=True)

            # REGIÃO DE CORREÇÃO (VERTICAL)
            st.markdown(f"""
            <div class="d-row" style="padding-top:10px; border-bottom: none; align-items: flex-start;">
                <div class="d-label" style="opacity:0.5; margin-top:5px;">REGIÃO DE CORREÇÃO</div>
                <div class="sub-grid">
                    <div class="sub-item">
                        <span class="v-peq">{(equilibrio - 0.0110):.4f}</span>
                        <span class="v-extra">{(equilibrio - 0.0220):.4f}</span>
                    </div>
                    <div class="sub-item">
                        <span class="v-peq">{(equilibrio + 0.0110):.4f}</span>
                        <span class="v-extra">{(equilibrio + 0.0220):.4f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # SINAL (PISCANTE)
            st.markdown(f'<div class="micro-container"><span class="{blink_class}" style="color:{mic_clr}">{mic_msg}</span></div>', unsafe_allow_html=True)

            # MURAL
            st.markdown(f'<div class="note-box"><div class="note-content">{st.session_state.notas_mural}</div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
