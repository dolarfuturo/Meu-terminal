import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO DE TELA (TABLET)
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL", initial_sidebar_state="collapsed")

# --- 2. ESTADO DO SISTEMA (O SET) ---
if 'a_ewz' not in st.session_state: st.session_state.a_ewz = 37.85
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00

# --- 3. CSS: VERTICAL SET & CHASSI ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background-color: #050a0e !important; }
    
    /* ESTILO DA GAVETA VERTICAL NO SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #0a141a !important;
        border-right: 2px solid #d4a017 !important;
        width: 250px !important;
    }
    
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
    
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 6px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    
    .bar-wrapper-dual { background: #0a141a; padding: 12px 10px 6px 10px; border: 2.5px solid #ffffff; border-radius: 8px; text-align: center; position: relative; }
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
</style>
""", unsafe_allow_html=True)

# --- 4. PAINEL ADM VERTICAL (A SETA QUE ABRE) ---
with st.sidebar:
    st.markdown("<h2 style='color:#d4a017; font-family:monospace;'>⚙️ SET ADM</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:12px;'>AJUSTE OS EIXOS ABAIXO:</p>", unsafe_allow_html=True)
    
    with st.form("set_vertical"):
        new_ewz = st.number_input("AXIS EWZ", value=st.session_state.a_ewz, format="%.2f")
        new_dol = st.number_input("AXIS DOLFUT", value=st.session_state.a_dol, format="%.2f")
        if st.form_submit_button("APLICAR AJUSTES"):
            st.session_state.a_ewz = new_ewz
            st.session_state.a_dol = new_dol
            st.rerun()
    
    st.markdown("---")
    st.info("Clique na seta (▶) no topo para esconder este painel.")

# --- 5. FUNÇÃO DE DADOS ---
def fetch_full(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m")
        mult = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1]*mult, "cl": t.info.get('previousClose', d['Open'].iloc[0])*mult, "mx": d['High'].max()*mult, "mn": d['Low'].min()*mult}
    except: return {"at":0.0,"cl":0.1,"mx":0.1,"mn":0.1}

# --- 6. MOTOR NEXUS ---
terminal_placeholder = st.empty()

while True:
    spot = fetch_full("USDBRL=X")
    ewz = fetch_full("EWZ")
    dxy = fetch_full("DX-Y.NYB")
    gold = fetch_full("GC=F")
    
    # Cálculos
    v_spot = (spot['at'] / spot['cl'] - 1) if spot['cl'] > 0 else 0
    v_ewz = (ewz['at'] / ewz['cl'] - 1) if ewz['cl'] > 0 else 0
    v_final = (v_spot * 0.6) - (v_ewz * 0.4)
    p_justo = st.session_state.a_dol * (1 + (v_final / 2))
    
    diff = spot['at'] - st.session_state.a_dol
    dist = abs(st.session_state.a_dol - ((spot['mx']+spot['mn'])/2))
    pv = min(100, (abs(diff)/(dist*2))*100) if diff < 0 and dist > 0 else 0
    pr = min(100, (abs(diff)/(dist*2))*100) if diff > 0 and dist > 0 else 0

    with terminal_placeholder.container():
        # Header com Relógio
        st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="terminal-text">-TERMINAL</span></div><div class="clock-box"><span style="color:#fff; font-size:20px; font-weight:bold; font-family:monospace;">{datetime.now().strftime('%H:%M:%S')}</span></div></div>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([3, 1])
        with c1:
            # Tabela principal
            html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
            # Ativos
            lista = [("DOLFUT (CALC)", p_justo, st.session_state.a_dol, spot['mx'], spot['mn'], v_final*100),
                     ("DOLSPOT", spot['at'], spot['cl'], spot['mx'], spot['mn'], v_spot*100),
                     ("EWZ", ewz['at'], ewz['cl'], ewz['mx'], ewz['mn'], v_ewz*100),
                     ("DXY", dxy['at'], dxy['cl'], dxy['mx'], dxy['mn'], (dxy['at']/dxy['cl']-1)*100)]
            
            for n, at, cl, mx, mn, vr in lista:
                p_disp = at/1000 if "DOL" in n else at
                c_disp = cl/1000 if "DOL" in n else cl
                mx_disp = mx/1000 if "DOL" in n else mx
                mn_disp = mn/1000 if "DOL" in n else mn
                color = "#00ff88" if vr >= 0 else "#ff4d4d"
                html += f"<tr><td class='asset-name'>{n}</td><td class='price-col'>{p_disp:.4f if 'DOL' in n else p_disp:.2f}</td><td>{c_disp:.4f if 'DOL' in n else c_disp:.2f}</td><td>{mx_disp:.4f if 'DOL' in n else mx_disp:.2f}</td><td>{mn_disp:.4f if 'DOL' in n else mn_disp:.2f}</td><td style='color:{color}; font-weight:bold;'>{vr:+.2f}%</td></tr>"
            st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

        with c2:
            # Painel Lateral
            st.markdown(f"""<div class="calc-panel"><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold;">AXIS: {st.session_state.a_dol:.2f}</div><div class="calc-row"><span>P. JUSTO</span> <span>{p_justo:.2f}</span></div><div class="calc-row" style="border:none;"><span>VAR AXIS</span> <span>{((spot['at']/st.session_state.a_dol)-1)*100:+.2f}%</span></div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="bar-wrapper-dual"><div class="force-container-dual"><div class="center-line"></div><div style="width:50%"><div class="fill-green" style="width:{pv}%"></div></div><div style="width:50%"><div class="fill-red" style="width:{pr}%"></div></div></div><div class="sinal-indicator blink" style="color:{('#00ff88' if pv>pr else '#ff4d4d')}">{('▲ COMPRA' if pv>80 else '▼ VENDA' if pr>80 else '---')}</div></div>""", unsafe_allow_html=True)

    time.sleep(2)
