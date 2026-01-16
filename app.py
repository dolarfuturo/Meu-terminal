import streamlit as st
import yfinance as yf
import time

# 1. SETUP DE PÁGINA (Impedir falha de carregamento)
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. VARIÁVEIS DE MEMÓRIA
for key, val in {
    'ptax': 5.4000, 'fech': 5.4000, 'ref': 5.4000, 
    'ajuste': 5.4000, 'auth': False
}.items():
    if key not in st.session_state: st.session_state[key] = val

# 3. LOGIN RÁPIDO
if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    senha = st.text_input("CHAVE", type="password")
    if st.button("ENTRAR"):
        if senha == "admin123": 
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. SIDEBAR (ENGRENAGEM)
with st.sidebar:
    st.header("⚙️ VARIÁVEIS")
    st.session_state.ptax = st.number_input("PTAX", value=st.session_state.ptax, format="%.4f")
    st.session_state.fech = st.number_input("FECHAMENTO", value=st.session_state.fech, format="%.4f")
    st.session_state.ref = st.number_input("REF. INST", value=st.session_state.ref, format="%.4f")
    st.session_state.ajuste = st.number_input("PARIDADE", value=st.session_state.ajuste, format="%.4f")
    if st.button("SALVAR"): st.rerun()

# 5. CSS BLINDADO (Sem dependências externas que causam tela preta)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    
    .t-header { text-align: center; padding-top: 10px; }
    .t-title { font-size: 24px; letter-spacing: 5px; font-weight: 300; } 
    .t-bold { font-weight: 900; } 
    .t-line { width: 60%; height: 1px; background: #333; margin: 8px auto 10px auto; }
    
    .gauge-container { position: relative; width: 160px; height: 80px; margin: 0 auto; overflow: hidden; }
    .gauge-bg { position: absolute; top: 0; left: 0; width: 160px; height: 160px; border-radius: 50%; background: conic-gradient(#ff3333 0deg 60deg, #ffff00 60deg 120deg, #00ff88 120deg 180deg, #000 180deg); transform: rotate(-90deg); }
    .gauge-cover { position: absolute; top: 12px; left: 12px; width: 136px; height: 136px; background: #000; border-radius: 50%; }
    .gauge-needle { position: absolute; bottom: 0; left: 50%; width: 2px; height: 70px; background: #fff; transform-origin: bottom center; transition: transform 0.8s ease; }

    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-bottom: 1px solid #111; }
    .d-label { font-size: 10px; font-weight: 900; color: #777; }
    .d-value { font-size: 21px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .corr-box { display: flex; flex-direction: column; align-items: center; font-family: 'Chakra Petch'; font-size: 15px; }
    .val-11 { font-weight: 700; color: #ffff00; }
    .val-22 { font-weight: 400; color: #ffff00; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #050505; border-top: 1px solid #222; overflow: hidden; }
    .tk-move { white-space: nowrap; animation: move 40s linear infinite; display: flex; align-items: center; height: 100%; }
    .tk-item { padding-right: 50px; font-family: 'Chakra Petch'; font-size: 11px; }
    @keyframes move { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

main_ui = st.empty()

while True:
    try:
        # Busca de dados com timeout para não travar
        ticker = yf.Ticker("BRL=X")
        data = ticker.history(period="1d", interval="1m")
        s_p = data['Close'].iloc[-1] if not data.empty else 0.0
        s_v = ((s_p / ticker.fast_info.previous_close) - 1) * 100 if s_p > 0 else 0.0
    except:
        s_p, s_v = 0.0, 0.0

    if s_p > 0:
        memoria = (st.session_state.ptax + st.session_state.fech) / 2
        diff = ((s_p / memoria) - 1) * 100
        angle = max(min(diff * 140, 90), -90)
        
        with main_ui.container():
            st.markdown(f"""
                <div class='t-header'>
                    <div class='t-title'>TERMINAL <span class='t-bold'>DÓLAR</span></div>
                    <div class='t-line'></div>
                    <div style='font-family:Chakra Petch; font-size:20px; font-weight:700;'>
                        {s_p:.4f} <span style='color:{"#00ff88" if s_v >= 0 else "#ff3333"}'>{s_v:+.2f}%</span>
                    </div>
                    <div class="gauge-container">
                        <div class="gauge-bg"></div>
                        <div class="gauge-cover"></div>
                        <div class="gauge-needle" style="transform: translateX(-50%) rotate({angle}deg);"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{st.session_state.ajuste:.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO JUSTO SPOT
            st.markdown(f"""<div class="d-row"><div class="d-label">PREÇO JUSTO SPOT</div><div style="display:flex; gap:15px;">
                <div style="text-align:center"><small>MIN</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#ff3333">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div>
                <div style="text-align:center"><small>JUSTO</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#0066cc">{(round((s_p+0.0310)*2000)/2000):.4f}</span></div>
                <div style="text-align:center"><small>MAX</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#00ff88">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div>
            </div></div>""", unsafe_allow_html=True)

            # REF INSTITUCIONAL
            st.markdown(f"""<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div style="display:flex; gap:15px;">
                <div style="text-align:center"><small>MIN</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#ff3333">{(round((st.session_state.ref+0.0220)*2000)/2000):.4f}</span></div>
                <div style="text-align:center"><small>JUSTO</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#0066cc">{(round((st.session_state.ref+0.0310)*2000)/2000):.4f}</span></div>
                <div style="text-align:center"><small>MAX</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#00ff88">{(round((st.session_state.ref+0.0420)*2000)/2000):.4f}</span></div>
            </div></div>""", unsafe_allow_html=True)

            # REGIÕES DE CORREÇÃO (EMPILHADO)
            st.markdown(f"""<div class="d-row"><div class="d-label">REGIÕES DE CORREÇÃO</div>
                <div style="display:flex; gap:40px;">
                    <div class="corr-box">
                        <span class="val-11">{(st.session_state.ref-0.0110):.4f}</span>
                        <span class="val-22">{(st.session_state.ref-0.0220):.4f}</span>
                    </div>
                    <div class="corr-box">
                        <span class="val-11">{(st.session_state.ref+0.0110):.4f}</span>
                        <span class="val-22">{(st.session_state.ref+0.0220):.4f}</span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # TICKER
            t_txt = f"SPOT: {s_p:.4f} ({s_v:+.2f}%) | PTAX: {st.session_state.ptax:.4f} | FECH: {st.session_state.fech:.4f}"
            st.markdown(f"<div class='f-bar'><div class='tk-move'><span class='tk-item'>{t_txt}</span><span class='tk-item'>{t_txt}</span></div></div>", unsafe_allow_html=True)
    else:
        main_ui.info("Conectando ao mercado...")

    time.sleep(2)
