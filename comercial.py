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
    st.session_state.notas_mural = "AGUARDANDO ATUALIZAÇÃO..."
    st.session_state.notas = "MURAL: AGUARDANDO..."
    st.session_state.notas2 = "INFORMATIVO: OPERACIONAL ATIVO"

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
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 12px; font-weight: 700; letter-spacing: 2px; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 75px; display: flex; flex-direction: column; }
    .sub-l { font-size: 8px; color: #888; margin-bottom: 2px; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .v-futuro-discreto { font-size: 16px; color: #444; font-family: 'Chakra Petch'; font-weight: 700; }
    .v-peq { font-size: 16px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .v-extra { font-size: 13px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; opacity: 0.4; margin-top: 2px; }

    .micro-container { text-align: right; padding: 0 15px 15px 0; font-family: 'Chakra Petch'; font-size: 10px; font-weight: 700; }
    @keyframes blinker { 50% { opacity: 0; } }
    .blink-text { animation: blinker 0.8s linear infinite; }

    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; min-height: 120px; }
    .note-title { font-size: 9px; color: #444; letter-spacing: 2px; margin-bottom: 8px; font-weight: 900; border-bottom: 1px solid #111; padding-bottom: 4px; }
    .note-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; line-height: 1.5; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 160px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .f-notes { font-family: 'Chakra Petch'; font-size: 11px; color: #ffff99; margin-bottom: 4px; text-transform: uppercase; }
    .f-notes2 { font-family: 'Chakra Petch'; font-size: 10px; color: #aaaaaa; margin-bottom: 8px; }
    .f-arrows { font-size: 16px; margin: 5px 0; letter-spacing: 8px; }
    .f-line { width: 85%; height: 1px; background: rgba(255,255,255,0.1); }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

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
        dol_futuro = spot + (st.session_state.fraldao / 1000)
        
        # AJUSTE DA PARIDADE (Removido sinal negativo invertido)
        # Cálculo: Ajuste * (1 + (DXY% + EWZ%)/100) -> Paridade direta
        correlacao_global = (d_m["var"] + e_m["var"]) 
        pari_val = st.session_state.ajuste * (1 + (correlacao_global / 100))
        
        equilibrio = round((st.session_state.ref + 0.0220) * 2000) / 2000
        
        # SINAL MICRO BASEADO NO FUTURO
        diff_pts = (dol_futuro - equilibrio) * 1000
        blink = ""
        if diff_pts >= 22: mic_msg, mic_clr, blink = "DÓLAR MUITO CARO", "#ff0000", "blink-text"
        elif diff_pts >= 11: mic_msg, mic_clr, blink = "DÓLAR CARO", "#ff6600", "blink-text"
        elif diff_pts <= -22: mic_msg, mic_clr, blink = "DÓLAR MUITO BARATO", "#00ff00", "blink-text"
        elif diff_pts <= -11: mic_msg, mic_clr, blink = "DÓLAR BARATO", "#00cc66", "blink-text"
        else: mic_msg, mic_clr, blink = "DÓLAR CONSOLIDADO", "#444444", ""

        with ui_area.container():
            # PAINEL ADM
            with st.expander("PAINEL ADM"):
                with st.form("adm_panel"):
                    c1, c2, c3 = st.columns(3)
                    st.session_state.ajuste = c1.number_input("PARIDADE", value=st.session_state.ajuste, format="%.4f")
                    st.session_state.ref = c2.number_input("REF INST", value=st.session_state.ref, format="%.4f")
                    st.session_state.fraldao = c3.number_input("PONTOS FUTURO", value=st.session_state.fraldao)
                    st.session_state.notas_mural = st.text_area("MORNING CALL", value=st.session_state.notas_mural)
                    if st.form_submit_button("SALVAR"): st.rerun()

            st.markdown('<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR PRO</span></div></div>', unsafe_allow_html=True)
            
            # BLOCO DE PARIDADE E EQUILIBRIO
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{abs(pari_val):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)
            
            # FUTURO DISCRETO
            st.markdown(f'<div class="d-row" style="border-bottom:none; padding: 5px 15px;"><div class="d-label" style="color:#333">DÓLAR FUTURO</div><div class="v-futuro-discreto">{dol_futuro:.4f}</div></div>', unsafe_allow_html=True)
            
            # CORREÇÃO VERTICAL (COLUNAS)
            st.markdown(f"""
            <div class="d-row" style="padding-top:10px; border-bottom: none; align-items: flex-start;">
                <div class="d-label" style="opacity:0.6; margin-top:5px;">REGIÃO DE CORREÇÃO</div>
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

            # SINAL MICRO
            st.markdown(f'<div class="micro-container"><span class="{blink}" style="color:{mic_clr}">{mic_msg}</span></div>', unsafe_allow_html=True)

            # MURAL
            st.markdown(f'<div class="note-box"><div class="note-title">MORNING CALL & AGENDA</div><div class="note-content">{st.session_state.notas_mural.replace("/n", "<br>")}</div></div>', unsafe_allow_html=True)

            # RODAPÉ
            def f_tk(d, n):
                c = "#00aa55" if d["var"] >= 0 else "#aa3333"
                return f"<span class='tk-item'><b>{n}</b> {d['last']:.4f} <span style='color:{c}'>({d['var']:+.2f}%)</span></span>"

            btk = f"{f_tk(s_m,'SPOT')} {f_tk(d_m,'DXY')} {f_tk(e_m,'EWZ')}"
            st.markdown(f'<div class="f-bar"><div class="f-line"></div><div class="f-arrows" style="color:{mic_clr}">{mic_msg}</div><div class="f-line"></div><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
