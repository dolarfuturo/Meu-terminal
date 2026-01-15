import streamlit as st
import yfinance as yf
import time

# 1. SETUP
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. VARIÁVEIS DE MEMÓRIA
if 'ptax' not in st.session_state: st.session_state.ptax = 5.4000
if 'fech' not in st.session_state: st.session_state.fech = 5.4000
if 'ref' not in st.session_state: st.session_state.ref = 5.4000
if 'ajuste' not in st.session_state: st.session_state.ajuste = 5.4000
if 'auth' not in st.session_state: st.session_state.auth = False

# 3. LOGIN
if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'] { display: none; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:120px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("CHAVE DE ACESSO", type="password")
        if st.button("ENTRAR"):
            if senha == "admin123": st.session_state.auth = True; st.rerun()
    st.stop()

# 4. SIDEBAR - SET DE VARIÁVEIS (PTAX E FECHAMENTO)
with st.sidebar:
    st.header("SET VARIÁVEIS")
    st.session_state.ptax = st.number_input("PTAX", value=st.session_state.ptax, format="%.4f")
    st.session_state.fech = st.number_input("FECHAMENTO", value=st.session_state.fech, format="%.4f")
    st.session_state.ref = st.number_input("REF. INST", value=st.session_state.ref, format="%.4f")
    st.session_state.ajuste = st.number_input("PARIDADE", value=st.session_state.ajuste, format="%.4f")
    if st.button("SALVAR"): st.rerun()

# 5. CSS ORIGINAL + VELOCÍMETRO EM HTML PURO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; overflow: hidden; }
    
    .t-header { text-align: center; padding: 10px 0; }
    .t-title { font-size: 22px; letter-spacing: 4px; font-weight: 900; margin-bottom: 10px; }
    
    /* VELOCÍMETRO CSS */
    .gauge-container { position: relative; width: 180px; height: 90px; margin: 0 auto; overflow: hidden; }
    .gauge-bg { position: absolute; top: 0; left: 0; width: 180px; height: 180px; border-radius: 50%; background: conic-gradient(#ff3333 0deg 60deg, #ffff00 60deg 120deg, #00ff88 120deg 180deg, #000 180deg); transform: rotate(-90deg); }
    .gauge-cover { position: absolute; top: 15px; left: 15px; width: 150px; height: 150px; background: #000; border-radius: 50%; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 75px; }
    .gauge-needle { position: absolute; bottom: 0; left: 50%; width: 3px; height: 80px; background: #fff; transform-origin: bottom center; transition: transform 0.8s cubic-bezier(0.65, 0, 0.35, 1); box-shadow: 0 0 10px #fff; }
    .gauge-value { position: absolute; bottom: 5px; width: 100%; text-align: center; font-family: 'Chakra Petch'; font-size: 14px; font-weight: 700; }

    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; font-weight: 900; color: #888; text-transform: uppercase; }
    .d-value { font-size: 22px; font-family: 'Chakra Petch'; font-weight: 700; }
    .sub-v { font-size: 17px; font-family: 'Chakra Petch'; font-weight: 700; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 999; }
    .tk-move { white-space: nowrap; animation: move 40s linear infinite; }
    .tk-item { display: inline-block; padding-right: 50px; font-family: 'Chakra Petch'; font-size: 11px; }
    @keyframes move { from { transform: translateX(0); } to { transform: translateX(-50%); } }
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

main_area = st.empty()

while True:
    s_p, s_v = get_live("BRL=X")
    dx_p, dx_v = get_live("DX-Y.NYB")
    ew_p, ew_v = get_live("EWZ")
    
    if s_p > 0:
        # LÓGICA DO VELOCÍMETRO: SPOT vs MÉDIA PTAX/FECH
        memoria = (st.session_state.ptax + st.session_state.fech) / 2
        diff = ((s_p / memoria) - 1) * 100
        # needle_angle: -90deg (vermelho) a +90deg (verde)
        angle = max(min(diff * 150, 90), -90) 
        
        spr = dx_v - ew_v
        justo = round((s_p + 0.0310) * 2000) / 2000

        with main_area.container():
            # 1. TÍTULO E VELOCÍMETRO CSS
            st.markdown(f"""
                <div class='t-header'>
                    <div class='t-title'>TERMINAL DÓLAR</div>
                    <div class="gauge-container">
                        <div class="gauge-bg"></div>
                        <div class="gauge-cover"></div>
                        <div class="gauge-needle" style="transform: translateX(-50%) rotate({angle}deg);"></div>
                        <div class="gauge-value">{diff:+.2f}%</div>
                    </div>
                    <div style="font-size: 10px; color: #555; margin-top: 5px;">SPOT vs PTAX/FECH</div>
                </div>
            """, unsafe_allow_html=True)

            # 2. ESTRUTURA ORIGINAL
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{(st.session_state.ajuste*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f"""<div class="d-row"><div class="d-label">PREÇO JUSTO SPOT</div><div style="display:flex; gap:15px;">
                <div style="text-align:center"><small>MIN</small><br><span class="sub-v" style="color:#ff3333">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div>
                <div style="text-align:center"><small>JUSTO</small><br><span class="sub-v" style="color:#0066cc">{justo:.4f}</span></div>
                <div style="text-align:center"><small>MAX</small><br><span class="sub-v" style="color:#00ff88">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div>
            </div></div>""", unsafe_allow_html=True)

            st.markdown(f"""<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div style="display:flex; gap:15px;">
                <div style="text-align:center"><small>MIN</small><br><span class="sub-v" style="color:#ff3333">{(round((st.session_state.ref+0.0220)*2000)/2000):.4f}</span></div>
                <div style="text-align:center"><small>JUSTO</small><br><span class="sub-v" style="color:#0066cc">{(round((st.session_state.ref+0.0310)*2000)/2000):.4f}</span></div>
                <div style="text-align:center"><small>MAX</small><br><span class="sub-v" style="color:#00ff88">{(round((st.session_state.ref+0.0420)*2000)/2000):.4f}</span></div>
            </div></div>""", unsafe_allow_html=True)

            st.markdown(f'<div class="d-row" style="border-bottom:none;"><div class="d-label">MEMÓRIAS SET</div><div class="d-value" style="font-size:16px;">PTAX: {st.session_state.ptax:.4f} | FECH: {st.session_state.fech:.4f}</div></div>', unsafe_allow_html=True)

            # 3. RODAPÉ (TICKER)
            def c(v): return "#00ff88" if v >= 0 else "#ff3333"
            t_html = (f"<b>SPOT:</b> {s_p:.4f} <span style='color:{c(s_v)}'>({s_v:+.2f}%)</span> | "
                      f"<b>DXY:</b> {dx_p:.2f} <span style='color:{c(dx_v)}'>({dx_v:+.2f}%)</span> | "
                      f"<b>EWZ:</b> {ew_p:.2f} <span style='color:{c(ew_v)}'>({ew_v:+.2f}%)</span> | "
                      f"<b>SPREAD:</b> <span style='color:{c(spr)}'>{spr:+.2f}%</span>")
            st.markdown(f"<div class='f-bar'><div class='tk-move'><span class='tk-item'>{t_html}</span><span class='tk-item'>{t_html}</span></div></div>", unsafe_allow_html=True)

    time.sleep(2)
