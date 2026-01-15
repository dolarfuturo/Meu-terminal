import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import time

# 1. SETUP
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. VARIÁVEIS DE MEMÓRIA (ADICIONADO PTAX E FECH)
if 'ptax' not in st.session_state: st.session_state.ptax = 5.4000
if 'fech' not in st.session_state: st.session_state.fech = 5.4000
if 'ref' not in st.session_state: st.session_state.ref = 5.4000
if 'auth' not in st.session_state: st.session_state.auth = False

# 3. LOGIN
if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'] { display: none; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("CHAVE", type="password")
        if st.button("ENTRAR"):
            if senha == "admin123": st.session_state.auth = True; st.rerun()
    st.stop()

# 4. SIDEBAR - SET DE VARIÁVEIS (PTAX E FECHAMENTO AQUI)
with st.sidebar:
    st.header("SET DE MEMÓRIA")
    st.session_state.ptax = st.number_input("PTAX", value=st.session_state.ptax, format="%.4f")
    st.session_state.fech = st.number_input("FECHAMENTO", value=st.session_state.fech, format="%.4f")
    st.session_state.ref = st.number_input("REF. INST", value=st.session_state.ref, format="%.4f")
    if st.button("SALVAR"): st.rerun()

# 5. CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .t-header { text-align: center; padding: 5px 0; }
    .t-title { font-size: 18px; letter-spacing: 3px; font-weight: 900; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 10px; font-weight: 900; color: #888; }
    .d-value { font-size: 20px; font-family: 'Chakra Petch'; font-weight: 700; }
    .sub-v { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #080808; border-top: 1px solid #222; display: flex; align-items: center; z-index: 1000; overflow: hidden; }
    .tk-move { white-space: nowrap; animation: move 35s linear infinite; }
    .tk-item { display: inline-block; padding-right: 45px; font-family: 'Chakra Petch'; font-size: 11px; }
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

main_ui = st.empty()

while True:
    s_p, s_v = get_live("BRL=X")
    dx_p, dx_v = get_live("DX-Y.NYB")
    ew_p, ew_v = get_live("EWZ")
    
    if s_p > 0:
        # LÓGICA DO TERMÔMETRO: DISTÂNCIA DO SPOT PARA A PTAX/FECH
        # Se Spot > Ptax/Fech = Alta (Verde) | Se Spot < Ptax/Fech = Baixa (Vermelho)
        alvo_memoria = (st.session_state.ptax + st.session_state.fech) / 2
        diff_memoria = ((s_p / alvo_memoria) - 1) * 100
        
        with main_ui.container():
            st.markdown("<div class='t-header'><div class='t-title'>TERMINAL DÓLAR</div></div>", unsafe_allow_html=True)
            
            # VELOCÍMETRO DE DISTORÇÃO (SPOT vs MEMÓRIA)
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = diff_memoria,
                number = {'suffix': "%", 'font': {'size': 18, 'color': "#fff"}, 'valueformat': ".2f"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "SPOT vs PTAX/FECH", 'font': {'size': 10, 'color': "#888"}},
                gauge = {
                    'axis': {'range': [-1, 1], 'tickwidth': 1, 'tickcolor': "#444"},
                    'bar': {'color': "#fff"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'steps': [
                        {'range': [-1, -0.1], 'color': "#ff3333"}, # Perdeu Ptax/Fech
                        {'range': [-0.1, 0.1], 'color': "#ffff00"}, # No ajuste
                        {'range': [0.1, 1], 'color': "#00ff88"}], # Acima da Memória
                }
            ))
            fig.update_layout(height=160, margin=dict(l=40, r=40, t=30, b=0), paper_bgcolor="black", font={'color': "white"})
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # TABELA DE DADOS
            st.markdown(f'<div class="d-row"><div class="d-label">PTAX SET</div><div class="d-value" style="color:#fff">{st.session_state.ptax:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">FECHAMENTO</div><div class="d-value" style="color:#fff">{st.session_state.fech:.4f}</div></div>', unsafe_allow_html=True)
            
            # REF INSTITUCIONAL
            st.markdown(f"""<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div style="display:flex; gap:15px;">
                <div style="text-align:center"><small>MIN</small><br><span class="sub-v" style="color:#ff3333">{(round((st.session_state.ref+0.0220)*2000)/2000):.4f}</span></div>
                <div style="text-align:center"><small>JUSTO</small><br><span class="sub-v" style="color:#0066cc">{(round((st.session_state.ref+0.0310)*2000)/2000):.4f}</span></div>
                <div style="text-align:center"><small>MAX</small><br><span class="sub-v" style="color:#00ff88">{(round((st.session_state.ref+0.0420)*2000)/2000):.4f}</span></div>
            </div></div>""", unsafe_allow_html=True)

            # TICKER RODAPÉ
            def c(v): return "#00ff88" if v >= 0 else "#ff3333"
            spr = dx_v - ew_v
            t_html = (f"<b>SPOT:</b> {s_p:.4f} <span style='color:{c(s_v)}'>({s_v:+.2f}%)</span> | "
                      f"<b>DXY:</b> {dx_p:.2f} <span style='color:{c(dx_v)}'>({dx_v:+.2f}%)</span> | "
                      f"<b>SPREAD:</b> <span style='color:{c(spr)}'>{spr:+.2f}%</span>")
            st.markdown(f"<div class='f-bar'><div class='tk-move'><span class='tk-item'>{t_html}</span><span class='tk-item'>{t_html}</span></div></div>", unsafe_allow_html=True)

    time.sleep(2)
