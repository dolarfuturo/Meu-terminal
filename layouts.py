import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- CSS: LIMPEZA SEM MATAR O ACESSO ---
st.markdown("""
<style>
    /* ESCONDE BONEQUINHOS E DEPLOY, MANTÉM O MENU LATERAL */
    [data-testid="stStatusWidget"] {display: none;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 8px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 6px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    .bar-wrapper-dual { background: #0a141a; padding: 12px 10px 6px 10px; border: 2.5px solid #ffffff; border-radius: 8px; text-align: center; position: relative; }
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.1, "cl": 0.1, "mx": 0.1, "mn": 0.1, "op": 0.1}
        m = 1000 if s == "USDBRL=X" else 1
        cl = t.info.get('previousClose', d['Open'].iloc[0]) * m
        return {"at": d['Close'].iloc[-1] * m, "cl": cl, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
    except: return {"at": 0.1, "cl": 0.1, "mx": 0.1, "mn": 0.1, "op": 0.1}

@st.cache_data(ttl=600)
def get_sentinela():
    try:
        df = yf.Ticker("EWZ").history(period="5d")
        return (df['High'].iloc[-2] + df['Low'].iloc[-2]) / 2
    except: return 37.85

# --- ESTADOS INICIAIS ---
if 'a_ewz' not in st.session_state: st.session_state.a_ewz = get_sentinela()
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00

# --- SIDEBAR ADM ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    st.session_state.a_ewz = st.number_input("AXIS EWZ:", value=float(st.session_state.a_ewz), format="%.2f")
    st.session_state.a_dol = st.number_input("AXIS DOLFUT:", value=float(st.session_state.a_dol), format="%.2f")
    st.button("SALVAR")
    st.markdown(f'<div style="border: 1px solid #d4a017; padding: 10px; border-radius: 5px; background: #0a141a; text-align: center; margin-top: 10px;"><span style="color: #d4a017; font-size: 10px; font-weight: bold; display: block;">SENTINELA EWZ</span><span style="color: #ffffff; font-size: 18px; font-weight: bold;">{get_sentinela():.2f}</span></div>', unsafe_allow_html=True)

# --- LOOP PRINCIPAL ---
main_space = st.empty()

while True:
    tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
    spot = fetch("USDBRL=X")
    ewz = fetch("EWZ")
    
    # Cálculo K97
    sprd = (spot['mx'] - spot['mn']) / 8
    v_v = (((spot['at']/spot['cl'])-1)*0.6 - ((ewz['at']/ewz['cl'])-1)*0.4) * 100
    dfut_calc = st.session_state.a_dol * (1 + (v_v/100))
    p_v = min(100, abs(spot['at'] - st.session_state.a_dol)) # Simp para teste rápido
    
    with main_space.container():
        # Header
        st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="terminal-text">-TERMINAL</span></div><div style="display:flex; gap:10px;"><div class="clock-box"><span class="clock-label">SP</span><br><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">NY</span><br><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>ATIVO</th><th>PRICE</th><th>MAX</th><th>MIN</th><th>VAR</th></tr></thead><tbody>"""
            html += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(dfut_calc/1000):.4f}</td><td>{(spot['mx']/1000):.4f}</td><td>{(spot['mn']/1000):.4f}</td><td style='color:#00ff00;'>{v_v:+.2f}%</td></tr>"
            st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span>AXIS</span><span>{st.session_state.a_dol:.2f}</span></div><div class="calc-row"><span>JUSTO</span><span>{dfut_calc:.2f}</span></div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="bar-wrapper-dual"><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width:{p_v}%"></div></div><div class="bar-side"></div></div></div>""", unsafe_allow_html=True)

    time.sleep(2)
