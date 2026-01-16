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
if 'v22' not in st.session_state: st.session_state.v22 = 0.0220
if 'v31' not in st.session_state: st.session_state.v31 = 0.0310
if 'v42' not in st.session_state: st.session_state.v42 = 0.0420
if 'txt_topo' not in st.session_state: st.session_state.txt_topo = "FOCO NO PLANO - RESPEITE O STOP"
if 'show_settings' not in st.session_state: st.session_state.show_settings = False

# 3. CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    
    .stNumberInput div div input, .stTextInput div div input { 
        background-color: #111 !important; color: #fff !important; border: 1px solid #333 !important; font-size: 11px !important; 
    }
    .stButton button { background-color: #111 !important; color: #888 !important; border: 1px solid #333 !important; font-size: 10px !important; }

    .t-header { text-align: center; padding-top: 5px; }
    .t-title { font-size: 24px; letter-spacing: 5px; font-weight: 300; } 
    .t-bold { font-weight: 900; } 
    .t-line { width: 60%; height: 1px; background: #333; margin: 8px auto 10px auto; }
    
    .gauge-container { position: relative; width: 140px; height: 70px; margin: 0 auto; overflow: hidden; }
    .gauge-bg { position: absolute; top: 0; left: 0; width: 140px; height: 140px; border-radius: 50%; background: conic-gradient(#ff3333 0deg 60deg, #ffff00 60deg 120deg, #00ff88 120deg 180deg, #000 180deg); transform: rotate(-90deg); }
    .gauge-cover { position: absolute; top: 10px; left: 10px; width: 120px; height: 120px; background: #000; border-radius: 50%; }
    .gauge-needle { position: absolute; bottom: 0; left: 50%; width: 2px; height: 60px; background: #fff; transform-origin: bottom center; transition: all 0.5s ease; }

    .btn-alerta { width: 220px; margin: 8px auto; padding: 4px; border-radius: 4px; font-size: 10px; font-weight: 900; text-align: center; letter-spacing: 2px; }
    
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; font-weight: 900; color: #fff; text-transform: uppercase; }
    .d-value { font-size: 19px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .corr-box { display: flex; flex-direction: column; align-items: center; font-family: 'Chakra Petch'; font-size: 14px; }
    .val-11 { font-weight: 700; color: #ffff00; }
    .val-22 { font-weight: 400; color: #ffff00; }

    .txt-editavel { text-align: center; font-family: 'Chakra Petch'; font-size: 11px; color: #666; margin-top: 15px; margin-bottom: 45px; text-transform: uppercase; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 999; overflow: hidden; }
    .tk-move { white-space: nowrap; animation: move 35s linear infinite; display: flex; align-items: center; }
    .tk-item { padding-right: 40px; font-family: 'Chakra Petch'; font-size: 11px; font-weight: 700; }
    @keyframes move { from { transform: translateX(100%); } to { transform: translateX(-100%); } }
</style>
""", unsafe_allow_html=True)

# 4. BOTÃO SET E MENU (FORA DO LOOP PARA FUNCIONAR)
if st.button("⚙️ SET" if not st.session_state.show_settings else "✖ FECHAR"):
    st.session_state.show_settings = not st.session_state.show_settings

if st.session_state.show_settings:
    with st.container():
        st.markdown("### CONFIGURAÇÕES DO TERMINAL")
        c_p, c_v = st.columns(2)
        with c_p:
            st.write("**PREÇO**")
            st.session_state.ptax = st.number_input("PTAX", value=st.session_state.ptax, format="%.4f")
            st.session_state.ajuste = st.number_input("AJUSTE", value=st.session_state.ajuste, format="%.4f")
        with c_v:
            st.write("**VARIÁVEIS DE PONTOS**")
            st.session_state.v22 = st.number_input("VAR 22", value=st.session_state.v22, format="%.4f")
            st.session_state.v31 = st.number_input("VAR 31", value=st.session_state.v31, format="%.4f")
            st.session_state.v42 = st.number_input("VAR 42", value=st.session_state.v42, format="%.4f")
            st.session_state.txt_topo = st.text_input("FRASE", value=st.session_state.txt_topo)
        if st.button("SALVAR"):
            st.session_state.show_settings = False
            st.rerun()

# 5. ÁREA DO TERMINAL
placeholder = st.empty()

while True:
    if not st.session_state.show_settings:
        try:
            t_usd = yf.Ticker("BRL=X").fast_info
            s_p, s_v = t_usd.last_price, ((t_usd.last_price / t_usd.previous_close) - 1) * 100
            t_dx = yf.Ticker("DX-Y.NYB").fast_info
            dx_p, dx_v = t_dx.last_price, ((t_dx.last_price / t_dx.previous_close) - 1) * 100
            t_ewz = yf.Ticker("EWZ").fast_info
            ew_p, ew_v = t_ewz.last_price, ((t_ewz.last_price / t_ewz.previous_close) - 1) * 100
            t_eur = yf.Ticker("EURUSD=X").fast_info
            eu_p, eu_v = t_eur.last_price, ((t_eur.last_price / t_eur.previous_close) - 1) * 100
            spread = s_p - st.session_state.ptax
        except:
            s_p = s_v = dx_p = dx_v = ew_p = ew_v = eu_p = eu_v = spread = 0

        if s_p > 0:
            equi = st.session_state.ptax + st.session_state.v22
            diff_g = ((s_p / ((st.session_state.ptax + st.session_state.fech) / 2)) - 1) * 100
            angle = max(min(diff_g * 140, 90), -90)
            
            if diff_g > 0.10: al_t, al_c = "PRECIFICAÇÃO DE ALTA", "#00ff88"
            elif diff_g < -0.10: al_t, al_c = "PRECIFICAÇÃO DE BAIXA", "#ff3333"
            else: al_t, al_c = "PRECIFICAÇÃO NEUTRA", "#ffff00"

            with placeholder.container():
                st.markdown(f"""
                    <div class='t-header'>
                        <div class='t-title'>TERMINAL <span class='t-bold'>DÓLAR</span></div>
                        <div class='t-line'></div>
                        <div style='font-family:Chakra Petch; font-size:22px; font-weight:700;'>
                            {s_p:.4f} <span style='color:{"#00ff88" if s_v >= 0 else "#ff3333"}'>{s_v:+.2f}%</span>
                        </div>
                        <div class="gauge-container">
                            <div class="gauge-bg"></div><div class="gauge-cover"></div>
                            <div class="gauge-needle" style="transform: translateX(-50%) rotate({angle}deg);"></div>
                        </div>
                        <div class="btn-alerta" style="border: 1px solid {al_c}; color: {al_c};">{al_t}</div>
                    </div>

                    <div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00ff88">{equi:.4f}</div></div>
                    <div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{st.session_state.ajuste:.4f}</div></div>
                    
                    <div class="d-row"><div class="d-label">PREÇO JUSTO</div><div style="display:flex; gap:15px;">
                        <div style="text-align:center"><small>MIN</small><br><span style="color:#ff3333">{(round((s_p+st.session_state.v22)*2000)/2000):.4f}</span></div>
                        <div style="text-align:center"><small>JUSTO</small><br><span style="color:#0066cc">{(round((s_p+st.session_state.v31)*2000)/2000):.4f}</span></div>
                        <div style="text-align:center"><small>MAX</small><br><span style="color:#00ff88">{(round((s_p+st.session_state.v42)*2000)/2000):.4f}</span></div>
                    </div></div>

                    <div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div style="display:flex; gap:15px;">
                        <div style="text-align:center"><small>MIN</small><br><span style="color:#ff3333">{(round((st.session_state.ref+st.session_state.v22)*2000)/2000):.4f}</span></div>
                        <div style="text-align:center"><small>JUSTO</small><br><span style="color:#0066cc">{(round((st.session_state.ref+st.session_state.v31)*2000)/2000):.4f}</span></div>
                        <div style="text-align:center"><small>MAX</small><br><span style="color:#00ff88">{(round((st.session_state.ref+st.session_state.v42)*2000)/2000):.4f}</span></div>
                    </div></div>

                    <div class="d-row"><div class="d-label">REGIÕES DE CORREÇÃO</div>
                        <div style="display:flex; gap:40px;">
                            <div class="corr-box"><span class="val-11">{(st.session_state.ref-0.0110):.4f}</span><span class="val-22">{(st.session_state.ref-st.session_state.v22):.4f}</span></div>
                            <div class="corr-box"><span class="val-11">{(st.session_state.ref+0.0110):.4f}</span><span class="val-22">{(st.session_state.ref+st.session_state.v22):.4f}</span></div>
                        </div>
                    </div>

                    <div class="txt-editavel">{st.session_state.txt_topo}</div>
                """, unsafe_allow_html=True)
                
                def c(v): return "#00ff88" if v >= 0 else "#ff3333"
                tk = (
                    f"<span class='tk-item'>DXY: {dx_p:.2f} <span style='color:{c(dx_v)}'>({dx_v:+.2f}%)</span></span>"
                    f"<span class='tk-item'>EWZ: {ew_p:.2f} <span style='color:{c(ew_v)}'>({ew_v:+.2f}%)</span></span>"
                    f"<span class='tk-item'>EURUSD: {eu_p:.4f} <span style='color:{c(eu_v)}'>({eu_v:+.2f}%)</span></span>"
                    f"<span class='tk-item'>SPREAD: <span style='color:#ffff00'>{spread:+.4f}</span></span>"
                    f"<span class='tk-item'>PTAX: {st.session_state.ptax:.4f}</span>"
                )
                st.markdown(f"<div class='f-bar'><div class='tk-move'>{tk}{tk}</div></div>", unsafe_allow_html=True)

    time.sleep(2)
