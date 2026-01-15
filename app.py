import streamlit as st
import yfinance as yf
import time

# 1. SETUP
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. PERSISTÊNCIA DAS VARIÁVEIS (SET)
if 'ajuste' not in st.session_state: st.session_state.ajuste = 5.4000
if 'ref' not in st.session_state: st.session_state.ref = 5.4000
if 'auth' not in st.session_state: st.session_state.auth = False

# 3. ACESSO
if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'] { display: none; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:120px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("PASSWORD", type="password")
        if st.button("UNLOCK"):
            if senha in ["admin123", "trader123"]:
                st.session_state.auth = True
                st.rerun()
    st.stop()

# 4. PAINEL DE AJUSTES (SIDEBAR)
with st.sidebar:
    st.markdown("### CONFIGURAÇÕES")
    st.session_state.ajuste = st.number_input("PARIDADE", value=st.session_state.ajuste, format="%.4f")
    st.session_state.ref = st.number_input("REF INST", value=st.session_state.ref, format="%.4f")
    if st.button("SALVAR E ATUALIZAR"): st.rerun()

# 5. CSS REVISADO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; overflow: hidden; }
    
    .t-header { text-align: center; padding: 10px 0; border-bottom: 1px solid #111; }
    .t-title { font-size: 22px; letter-spacing: 4px; }
    .t-light { font-weight: 300; }
    .t-bold { font-weight: 900; }
    
    /* TERMÔMETRO REFINADO */
    .v-frame { width: 40%; height: 4px; background: #111; margin: 8px auto; border-radius: 5px; position: relative; border: 1px solid #222; }
    .v-bar { height: 100%; border-radius: 5px; transition: width 0.8s ease; box-shadow: 0 0 12px currentColor; }
    
    .spot-mini { font-family: 'Chakra Petch'; font-size: 15px; color: #999; margin-top: 4px; }
    .s-msg { font-size: 9px; font-weight: 700; letter-spacing: 2px; margin-top: 5px; }

    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 10px; font-weight: 900; }
    .d-value { font-size: 20px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .sub-v { font-size: 16px; font-family: 'Chakra Petch'; font-weight: 700; }

    /* TICKER */
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 999; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; white-space: nowrap; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 11px; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_live(ticker):
    try:
        t = yf.Ticker(ticker)
        d = t.history(period="1d", interval="1m")
        if d.empty: return 0.0, 0.0
        l = d['Close'].iloc[-1]
        v = ((l - t.fast_info.previous_close) / t.fast_info.previous_close * 100)
        return float(l), float(v)
    except: return 0.0, 0.0

display = st.empty()

while True:
    s_p, s_v = get_live("BRL=X")
    dx_p, dx_v = get_live("DX-Y.NYB")
    ew_p, ew_v = get_live("EWZ")
    eu_p, eu_v = get_live("EURUSD=X")
    
    if s_p > 0:
        spr = dx_v - ew_v
        justo = round((s_p + 0.0310) * 2000) / 2000
        equi = round((st.session_state.ref + 0.0220) * 2000) / 2000
        
        # Lógica Termômetro (Pressão baseada na variação do Spread)
        v_width = min(abs(spr) * 20, 100)
        
        diff = s_p - justo
        if diff < -0.0015: msg, clr = "● PRECIFICAÇÃO DE ALTA", "#00ff88"
        elif diff > 0.0015: msg, clr = "● PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: msg, clr = "● PRECIFICAÇÃO NEUTRA", "#ffff00"

        with display.container():
            # HEADER CENTRAL
            st.markdown(f"""
                <div class='t-header'>
                    <div class='t-title'><span class='t-light'>TERMINAL</span> <span class='t-bold'>DÓLAR</span></div>
                    <div class='v-frame'><div class='v-bar' style='width: {v_width}%; background: {clr}; color: {clr};'></div></div>
                    <div class='spot-mini'>{s_p:.4f} <span style='color:{"#00ff88" if s_v >= 0 else "#ff3333"}'>{s_v:+.2f}%</span></div>
                    <div class='s-msg' style='color:{clr}'>{msg}</div>
                </div>
            """, unsafe_allow_html=True)

            # GRIDS
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{(st.session_state.ajuste*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equi:.4f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="d-row">
                    <div class="d-label">PREÇO JUSTO</div>
                    <div style="display:flex; gap:15px;">
                        <div style="text-align:center"><small style="color:#555">MIN</small><br><span class="sub-v" style="color:#ff3333">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div>
                        <div style="text-align:center"><small style="color:#555">JUSTO</small><br><span class="sub-v" style="color:#0066cc">{justo:.4f}</span></div>
                        <div style="text-align:center"><small style="color:#555">MAX</small><br><span class="sub-v" style="color:#00ff88">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="d-row" style="border:none;">
                    <div class="d-label">REGIÃO DE CORREÇÃO</div>
                    <div style="display:flex; gap:20px;">
                        <div style="color:#ffff00; font-weight:700;">{(equi-0.0110):.4f} / {(equi-0.0220):.4f}</div>
                        <div style="color:#ffff00; font-weight:700;">{(equi+0.0110):.4f} / {(equi+0.0220):.4f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # TICKER COLORIDO
            def _c(v): return "#00ff88" if v >= 0 else "#ff3333"
            t_html = (
                f"<b>SPOT:</b> {s_p:.4f} <span style='color:{_c(s_v)}'>({s_v:+.2f}%)</span> &nbsp;&nbsp;&nbsp; "
                f"<b>DXY:</b> {dx_p:.2f} <span style='color:{_c(dx_v)}'>({dx_v:+.2f}%)</span> &nbsp;&nbsp;&nbsp; "
                f"<b>EWZ:</b> {ew_p:.2f} <span style='color:{_c(ew_v)}'>({ew_v:+.2f}%)</span> &nbsp;&nbsp;&nbsp; "
                f"<b>EUR:</b> {eu_p:.4f} <span style='color:{_c(eu_v)}'>({eu_v:+.2f}%)</span> &nbsp;&nbsp;&nbsp; "
                f"<b>SPREAD:</b> <span style='color:{_c(spr)}'>{spr:+.2f}%</span>"
            )
            st.markdown(f"<div class='f-bar'><div class='tk-move'><span class='tk-item'>{t_html}</span><span class='tk-item'>{t_html}</span></div></div>", unsafe_allow_html=True)

    time.sleep(2)
