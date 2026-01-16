import streamlit as st
import yfinance as yf
import time

# 1. SETUP
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. INICIALIZAÇÃO DE VARIÁVEIS
if 'ptax' not in st.session_state: st.session_state.ptax = 5.4000
if 'fech' not in st.session_state: st.session_state.fech = 5.4000
if 'ref' not in st.session_state: st.session_state.ref = 5.4000
if 'ajuste' not in st.session_state: st.session_state.ajuste = 5.4000
if 'show_settings' not in st.session_state: st.session_state.show_settings = False

# 3. CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    
    /* INPUTS DISCRETOS */
    .stNumberInput div div input {
        background-color: #111 !important;
        color: #fff !important;
        border: 1px solid #333 !important;
        font-size: 11px !important;
        height: 28px !important;
    }
    .stButton button {
        background-color: #111 !important;
        color: #777 !important;
        border: 1px solid #333 !important;
        font-size: 11px !important;
    }

    .t-header { text-align: center; padding-top: 5px; }
    .t-title { font-size: 24px; letter-spacing: 5px; font-weight: 300; } 
    .t-bold { font-weight: 900; } 
    .t-line { width: 60%; height: 1px; background: #333; margin: 8px auto 10px auto; }
    
    .gauge-container { position: relative; width: 160px; height: 80px; margin: 0 auto; overflow: hidden; }
    .gauge-bg { position: absolute; top: 0; left: 0; width: 160px; height: 160px; border-radius: 50%; background: conic-gradient(#ff3333 0deg 60deg, #ffff00 60deg 120deg, #00ff88 120deg 180deg, #000 180deg); transform: rotate(-90deg); }
    .gauge-cover { position: absolute; top: 12px; left: 12px; width: 136px; height: 136px; background: #000; border-radius: 50%; }
    .gauge-needle { position: absolute; bottom: 0; left: 50%; width: 2px; height: 70px; background: #fff; transform-origin: bottom center; transition: all 0.5s ease; }

    .btn-alerta { 
        width: 220px; margin: 10px auto; padding: 5px; border-radius: 4px; 
        font-size: 11px; font-weight: 900; text-align: center; letter-spacing: 2px;
    }

    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-bottom: 1px solid #111; }
    .d-label { font-size: 10px; font-weight: 900; color: #777; }
    .d-value { font-size: 21px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .corr-box { display: flex; flex-direction: column; align-items: center; font-family: 'Chakra Petch'; font-size: 15px; }
    .val-11 { font-weight: 700; color: #ffff00; }
    .val-22 { font-weight: 400; color: #ffff00; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 999; overflow: hidden; }
    .tk-move { white-space: nowrap; animation: move 30s linear infinite; display: flex; align-items: center; }
    .tk-item { padding-right: 50px; font-family: 'Chakra Petch'; font-size: 11px; font-weight: 700; }
    @keyframes move { from { transform: translateX(100%); } to { transform: translateX(-100%); } }
</style>
""", unsafe_allow_html=True)

# 4. BOTÃO DE ENTRAR/SAIR DAS VARIÁVEIS
col_btn, _ = st.columns([1, 10])
with col_btn:
    if st.button("⚙️ SET" if not st.session_state.show_settings else "✖ FECHAR"):
        st.session_state.show_settings = not st.session_state.show_settings
        st.rerun()

# 5. CAMPOS DE AJUSTE (SÓ APARECEM SE SHOW_SETTINGS FOR TRUE)
if st.session_state.show_settings:
    with st.container():
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.session_state.ptax = st.number_input("P", value=st.session_state.ptax, format="%.4f")
        with c2: st.session_state.fech = st.number_input("F", value=st.session_state.fech, format="%.4f")
        with c3: st.session_state.ref = st.number_input("R", value=st.session_state.ref, format="%.4f")
        with c4: st.session_state.ajuste = st.number_input("A", value=st.session_state.ajuste, format="%.4f")
        with c5: 
            st.write("<div style='height:25px;'></div>", unsafe_allow_html=True)
            if st.button("SALVAR"): 
                st.session_state.show_settings = False
                st.rerun()

main_area = st.empty()

while True:
    try:
        ticker_brl = yf.Ticker("BRL=X")
        s_p = ticker_brl.fast_info.last_price
        s_v = ((s_p / ticker_brl.fast_info.previous_close) - 1) * 100
        
        dxy_data = yf.Ticker("DX-Y.NYB").fast_info
        dx_p, dx_v = dxy_data.last_price, ((dxy_data.last_price / dxy_data.previous_close) - 1) * 100
        
        ewz_data = yf.Ticker("EWZ").fast_info
        ew_p, ew_v = ewz_data.last_price, ((ewz_data.last_price / ewz_data.previous_close) - 1) * 100
    except:
        s_p, s_v, dx_p, dx_v, ew_p, ew_v = 0, 0, 0, 0, 0, 0

    if s_p > 0:
        memoria = (st.session_state.ptax + st.session_state.fech) / 2
        diff = ((s_p / memoria) - 1) * 100
        angle = max(min(diff * 140, 90), -90)

        if diff > 0.10:
            alerta_text, alerta_clr = "PRECIFICAÇÃO DE ALTA", "#00ff88"
        elif diff < -0.10:
            alerta_text, alerta_clr = "PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else:
            alerta_text, alerta_clr = "PRECIFICAÇÃO NEUTRA", "#ffff00"

        with main_area.container():
            st.markdown(f"""
                <div class='t-header'>
                    <div class='t-title'>TERMINAL <span class='t-bold'>DÓLAR</span></div>
                    <div class='t-line'></div>
                    <div style='font-family:Chakra Petch; font-size:22px; font-weight:700;'>
                        {s_p:.4f} <span style='color:{"#00ff88" if s_v >= 0 else "#ff3333"}'>{s_v:+.2f}%</span>
                    </div>
                    <div class="gauge-container">
                        <div class="gauge-bg"></div>
                        <div class="gauge-cover"></div>
                        <div class="gauge-needle" style="transform: translateX(-50%) rotate({angle}deg);"></div>
                    </div>
                    <div class="btn-alerta" style="border: 1px solid {alerta_clr}; color: {alerta_clr};">
                        {alerta_text}
                    </div>
                </div>

                <div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{st.session_state.ajuste:.4f}</div></div>
                
                <div class="d-row"><div class="d-label">PREÇO JUSTO SPOT</div><div style="display:flex; gap:15px;">
                    <div style="text-align:center"><small>MIN</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#ff3333">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div>
                    <div style="text-align:center"><small>JUSTO</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#0066cc">{(round((s_p+0.0310)*2000)/2000):.4f}</span></div>
                    <div style="text-align:center"><small>MAX</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#00ff88">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div>
                </div></div>

                <div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div style="display:flex; gap:15px;">
                    <div style="text-align:center"><small>MIN</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#ff3333">{(round((st.session_state.ref+0.0220)*2000)/2000):.4f}</span></div>
                    <div style="text-align:center"><small>JUSTO</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#0066cc">{(round((st.session_state.ref+0.0310)*2000)/2000):.4f}</span></div>
                    <div style="text-align:center"><small>MAX</small><br><span style="font-family:Chakra Petch; font-weight:700; font-size:16px; color:#00ff88">{(round((st.session_state.ref+0.0420)*2000)/2000):.4f}</span></div>
                </div></div>

                <div class="d-row"><div class="d-label">REGIÕES DE CORREÇÃO</div>
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
                </div>
            """, unsafe_allow_html=True)

            def color_tick(v): return "#00ff88" if v >= 0 else "#ff3333"
            ticker_html = (
                f"<span class='tk-item'>SPOT: {s_p:.4f} <span style='color:{color_tick(s_v)}'>({s_v:+.2f}%)</span></span>"
                f"<span class='tk-item'>DXY: {dx_p:.2f} <span style='color:{color_tick(dx_v)}'>({dx_v:+.2f}%)</span></span>"
                f"<span class='tk-item'>EWZ: {ew_p:.2f} <span style='color:{color_tick(ew_v)}'>({ew_v:+.2f}%)</span></span>"
            )
            st.markdown(f"<div class='f-bar'><div class='tk-move'>{ticker_html}{ticker_html}</div></div>", unsafe_allow_html=True)

    time.sleep(2)
