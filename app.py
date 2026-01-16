import streamlit as st
import yfinance as yf
import time

# 1. SETUP INICIAL
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. INICIALIZAÇÃO DE VARIÁVEIS DE ESTADO
for key, val in {
    'ptax': 5.4000, 'ajuste': 5.4000, 'ref': 5.4000,
    'v22': 0.0220, 'v31': 0.0310, 'v42': 0.0420,
    'txt_topo': "FOCO NO PLANO - RESPEITE O STOP", 'show_settings': False
}.items():
    if key not in st.session_state: st.session_state[key] = val

# 3. CSS ESTILIZAÇÃO
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
    .v-pari-justo { font-size: 13px; color: #0066cc; font-family: 'Chakra Petch'; margin-left: 10px; font-weight: 400; }
    .corr-box { display: flex; flex-direction: column; align-items: center; font-family: 'Chakra Petch'; font-size: 14px; }
    .val-11 { font-weight: 700; color: #ffff00; }
    .val-22 { font-weight: 400; color: #ffff00; opacity: 0.6; }
    .txt-editavel { text-align: center; font-family: 'Chakra Petch'; font-size: 11px; color: #666; margin-top: 15px; margin-bottom: 45px; text-transform: uppercase; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 999; overflow: hidden; }
    .tk-move { white-space: nowrap; animation: move 35s linear infinite; display: flex; align-items: center; }
    .tk-item { padding-right: 40px; font-family: 'Chakra Petch'; font-size: 11px; font-weight: 700; }
    @keyframes move { from { transform: translateX(100%); } to { transform: translateX(-100%); } }
</style>
""", unsafe_allow_html=True)

# 4. MENU CONFIGURAÇÕES (SET)
if st.button("⚙️ SET" if not st.session_state.show_settings else "✖ FECHAR"):
    st.session_state.show_settings = not st.session_state.show_settings
    st.rerun()

if st.session_state.show_settings:
    st.markdown("### AJUSTES TÉCNICOS")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.ajuste = st.number_input("VALOR DO AJUSTE (BASE)", value=st.session_state.ajuste, format="%.4f")
        st.session_state.ptax = st.number_input("VALOR DA PTAX", value=st.session_state.ptax, format="%.4f")
        st.session_state.ref = st.number_input("REFERÊNCIA BASE", value=st.session_state.ref, format="%.4f")
    with c2:
        st.session_state.v22 = st.number_input("VARIAÇÃO 22", value=st.session_state.v22, format="%.4f")
        st.session_state.v31 = st.number_input("VARIAÇÃO 31", value=st.session_state.v31, format="%.4f")
        st.session_state.v42 = st.number_input("VARIAÇÃO 42", value=st.session_state.v42, format="%.4f")
    st.session_state.txt_topo = st.text_input("FRASE TOPO", value=st.session_state.txt_topo)
    if st.button("SALVAR"):
        st.session_state.show_settings = False
        st.rerun()

# 5. MOTOR DE DADOS E INTERFACE
placeholder = st.empty()
while True:
    if not st.session_state.show_settings:
        try:
            # Busca de dados Yahoo Finance
            t_usd = yf.Ticker("BRL=X").fast_info
            t_dxy = yf.Ticker("DX-Y.NYB").fast_info
            t_ewz = yf.Ticker("EWZ").fast_info
            t_eur = yf.Ticker("EURUSD=X").fast_info
            
            spot = t_usd.last_price
            v_dxy = ((t_dxy.last_price / t_dxy.previous_close) - 1) * 100
            v_ewz = ((t_ewz.last_price / t_ewz.previous_close) - 1) * 100
            v_eur = ((t_eur.last_price / t_eur.previous_close) - 1) * 100
            v_spot = ((t_usd.last_price / t_usd.previous_close) - 1) * 100
            
            # Cálculos de Paridade e Justos
            spread = v_dxy - v_ewz
            paridade = st.session_state.ajuste * (1 + (spread / 100))
            pari_justo = round((paridade + st.session_state.v22) * 2000) / 2000
            
            equi = round((st.session_state.ref + st.session_state.v22) * 2000) / 2000
            j_min = round((spot + st.session_state.v22) * 2000) / 2000
            j_med = round((spot + st.session_state.v31) * 2000) / 2000
            j_max = round((spot + st.session_state.v42) * 2000) / 2000
            
            # Alerta de Precificação
            diff = spot - j_med
            if diff < -0.0015: al_t, al_c, ang = "PRECIFICAÇÃO DE ALTA", "#00ff88", 45
            elif diff > 0.0015: al_t, al_c, ang = "PRECIFICAÇÃO DE BAIXA", "#ff3333", -45
            else: al_t, al_c, ang = "PRECIFICAÇÃO NEUTRA", "#ffff00", 0

            with placeholder.container():
                # Bloco Superior
                st.markdown(f"""
                <div class='t-header'>
                    <div class='t-title'>TERMINAL <span class='t-bold'>DÓLAR</span></div>
                    <div class='t-line'></div>
                    <div style='font-family:Chakra Petch; font-size:22px; font-weight:700;'>
                        {spot:.4f} <span style='color:{al_c}'>{v_spot:+.2f}%</span>
                    </div>
                    <div class="gauge-container">
                        <div class="gauge-bg"></div><div class="gauge-cover"></div>
                        <div class="gauge-needle" style="transform: translateX(-50%) rotate({ang}deg);"></div>
                    </div>
                    <div class="btn-alerta" style="border: 1px solid {al_c}; color: {al_c};">{al_t}</div>
                </div>
                """, unsafe_allow_html=True)

                # Valores Principais (Paridade e Equilíbrio)
                st.markdown(f"""
                <div class="d-row">
                    <div class="d-label">PARIDADE GLOBAL</div>
                    <div>
                        <span class="d-value" style="color:#cc9900">{paridade:.4f}</span>
                        <span class="v-pari-justo">{pari_justo:.4f}</span>
                    </div>
                </div>
                <div class="d-row">
                    <div class="d-label">EQUILÍBRIO</div>
                    <div class="d-value" style="color:#00cccc">{equi:.4f}</div>
                </div>
                """, unsafe_allow_html=True)

                # Preço Justo e Regiões
                st.markdown(f"""
                <div class="d-row">
                    <div class="d-label">PREÇO JUSTO</div>
                    <div style="display:flex; gap:15px;">
                        <div style="text-align:center"><small>MIN</small><br><span style="color:#cc3333" class="d-value">{j_min:.4f}</span></div>
                        <div style="text-align:center"><small>JUSTO</small><br><span style="color:#0066cc" class="d-value">{j_med:.4f}</span></div>
                        <div style="text-align:center"><small>MAX</small><br><span style="color:#00cc66" class="d-value">{j_max:.4f}</span></div>
                    </div>
                </div>
                <div class="d-row" style="border-bottom:none">
                    <div class="d-label">REGIÕES DE CORREÇÃO</div>
                    <div style="display:flex; gap:40px;">
                        <div class="corr-box"><span class="val-11">{(equi - 0.0110):.4f}</span><span class="val-22">{(equi - 0.0220):.4f}</span></div>
                        <div class="corr-box"><span class="val-11">{(equi + 0.0110):.4f}</span><span class="val-22">{(equi + 0.0220):.4f}</span></div>
                    </div>
                </div>
                <div class="txt-editavel">{st.session_state.txt_topo}</div>
                """, unsafe_allow_html=True)
                
                # Ticker de Rodapé com SPOT e EURUSD
                def c(v): return "#00ff88" if v >= 0 else "#ff3333"
                tk_c = f"""
                <span class='tk-item'><b>SPOT</b> {spot:.4f} <span style='color:{c(v_spot)}'>({v_spot:+.2f}%)</span></span>
                <span class='tk-item'><b>DXY</b> {t_dxy.last_price:.2f} <span style='color:{c(v_dxy)}'>({v_dxy:+.2f}%)</span></span>
                <span class='tk-item'><b>EWZ</b> {t_ewz.last_price:.2f} <span style='color:{c(v_ewz)}'>({v_ewz:+.2f}%)</span></span>
                <span class='tk-item'><b>EURUSD</b> {t_eur.last_price:.4f} <span style='color:{c(v_eur)}'>({v_eur:+.2f}%)</span></span>
                <span class='tk-item'><b>SPREAD</b> <span style='color:#ffff00'>{spread:+.2f}%</span></span>
                <span class='tk-item'><b>PTAX</b> {st.session_state.ptax:.4f}</span>
                """
                st.markdown(f"<div class='f-bar'><div class='tk-move'>{tk_c} {tk_c}</div></div>", unsafe_allow_html=True)
        except Exception:
            pass
    time.sleep(2)
