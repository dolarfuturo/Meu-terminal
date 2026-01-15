import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
if 'ajuste' not in st.session_state: st.session_state.ajuste = 5.4000
if 'ref' not in st.session_state: st.session_state.ref = 5.4000

# 3. ACESSO
if 'auth' not in st.session_state: st.session_state.auth = False
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

# 4. CSS OTIMIZADO - FOCO NO ENCAIXE E TERMÔMETRO NO TOPO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    /* TERMÔMETRO NO TOPO */
    .v-frame { width: 100%; height: 6px; background: #111; position: fixed; top: 0; left: 0; z-index: 99999; }
    .v-bar { height: 100%; transition: width 0.8s ease; box-shadow: 0 0 15px currentColor; }
    
    /* CABEÇALHO CENTRALIZADO */
    .t-header { text-align: center; padding: 15px 0 5px 0; border-bottom: 1px solid #111; margin-top: 6px; }
    .t-title { font-size: 22px; letter-spacing: 4px; margin-bottom: 4px; }
    .t-light { font-weight: 300; }
    .t-bold { font-weight: 900; }
    
    .spot-mini { font-family: 'Chakra Petch'; font-size: 16px; color: #888; font-weight: 400; }

    .s-container { text-align: center; padding: 4px 0; border-bottom: 1px solid #111; background: #080808; }
    .s-text { font-size: 9px; font-weight: 700; letter-spacing: 2px; }
    
    /* LINHAS DE DADOS */
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 10px; font-weight: 900; width: 40%; }
    .sub-grid { display: flex; gap: 10px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 60px; display: flex; flex-direction: column; }
    .sub-l { font-size: 7px; color: #666; }
    .sub-v { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; }
    .v-peq { font-size: 14px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    .v-extra { font-size: 10px; font-family: 'Chakra Petch'; color: #ffff00; opacity: 0.5; }
    .d-value { font-size: 19px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }

    /* RODAPÉ COLORIDO */
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 9999; }
    .tk-move { display: inline-block; animation: slide 35s linear infinite; white-space: nowrap; }
    .tk-item { padding-right: 35px; display: inline-block; font-family: 'Chakra Petch'; font-size: 11px; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d", interval="1m")
        if df.empty: return {"last": 0.0, "var": 0.0}
        last = df['Close'].iloc[-1]
        var = ((last - t.fast_info.previous_close) / t.fast_info.previous_close * 100)
        return {"last": last, "var": var}
    except: return {"last": 0.0, "var": 0.0}

# PAINEL ADM CORRIGIDO (FORA DO LOOP)
if st.session_state.user_type == "ADM":
    with st.sidebar:
        st.header("CONFIGS")
        st.session_state.ajuste = st.number_input("PARIDADE", value=st.session_state.ajuste, format="%.4f")
        st.session_state.ref = st.number_input("REF INST", value=st.session_state.ref, format="%.4f")
        if st.button("ATUALIZAR"): st.rerun()

ui_area = st.empty()

while True:
    d_m, e_m, s_m, eu_m = get_data("DX-Y.NYB"), get_data("EWZ"), get_data("BRL=X"), get_data("EURUSD=X")
    
    if d_m["last"] > 0:
        spot, spot_var = s_m["last"], s_m["var"]
        spr = d_m["var"] - e_m["var"]
        justo = round((spot + 0.0310) * 2000) / 2000
        equi = round((st.session_state.ref + 0.0220) * 2000) / 2000
        
        dist = abs(spot - equi) * 1000
        v_width = min(dist * 4, 100)
        
        diff_j = spot - justo
        if diff_j < -0.0015: msg, clr = "● PRECIFICAÇÃO DE ALTA", "#00ff88"
        elif diff_j > 0.0015: msg, clr = "● PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: msg, clr = "● PRECIFICAÇÃO NEUTRA", "#ffff00"
            
        with ui_area.container():
            # 1. TERMÔMETRO (TOPO)
            st.markdown(f'<div class="v-frame"><div class="v-bar" style="width: {v_width}%; background: {clr}; color: {clr};"></div></div>', unsafe_allow_html=True)

            # 2. CABEÇALHO CENTRAL
            v_clr = "#00ff88" if spot_var >= 0 else "#ff3333"
            st.markdown(f"""
                <div class="t-header">
                    <div class="t-title"><span class="t-light">TERMINAL</span> <span class="t-bold">DÓLAR</span></div>
                    <div class="spot-mini">{spot:.4f} <span style="color:{v_clr}">{spot_var:+.2f}%</span></div>
                </div>
                <div class="s-container"><div class="s-text" style="color:{clr}">{msg}</div></div>
            """, unsafe_allow_html=True)
            
            # 3. LINHAS DE PREÇO
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{(st.session_state.ajuste*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equi:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v" style="color:#cc3333">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v" style="color:#0066cc">{justo:.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v" style="color:#00cc66">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v" style="color:#cc3333">{(round((st.session_state.ref+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v" style="color:#0066cc">{(round((st.session_state.ref+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v" style="color:#00cc66">{(round((st.session_state.ref+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row" style="border-bottom:none;"><div class="d-label">REGIÃO DE CORREÇÃO</div><div class="sub-grid"><div class="sub-item"><span class="v-peq">{(equi-0.0110):.4f}</span><span class="v-extra">{(equi-0.0220):.4f}</span></div><div class="sub-item"><span class="v-peq">{(equi+0.0110):.4f}</span><span class="v-extra">{(equi+0.0220):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # 4. RODAPÉ (TICKER)
            def fc(val): return "#00ff88" if val >= 0 else "#ff3333"
            btk = f"""
            <span class='tk-item'><b>SPOT</b> {spot:.4f} <span style="color:{fc(spot_var)}">({spot_var:+.2f}%)</span></span>
            <span class='tk-item'><b>DXY</b> {d_m['last']:.2f} <span style="color:{fc(d_m['var'])}">({d_m['var']:+.2f}%)</span></span>
            <span class='tk-item'><b>EWZ</b> {e_m['last']:.2f} <span style="color:{fc(e_m['var'])}">({e_m['var']:+.2f}%)</span></span>
            <span class='tk-item'><b>EURUSD</b> {eu_m['last']:.4f} <span style="color:{fc(eu_m['var'])}">({eu_m['var']:+.2f}%)</span></span>
            <span class='tk-item'><b>SPREAD</b> <span style="color:{fc(spr)}">{spr:+.2f}%</span></span>
            """
            st.markdown(f'<div class="f-bar"><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
