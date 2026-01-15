import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO INICIAL (LAYOUT COMPACTO)
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO DAS VARIÁVEIS (SET)
if 'ajuste' not in st.session_state: st.session_state.ajuste = 5.4000
if 'ref' not in st.session_state: st.session_state.ref = 5.4000
if 'auth' not in st.session_state: st.session_state.auth = False

# 3. LOGIN SIMPLES
if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'] { display: none; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("CHAVE", type="password")
        if st.button("ENTRAR"):
            if senha in ["admin123", "trader123"]:
                st.session_state.auth = True
                st.rerun()
    st.stop()

# 4. PAINEL DE CONTROLE (SIDEBAR)
with st.sidebar:
    st.title("CONFIGS")
    st.session_state.ajuste = st.number_input("PARIDADE", value=st.session_state.ajuste, format="%.4f")
    st.session_state.ref = st.number_input("REF INST", value=st.session_state.ref, format="%.4f")
    if st.button("SALVAR"): st.rerun()

# 5. CSS REVISADO (SEM ERROS DE RENDERIZAÇÃO)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; overflow: hidden; }
    
    .t-header { text-align: center; padding: 10px 0; }
    .t-title { font-size: 24px; letter-spacing: 4px; }
    .t-light { font-weight: 300; color: white; }
    .t-bold { font-weight: 900; color: white; }
    
    /* TERMÔMETRO - BARRA FIXA E VISÍVEL */
    .v-frame { width: 50%; height: 6px; background: #1a1a1a; margin: 10px auto; border-radius: 10px; border: 1px solid #333; position: relative; }
    .v-bar { height: 100%; border-radius: 10px; transition: width 0.8s ease; box-shadow: 0 0 15px currentColor; }
    
    .spot-mini { font-family: 'Chakra Petch'; font-size: 16px; margin-top: 5px; color: #888; }
    .s-msg { font-size: 10px; font-weight: 700; letter-spacing: 2px; margin-top: 5px; }

    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 10px; font-weight: 900; color: #fff; }
    .d-value { font-size: 20px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .sub-v { font-size: 16px; font-family: 'Chakra Petch'; font-weight: 700; }

    /* TICKER OTIMIZADO */
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 40px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 1000; }
    .tk-move { display: inline-block; animation: slide 45s linear infinite; white-space: nowrap; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 12px; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# Função de busca sem SyntaxError
def get_mkt(ticker):
    try:
        t = yf.Ticker(ticker)
        d = t.history(period="1d", interval="1m")
        if d.empty: return 0.0, 0.0
        last = d['Close'].iloc[-1]
        prev = t.fast_info.previous_close
        v = ((last - prev) / prev * 100)
        return float(last), float(v)
    except:
        return 0.0, 0.0

main_ui = st.empty()

while True:
    # Coleta
    s_p, s_v = get_mkt("BRL=X")
    dx_p, dx_v = get_mkt("DX-Y.NYB")
    ew_p, ew_v = get_mkt("EWZ")
    eu_p, eu_v = get_mkt("EURUSD=X")
    
    if s_p > 0:
        spr = dx_v - ew_v
        justo = round((s_p + 0.0310) * 2000) / 2000
        equi = round((st.session_state.ref + 0.0220) * 2000) / 2000
        
        # Termômetro: distância do Spot para o Equilíbrio
        dist = abs(s_p - equi) * 1000
        w_pct = min(dist * 4, 100)
        
        diff = s_p - justo
        if diff < -0.0015: msg, clr = "● PRECIFICAÇÃO DE ALTA", "#00ff88"
        elif diff > 0.0015: msg, clr = "● PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: msg, clr = "● PRECIFICAÇÃO NEUTRA", "#ffff00"

        with main_ui.container():
            # TOPO CENTRALIZADO
            st.markdown(f"""
                <div class='t-header'>
                    <div class='t-title'><span class='t-light'>TERMINAL</span> <span class='t-bold'>DÓLAR</span></div>
                    <div class='v-frame'><div class='v-bar' style='width: {w_pct}%; background: {clr}; color: {clr};'></div></div>
                    <div class='spot-mini'>{s_p:.4f} <span style='color:{"#00ff88" if s_v >= 0 else "#ff3333"}'>{s_v:+.2f}%</span></div>
                    <div class='s-msg' style='color:{clr}'>{msg}</div>
                </div>
            """, unsafe_allow_html=True)

            # CONTEÚDO
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{(st.session_state.ajuste*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equi:.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO JUSTO
            st.markdown(f"""
                <div class="d-row">
                    <div class="d-label">PREÇO JUSTO</div>
                    <div style="display:flex; gap:15px;">
                        <div style="text-align:center"><small style="color:#666">MIN</small><br><span class="sub-v" style="color:#ff3333">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div>
                        <div style="text-align:center"><small style="color:#666">JUSTO</small><br><span class="sub-v" style="color:#0066cc">{justo:.4f}</span></div>
                        <div style="text-align:center"><small style="color:#666">MAX</small><br><span class="sub-v" style="color:#00ff88">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # REGIAO CORREÇAO
            st.markdown(f"""
                <div class="d-row" style="border:none;">
                    <div class="d-label">REGIÃO DE CORREÇÃO</div>
                    <div style="display:flex; gap:20px;">
                        <div style="color:#ffff00; font-weight:700;">{(equi-0.0110):.4f} / {(equi-0.0220):.4f}</div>
                        <div style="color:#ffff00; font-weight:700;">{(equi+0.0110):.4f} / {(equi+0.0220):.4f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # TICKER COLORIDO (SEM ERRO DE VALUE)
            def c(v): return "#00ff88" if v >= 0 else "#ff3333"
            
            t_html = (
                f"<b>SPOT:</b> {s_p:.4f} <span style='color:{c(s_v)}'>({s_v:+.2f}%)</span> &nbsp;&nbsp;&nbsp; "
                f"<b>DXY:</b> {dx_p:.2f} <span style='color:{c(dx_v)}'>({dx_v:+.2f}%)</span> &nbsp;&nbsp;&nbsp; "
                f"<b>EWZ:</b> {ew_p:.2f} <span style='color:{c(ew_v)}'>({ew_v:+.2f}%)</span> &nbsp;&nbsp;&nbsp; "
                f"<b>EUR:</b> {eu_p:.4f} <span style='color:{c(eu_v)}'>({eu_v:+.2f}%)</span> &nbsp;&nbsp;&nbsp; "
                f"<b>SPREAD:</b> <span style='color:{c(spr)}'>{spr:+.2f}%</span>"
            )
            
            st.markdown(f"""
                <div class="f-bar">
                    <div class="tk-move">
                        <span class="tk-item">{t_html}</span>
                        <span class="tk-item">{t_html}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    time.sleep(2)
