import streamlit as st
import yfinance as yf
import time

# 1. SETUP DE PÁGINA
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. VARIÁVEIS DE CONTROLE (SET)
if 'ajuste' not in st.session_state: st.session_state.ajuste = 5.4000
if 'ref' not in st.session_state: st.session_state.ref = 5.4000
if 'auth' not in st.session_state: st.session_state.auth = False

# 3. LOGIN
if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'] { display: none; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("CHAVE", type="password")
        if st.button("ACESSAR"):
            if senha in ["admin123", "trader123"]:
                st.session_state.auth = True
                st.rerun()
    st.stop()

# 4. PAINEL ADM (SIDEBAR)
with st.sidebar:
    st.title("⚙️ SET VARIÁVEIS")
    st.session_state.ajuste = st.number_input("PARIDADE", value=st.session_state.ajuste, format="%.4f")
    st.session_state.ref = st.number_input("REF. INSTITUCIONAL", value=st.session_state.ref, format="%.4f")
    if st.button("SALVAR"): st.rerun()

# 5. CSS DO TERMINAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    
    /* CABEÇALHO */
    .t-header { text-align: center; padding: 5px 0; }
    .t-title { font-size: 26px; letter-spacing: 5px; font-weight: 900; }
    
    /* BLOCOS DE PREÇO */
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; font-weight: 900; color: #aaa; text-transform: uppercase; }
    .d-value { font-size: 22px; font-family: 'Chakra Petch'; font-weight: 700; }
    .sub-v { font-size: 16px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    /* TICKER RODAPÉ */
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #080808; border-top: 1px solid #222; display: flex; align-items: center; z-index: 1000; }
    .tk-move { white-space: nowrap; animation: move 30s linear infinite; }
    .tk-item { display: inline-block; padding-right: 50px; font-family: 'Chakra Petch'; font-size: 12px; }
    @keyframes move { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        d = t.history(period="1d", interval="1m")
        if d.empty: return 0.0, 0.0
        last = d['Close'].iloc[-1]
        var = ((last - t.fast_info.previous_close) / t.fast_info.previous_close * 100)
        return float(last), float(var)
    except: return 0.0, 0.0

main_container = st.empty()

while True:
    # Captura de dados
    s_p, s_v = get_data("BRL=X")
    dx_p, dx_v = get_data("DX-Y.NYB")
    ew_p, ew_v = get_data("EWZ")
    eu_p, eu_v = get_data("EURUSD=X")
    
    if s_p > 0:
        spr = dx_v - ew_v
        justo = round((s_p + 0.0310) * 2000) / 2000
        ref_j = round((st.session_state.ref + 0.0310) * 2000) / 2000
        
        # Lógica de cor e mensagem
        diff = s_p - justo
        if diff < -0.0015: msg, clr = "PRECIFICAÇÃO DE ALTA", "#00ff88"
        elif diff > 0.0015: msg, clr = "PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: msg, clr = "PRECIFICAÇÃO NEUTRA", "#ffff00"

        with main_container.container():
            # 1. TOPO: TÍTULO E TERMÔMETRO (ESTILO VELOCÍMETRO)
            st.markdown(f"<div class='t-header'><div class='t-title'>TERMINAL <span style='color:{clr}'>DÓLAR</span></div></div>", unsafe_allow_html=True)
            
            # Termômetro Centralizado usando coluna do Streamlit (Velocímetro de Pressão)
            c1, c2, c3 = st.columns([1,1,1])
            with c2:
                st.metric(label=msg, value=f"{s_p:.4f}", delta=f"{s_v:+.2f}%")
                # Barra de pressão visual (Velocímetro)
                st.progress(min(max(int(50 + (spr * 10)), 0), 100))

            # 2. BLOCOS DE DADOS
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{(st.session_state.ajuste*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO JUSTO (SPOT)
            st.markdown(f"""
                <div class="d-row">
                    <div class="d-label">PREÇO JUSTO (SPOT)</div>
                    <div style="display:flex; gap:15px;">
                        <div style="text-align:center"><small>MIN</small><br><span class="sub-v" style="color:#ff3333">{(round((s_p+0.0220)*2000)/2000):.4f}</span></div>
                        <div style="text-align:center"><small>JUSTO</small><br><span class="sub-v" style="color:#0066cc">{justo:.4f}</span></div>
                        <div style="text-align:center"><small>MAX</small><br><span class="sub-v" style="color:#00ff88">{(round((s_p+0.0420)*2000)/2000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # REF INSTITUCIONAL
            st.markdown(f"""
                <div class="d-row">
                    <div class="d-label">REF. INSTITUCIONAL</div>
                    <div style="display:flex; gap:15px;">
                        <div style="text-align:center"><small>MIN</small><br><span class="sub-v" style="color:#ff3333">{(round((st.session_state.ref+0.0220)*2000)/2000):.4f}</span></div>
                        <div style="text-align:center"><small>JUSTO</small><br><span class="sub-v" style="color:#0066cc">{ref_j:.4f}</span></div>
                        <div style="text-align:center"><small>MAX</small><br><span class="sub-v" style="color:#00ff88">{(round((st.session_state.ref+0.0420)*2000)/2000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # REGIÃO DE CORREÇÃO
            st.markdown(f"""
                <div class="d-row" style="border:none;">
                    <div class="d-label">REGIÃO DE CORREÇÃO</div>
                    <div style="display:flex; gap:20px; color:#ffff00; font-weight:700; font-family:'Chakra Petch';">
                        <div>{(st.session_state.ref-0.0110):.4f} / {(st.session_state.ref-0.0220):.4f}</div>
                        <div>{(st.session_state.ref+0.0110):.4f} / {(st.session_state.ref+0.0220):.4f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 3. RODAPÉ (TICKER COM CORES INDIVIDUAIS)
            def color(v): return "#00ff88" if v >= 0 else "#ff3333"
            t_html = (
                f"<b>SPOT:</b> {s_p:.4f} <span style='color:{color(s_v)}'>({s_v:+.2f}%)</span> | "
                f"<b>DXY:</b> {dx_p:.2f} <span style='color:{color(dx_v)}'>({dx_v:+.2f}%)</span> | "
                f"<b>EWZ:</b> {ew_p:.2f} <span style='color:{color(ew_v)}'>({ew_v:+.2f}%)</span> | "
                f"<b>EUR:</b> {eu_p:.4f} <span style='color:{color(eu_v)}'>({eu_v:+.2f}%)</span> | "
                f"<b>SPREAD:</b> <span style='color:{color(spr)}'>{spr:+.2f}%</span>"
            )
            st.markdown(f"<div class='f-bar'><div class='tk-move'><span class='tk-item'>{t_html}</span><span class='tk-item'>{t_html}</span></div></div>", unsafe_allow_html=True)

    time.sleep(2)
