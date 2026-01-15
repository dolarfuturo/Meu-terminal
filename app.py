import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL (ADM)
if 'ajuste' not in st.session_state:
    st.session_state.ajuste = 5.4000
    st.session_state.ref = 5.4000
    st.session_state.mural = ""

# 3. ACESSO
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
            elif senha == "trader123":
                st.session_state.auth = True
                st.session_state.user_type = "USER"
                st.rerun()
    st.stop()

# 4. CSS DO VELOCÍMETRO E LAYOUT
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    .t-header { text-align: center; padding: 15px 0 5px 0; }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    .spot-destaque { font-size: 60px; color: #fff; font-weight: 900; font-family: 'Chakra Petch'; margin: 0; line-height: 1; text-shadow: 0 0 20px rgba(255,255,255,0.2); }
    
    /* VELOCÍMETRO / TERMÔMETRO */
    .v-wrap { width: 85%; margin: 15px auto; padding: 3px; background: #111; border-radius: 50px; border: 1px solid #333; box-shadow: inset 0 0 10px #000; }
    .v-fill { height: 10px; border-radius: 50px; transition: width 0.8s cubic-bezier(0.17, 0.67, 0.83, 0.67); box-shadow: 0 0 15px; }
    
    .s-container { text-align: center; padding: 10px 0; margin-top: 5px; }
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
    
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 50px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 9999; }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; }
    .tk-move { display: inline-block; animation: slide 45s linear infinite; }
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
    except: return {"last": 0.0, "prev": 0.0, "var": 0.0}

# PAINEL ADM
if st.session_state.user_type == "ADM":
    with st.expander("⚙️ CONFIGURAÇÕES MESTRE"):
        with st.form("adm_form"):
            c1, c2 = st.columns(2)
            st.session_state.ajuste = c1.number_input("PARIDADE", value=st.session_state.ajuste, format="%.4f")
            st.session_state.ref = c2.number_input("REF INST", value=st.session_state.ref, format="%.4f")
            st.session_state.mural = st.text_input("MENSAGEM MURAL", value=st.session_state.mural)
            if st.form_submit_button("ATUALIZAR"): st.rerun()

ui_area = st.empty()

while True:
    d_m, e_m, s_m, eu_m = get_clean_data("DX-Y.NYB"), get_clean_data("EWZ"), get_clean_data("BRL=X"), get_clean_data("EURUSD=X")
    
    if d_m["last"] > 0:
        spot = s_m["last"]
        spr = d_m["var"] - e_m["var"]
        justo = round((spot + 0.0310) * 2000) / 2000
        equi = round((st.session_state.ref + 0.0220) * 2000) / 2000
        
        # LÓGICA DO VELOCÍMETRO (Pressão de 0 a 100%)
        dif_pts = abs(spot - equi) * 1000
        perc = min(max(dif_pts * 4, 2), 100) # 25 pts = 100% da barra
        
        diff_j = spot - justo
        if diff_j < -0.0015: msg, clr = "● PRECIFICAÇÃO DE ALTA", "#00ff88"
        elif diff_j > 0.0015: msg, clr = "● PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: msg, clr = "● PRECIFICAÇÃO NEUTRA", "#ffff00"
            
        with ui_area.container():
            st.markdown(f"""
                <div class="t-header">
                    <div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div>
                    <div class="spot-destaque">{spot:.4f}</div>
                    <div class="v-wrap">
                        <div class="v-fill" style="width: {perc}%; background: {clr}; box-shadow: 0 0 15px {clr};"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {clr}44"><div class="s-text" style="color:{clr}">{msg}</div></div>', unsafe_allow_html=True)
            
            # PREÇOS CALCULADOS
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{(st.session_state.ajuste*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equi:.4f}</div></div>', unsafe_allow_html=True)
            
            # JUSTO E REF
            for label, v1, v2, v3, c1, c2, c3 in [
                ("PREÇO JUSTO", (round((spot+0.0220)*2000)/2000), justo, (round((spot+0.0420)*2000)/2000), "#cc3333", "#0066cc", "#00cc66"),
                ("REF. INSTITUCIONAL", (round((st.session_state.ref+0.0220)*2000)/2000), (round((st.session_state.ref+0.0310)*2000)/2000), (round((st.session_state.ref+0.0420)*2000)/2000), "#cc3333", "#0066cc", "#00cc66")
            ]:
                st.markdown(f'<div class="d-row"><div class="d-label">{label}</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v" style="color:{c1}">{v1:.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v" style="color:{c2}">{v2:.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v" style="color:{c3}">{v3:.4f}</span></div></div></div>', unsafe_allow_html=True)

            # REGIÃO CORREÇÃO
            st.markdown(f'<div class="d-row" style="border-bottom:none;"><div class="d-label">REGIÃO DE CORREÇÃO</div><div class="sub-grid"><div class="sub-item"><span class="v-peq">{(equi-0.0110):.4f}</span><span class="v-extra">{(equi-0.0220):.4f}</span></div><div class="sub-item"><span class="v-peq">{(equi+0.0110):.4f}</span><span class="v-extra">{(equi+0.0220):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # RODAPÉ TICKER
            def f_tk(d, n):
                v, p = d["var"], d["last"]
                c = "#00ff88" if v >= 0 else "#ff3333"
                pf = f"{p:.4f}" if n == "SPOT" else f"{p:.2f}"
                return f"<span class='tk-item'><b>{n}</b> {pf} <span style='color:{c}'>({v:+.2f}%)</span></span>"

            mural = f"<span class='tk-item'><b>MURAL:</b> {st.session_state.mural}</span>" if st.session_state.mural else ""
            btk = f"{f_tk(s_m,'SPOT')} {f_tk(d_m,'DXY')} {f_tk(e_m,'EWZ')} {f_tk(eu_m,'EURUSD')} <span class='tk-item'><b>SPREAD</b> {spr:+.2f}%</span> {mural}"
            st.markdown(f'<div class="f-bar"><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
