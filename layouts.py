import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO DE TELA
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- 2. ESTADO DO SISTEMA (O SET + CONTROLE DE VISIBILIDADE) ---
if 'a_ewz' not in st.session_state: st.session_state.a_ewz = 37.85
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00
if 'show_adm' not in st.session_state: st.session_state.show_adm = False

# --- 3. CSS COMPLETO (CHASSI NEXUS) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background-color: #050a0e !important; }
    
    .adm-box { background-color: #0a141a; border: 1px solid #d4a017; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
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
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; }
    
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 6px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    
    .bar-wrapper-dual { background: #0a141a; padding: 12px 10px 6px 10px; border: 2.5px solid #ffffff; border-radius: 8px; text-align: center; position: relative; }
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .fill-green { background: #00ff88; float: right; height: 100%; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
</style>
""", unsafe_allow_html=True)

# --- 4. O BOTÃO DE ENGRENAGEM (SET) ---
col_set1, col_set2 = st.columns([1, 8])
if col_set1.button("⚙️ AJUSTAR"):
    st.session_state.show_adm = not st.session_state.show_adm

if st.session_state.show_adm:
    with st.container():
        st.markdown('<div class="adm-box">', unsafe_allow_html=True)
        with st.form("set_form"):
            c_adm1, c_adm2 = st.columns(2)
            new_ewz = c_adm1.number_input("AXIS EWZ:", value=st.session_state.a_ewz, format="%.2f")
            new_dol = c_adm2.number_input("AXIS DOLFUT:", value=st.session_state.a_dol, format="%.2f")
            if st.form_submit_button("💾 SALVAR E OCULTAR"):
                st.session_state.a_ewz = new_ewz
                st.session_state.a_dol = new_dol
                st.session_state.show_adm = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. MOTOR DE DADOS (TODOS OS ATIVOS DE VOLTA) ---
def fetch_full(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m")
        if d.empty: return {"at":0.0,"cl":0.1,"mx":0.1,"mn":0.1}
        mult = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1]*mult, "cl": t.info.get('previousClose', d['Open'].iloc[0])*mult, "mx": d['High'].max()*mult, "mn": d['Low'].min()*mult}
    except: return {"at":0.0,"cl":0.1,"mx":0.1,"mn":0.1}

# --- 6. LOOP DE ATUALIZAÇÃO ---
terminal_placeholder = st.empty()

while True:
    spot = fetch_full("USDBRL=X")
    ewz = fetch_full("EWZ")
    dxy = fetch_full("DX-Y.NYB")
    gold = fetch_full("GC=F")
    brent = fetch_full("BZ=F")
    jpy = fetch_full("JPYUSD=X")
    
    # Cálculos Frajola
    v_spot = (spot['at'] / spot['cl'] - 1) if spot['cl'] > 0 else 0
    v_ewz = (ewz['at'] / ewz['cl'] - 1) if ewz['cl'] > 0 else 0
    v_final = (v_spot * 0.6) - (v_ewz * 0.4)
    p_justo = st.session_state.a_dol * (1 + (v_final / 2))
    
    diff = spot['at'] - st.session_state.a_dol
    dist = abs(st.session_state.a_dol - ((spot['mx']+spot['mn'])/2))
    pv = min(100, (abs(diff)/(dist*2))*100) if diff < 0 and dist > 0 else 0
    pr = min(100, (abs(diff)/(dist*2))*100) if diff > 0 and dist > 0 else 0

    with terminal_placeholder.container():
        st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="terminal-text">-TERMINAL</span></div><div class="clock-box"><span class="clock-time">{datetime.now().strftime('%H:%M:%S')}</span></div></div>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([3, 1])
        with c1:
            # TABELA COMPLETA COM SEUS ATIVOS
            html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
            # DOLFUT
            html += f"<tr><td class='asset-name'>DOLFUT (CALC)</td><td class='price-col'>{(p_justo/1000):.4f}</td><td>{(st.session_state.a_dol/1000):.4f}</td><td>{(spot['mx']/1000):.4f}</td><td>{(spot['mn']/1000):.4f}</td><td style='color:#00ff88;'>{v_final*100:+.2f}%</td></tr>"
            # LISTA DE ATIVOS
            ativos = [("DOLSPOT", spot), ("EWZ", ewz), ("DXY", dxy), ("OURO", gold), ("BRENT", brent), ("JPY/USD", jpy)]
            for name, d in ativos:
                var = (d['at']/d['cl']-1)*100
                color = "#00ff88" if var >= 0 else "#ff4d4d"
                p_disp = d['at']/1000 if name=="DOLSPOT" else d['at']
                html += f"<tr><td class='asset-name'>{name}</td><td class='price-col'>{p_disp:.4f}</td><td>{(d['cl']/1000 if name=='DOLSPOT' else d['cl']):.4f}</td><td>{(d['mx']/1000 if name=='DOLSPOT' else d['mx']):.4f}</td><td>{(d['mn']/1000 if name=='DOLSPOT' else d['mn']):.4f}</td><td style='color:{color};'>{var:+.2f}%</td></tr>"
            st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

        with c2:
            st.markdown(f"""<div class="calc-panel"><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold;">AXIS: {st.session_state.a_dol:.2f}</div><div class="calc-row"><span>P. JUSTO</span> <span>{p_justo:.2f}</span></div><div class="calc-row" style="border:none;"><span>VAR AXIS</span> <span>{((spot['at']/st.session_state.a_dol)-1)*100:+.2f}%</span></div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="bar-wrapper-dual"><div class="force-container-dual"><div class="center-line"></div><div style="width:50%"><div class="fill-green" style="width:{pv}%"></div></div><div style="width:50%"><div class="fill-red" style="width:{pr}%"></div></div></div><div class="sinal-indicator blink" style="color:{('#00ff88' if pv>pr else '#ff4d4d')}">{('▲ COMPRA' if pv>80 else '▼ VENDA' if pr>80 else '---')}</div></div>""", unsafe_allow_html=True)

    time.sleep(2)
