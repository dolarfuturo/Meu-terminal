import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
if 'ajuste' not in st.session_state:
    st.session_state.ajuste = 5.4000
    st.session_state.ref = 5.4000
    st.session_state.mural = ""

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
            if senha == "admin123": st.session_state.auth, st.session_state.user_type = True, "ADM"; st.rerun()
            elif senha == "trader123": st.session_state.auth, st.session_state.user_type = True, "USER"; st.rerun()
    st.stop()

# 4. CSS FINAL (SEM ERROS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    .t-header { text-align: center; padding: 20px 0 10px 0; }
    .t-light { font-weight: 300; font-size: 26px; letter-spacing: 4px; color: #fff; }
    .t-bold { font-weight: 900; font-size: 26px; letter-spacing: 4px; color: #fff; }
    
    .spot-box { margin: 10px 0; }
    .spot-val { font-family: 'Chakra Petch'; font-size: 36px; font-weight: 700; }
    .spot-var { font-family: 'Chakra Petch'; font-size: 18px; margin-left: 10px; }

    /* VELOCÍMETRO */
    .v-frame { width: 65%; height: 10px; background: #111; border-radius: 20px; margin: 15px auto; border: 1px solid #333; overflow: hidden; }
    .v-bar { height: 100%; transition: width 0.8s ease; box-shadow: 0 0 15px currentColor; }
    
    .s-container { text-align: center; padding: 10px 0; border-bottom: 1px solid #111; }
    .s-text { font-size: 11px; font-weight: 700; letter-spacing: 2px; }
    
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; font-weight: 900; width: 40%; }
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; display: flex; flex-direction: column; }
    .sub-l { font-size: 8px; color: #888; margin-bottom: 2px; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .v-peq { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .v-extra { font-size: 12px; font-family: 'Chakra Petch'; font-weight: 400; color: #ffff00; opacity: 0.6; }
    .d-value { font-size: 24px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 50px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 9999; }
    .tk-move { display: inline-block; animation: slide 45s linear infinite; white-space: nowrap; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d", interval="1m")
        last = df['Close'].iloc[-1]
        prev = t.fast_info.previous_close
        var = ((last - prev) / prev * 100)
        return {"last": last, "var": var}
    except: return {"last": 0.0, "var": 0.0}

if st.session_state.user_type == "ADM":
    with st.expander("⚙️ PAINEL ADM"):
        with st.form("adm"):
            st.session_state.ajuste = st.number_input("PARIDADE", value=st.session_state.ajuste, format="%.4f")
            st.session_state.ref = st.number_input("REF INST", value=st.session_state.ref, format="%.4f")
            st.session_state.mural = st.text_input("MURAL", value=st.session_state.mural)
            if st.form_submit_button("SALVAR"): st.rerun()

ui_area = st.empty()

while True:
    d_m, e_m, s_m, eu_m = get_data("DX-Y.NYB"), get_data("EWZ"), get_data("BRL=X"), get_data("EURUSD=X")
    
    if d_m["last"] > 0:
        spot, spot_var = s_m["last"], s_m["var"]
        spr = d_m["var"] - e_m["var"]
        justo = round((spot + 0.0310) * 2000) / 2000
        equi = round((st.session_state.ref + 0.0220) * 2000) / 2000
        
        # VELOCÍMETRO
        dist = abs(spot - equi) * 1000
        v_width = min(dist * 4, 100)
        
        diff_j = spot - justo
        if diff_j < -0.0015: msg, clr = "● PRECIFICAÇÃO DE ALTA", "#00ff88"
        elif diff_j > 0.0015: msg, clr = "● PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: msg, clr = "● PRECIFICAÇÃO NEUTRA", "#ffff00"
            
        with ui_area.container():
            # HEADER CENTRALIZADO
            v_clr = "#00ff88" if spot_var >= 0 else "#ff3333"
            st.markdown(f"""
                <div class="t-header">
                    <div><span class="t-light">TERMINAL</span> <span class="t-bold">DÓLAR</span></div>
                    <div class="spot-box">
                        <span class="spot-val">{spot:.4f}</span>
                        <span class="spot-var" style="color:{v_clr}">{spot_var:+.2f}%</span>
                    </div>
                    <div class="v-frame">
                        <div class="v-bar" style="width: {v_width}%; background: {clr}; color: {clr};"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<div class="s-container"><div class="s-text" style="color:{clr}">{msg}</div></div>', unsafe_allow_html=True)
            
            # PREÇOS
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{(st.session_state.ajuste*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equi:.4f}</div></div>', unsafe_allow_html=True)
            
            # JUSTO
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v" style="color:#cc3333">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v" style="color:#0066cc">{justo:.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v" style="color:#00cc66">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            
            # REF
            st.markdown(f'<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v" style="color:#cc3333">{(round((st.session_state.ref+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v" style="color:#0066cc">{(round((st.session_state.ref+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v" style="color:#00cc66">{(round((st.session_state.ref+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # REGIÃO CORREÇÃO
            st.markdown(f"""
            <div class="d-row" style="border-bottom:none;">
                <div class="d-label">REGIÃO DE CORREÇÃO</div>
                <div class="sub-grid">
                    <div class="sub-item"><span class="v-peq">{(equi-0.0110):.4f}</span><span class="v-extra">{(equi-0.0220):.4f}</span></div>
                    <div class="sub-item"><span class="v-peq">{(equi+0.0110):.4f}</span><span class="v-extra">{(equi+0.0220):.4f}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # RODAPÉ
            btk = f"<span class='tk-item'><b>DXY</b> {d_m['last']:.2f} ({d_m['var']:+.2f}%)</span> <span class='tk-item'><b>EWZ</b> {e_m['last']:.2f} ({e_m['var']:+.2f}%)</span> <span class='tk-item'><b>EURUSD</b> {eu_m['last']:.4f}</span> <span class='tk-item'><b>SPREAD</b> {spr:+.2f}%</span> <span class='tk-item'><b>MURAL:</b> {st.session_state.mural}</span>"
            st.markdown(f'<div class="f-bar"><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
