import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO BÁSICA
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO DAS VARIÁVEIS (SET)
if 'ajuste' not in st.session_state: st.session_state.ajuste = 5.4000
if 'ref' not in st.session_state: st.session_state.ref = 5.4000

# Sidebar para SET de variáveis (sempre visível para o ADM)
with st.sidebar:
    st.header("⚙️ CONFIGURAÇÕES")
    st.session_state.ajuste = st.number_input("PARIDADE (AJUSTE)", value=st.session_state.ajuste, format="%.4f")
    st.session_state.ref = st.number_input("REF. INSTITUCIONAL", value=st.session_state.ref, format="%.4f")
    if st.button("ATUALIZAR TERMINAL"): st.rerun()

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False

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

# 4. CSS DO LAYOUT, TERMÔMETRO E TICKER
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"] { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    
    /* CABEÇALHO */
    .t-header { text-align: center; padding-top: 10px; }
    .t-title { font-size: 22px; letter-spacing: 3px; }
    .t-light { font-weight: 300; }
    .t-bold { font-weight: 900; }
    
    /* TERMÔMETRO */
    .thermo-container { width: 60%; height: 4px; background: #111; margin: 8px auto; border-radius: 2px; overflow: hidden; border: 1px solid #222; }
    .thermo-bar { height: 100%; transition: width 0.8s ease; box-shadow: 0 0 10px currentColor; }
    
    .spot-mini { font-family: 'Chakra Petch'; font-size: 14px; color: #888; margin-bottom: 5px; }
    .precificacao { font-size: 10px; font-weight: 700; letter-spacing: 2px; border-bottom: 1px solid #111; padding-bottom: 5px; }

    /* GRID DE PREÇOS */
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 10px; font-weight: 900; width: 40%; }
    .sub-v { font-size: 16px; font-family: 'Chakra Petch'; font-weight: 700; }
    .d-value { font-size: 19px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    /* TICKER NO RODAPÉ */
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 999; overflow: hidden; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; white-space: nowrap; }
    .tk-item { padding-right: 40px; display: inline-block; font-family: 'Chakra Petch'; font-size: 11px; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_market_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d", interval="1m")
        if df.empty: return {"last": 0.0, "var": 0.0}
        last = df['Close'].iloc[-1]
        prev = t.fast_info.previous_close
        var = ((last - prev) / prev * 100)
        return {"last": last, "var": var}
    except: return {"last": 0.0, "var": 0.0}

ui_area = st.empty()

while True:
    # Captura de dados
    dxy = get_market_data("DX-Y.NYB")
    ewz = get_market_data("EWZ")
    spot_data = get_market_data("BRL=X")
    eur = get_market_data("EURUSD=X")
    
    if spot_data["last"] > 0:
        spot = spot_data["last"]
        spot_var = spot_data["var"]
        spr = dxy["var"] - ewz["var"]
        
        # Cálculos de tela
        justo = round((spot + 0.0310) * 2000) / 2000
        equi = round((st.session_state.ref + 0.0220) * 2000) / 2000
        
        # Lógica do Termômetro
        dist = abs(spot - equi) * 1000
        t_width = min(dist * 5, 100)
        
        diff_j = spot - justo
        if diff_j < -0.0015: msg, clr = "● PRECIFICAÇÃO DE ALTA", "#00ff88"
        elif diff_j > 0.0015: msg, clr = "● PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: msg, clr = "● PRECIFICAÇÃO NEUTRA", "#ffff00"
            
        with ui_area.container():
            # CABEÇALHO E TERMÔMETRO
            st.markdown(f"""
                <div class="t-header">
                    <div class="t-title"><span class="t-light">TERMINAL</span> <span class="t-bold">DÓLAR</span></div>
                    <div class="thermo-container">
                        <div class="thermo-bar" style="width: {t_width}%; background: {clr}; color: {clr};"></div>
                    </div>
                    <div class="spot-mini">{spot:.4f} <span style="color:{'#00ff88' if spot_var >= 0 else '#ff3333'}">{spot_var:+.2f}%</span></div>
                    <div class="precificacao" style="color:{clr}">{msg}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # GRID DE PREÇOS
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{(st.session_state.ajuste*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equi:.4f}</div></div>', unsafe_allow_html=True)
            
            # JUSTO
            st.markdown(f"""
                <div class="d-row">
                    <div class="d-label">PREÇO JUSTO</div>
                    <div style="display:flex; gap:10px;">
                        <div style="text-align:center"><small style="color:#666; font-size:8px;">MIN</small><br><span class="sub-v" style="color:#ff3333">{(round((spot+0.0220)*2000)/2000):.4f}</span></div>
                        <div style="text-align:center"><small style="color:#666; font-size:8px;">JUSTO</small><br><span class="sub-v" style="color:#0066cc">{justo:.4f}</span></div>
                        <div style="text-align:center"><small style="color:#666; font-size:8px;">MAX</small><br><span class="sub-v" style="color:#00ff88">{(round((spot+0.0420)*2000)/2000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # TICKER COLORIDO NO RODAPÉ
            def fmt_tk(n, d):
                c = "#00ff88" if d["var"] >= 0 else "#ff3333"
                return f"<b>{n}</b> {d['last']:.2f if n != 'EUR' else d['last']:.4f} <span style='color:{c}'>({d['var']:+.2f}%)</span>"

            tick_html = f"{fmt_tk('SPOT', spot_data)} | {fmt_tk('DXY', dxy)} | {fmt_tk('EWZ', ewz)} | {fmt_tk('EUR', eur)} | <b>SPREAD</b> <span style='color:{'#00ff88' if spr >=0 else '#ff3333'}'>{spr:+.2f}%</span>"
            
            st.markdown(f"""
                <div class="f-bar">
                    <div class="tk-move">
                        <span class="tk-item">{tick_html}</span>
                        <span class="tk-item">{tick_html}</span>
                        <span class="tk-item">{tick_html}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    time.sleep(2)
