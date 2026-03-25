import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. SETUP NEXUS (ESTÁTICO)
st.set_page_config(layout="wide", page_title="BAIR - NEXUS TERMINAL", initial_sidebar_state="collapsed")

# Inicialização de Variáveis de Estado
if 'a_ewz' not in st.session_state: st.session_state.a_ewz = 37.85
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00

# 2. CSS NEXUS (NÃO RECARREGA)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background-color: #050a0e !important; }
    .nexus-wrapper { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; font-family: monospace; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 16px; font-weight: bold; }
    .price-col { color: #00f2ff !important; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 10px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: monospace; }
    .term-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: monospace; }
    .clock-box { border: 1.5px solid #ffffff; padding: 5px 15px; border-radius: 4px; background: #0a141a; color: #fff; font-size: 24px; font-weight: bold; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; }
    .stExpander { border: 2px solid #d4a017 !important; background: #0a141a !important; margin-bottom: 10px !important; }
    
    /* BARRA DUAL */
    .force-container-dual { background: #111; height: 18px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 10px 0; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
</style>
""", unsafe_allow_html=True)

# 3. GATILHO SET (EXPANDER NO TOPO)
with st.expander("▶ AJUSTAR EIXOS (SET ADM)"):
    with st.form("nexus_set"):
        c1, c2 = st.columns(2)
        n_ewz = c1.number_input("AXIS EWZ", value=st.session_state.a_ewz, format="%.2f")
        n_dol = c2.number_input("AXIS DOLFUT", value=st.session_state.a_dol, format="%.2f")
        if st.form_submit_button("SALVAR"):
            st.session_state.a_ewz, st.session_state.a_dol = n_ewz, n_dol
            st.rerun()

# 4. MOTOR DE DADOS BLINDADO
def fetch_nexus(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.01, "mx": 0.0, "mn": 0.0, "op": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1]*m, "cl": t.info.get('previousClose', d['Open'].iloc[0])*m, "op": d['Open'].iloc[0]*m, "mx": d['High'].max()*m, "mn": d['Low'].min()*m}
    except: return {"at": 0.0, "cl": 0.01, "mx": 0.0, "mn": 0.0, "op": 0.0}

# 5. LOOP DE RENDERIZAÇÃO (O CHASSI)
nexus_container = st.empty()

while True:
    # Captura de Dados
    spot = fetch_nexus("USDBRL=X")
    ewz = fetch_nexus("EWZ")
    dxy = fetch_nexus("DX-Y.NYB")
    
    # Cálculos Nexus
    v_spot = (spot['at'] / spot['cl'] - 1) if spot['cl'] > 0 else 0
    v_ewz = (ewz['at'] / ewz['cl'] - 1) if ewz['cl'] > 0 else 0
    v_final = (v_spot * 0.6) - (v_ewz * 0.4)
    p_justo = st.session_state.a_dol * (1 + (v_final / 2))
    
    # Barra de Força
    diff = spot['at'] - st.session_state.a_dol
    p_r = min(100, (diff / 15) * 100) if diff > 0 else 0
    p_v = min(100, (abs(diff) / 15) * 100) if diff < 0 else 0

    with nexus_container.container():
        # Header
        st.markdown(f"""
        <div class="header-bair">
            <div><span class="bair-text">BAIR</span><span class="term-text">-TERMINAL</span></div>
            <div class="clock-box">{datetime.now().strftime('%H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)

        c_main, c_side = st.columns([3, 1])

        with c_main:
            # Tabela Estabilizada
            html = """<div class="nexus-wrapper"><table class="terminal-table">
            <tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>MAX</th><th>MIN</th><th>VAR%</th></tr>"""
            
            ativos = [
                ("DOLFUT (CALC)", p_justo, st.session_state.a_dol, spot['mx'], spot['mn'], v_final*100),
                ("DOLSPOT", spot['at'], spot['cl'], spot['mx'], spot['mn'], v_spot*100),
                ("EWZ", ewz['at'], ewz['cl'], ewz['mx'], ewz['mn'], v_ewz*100),
                ("DXY", dxy['at'], dxy['cl'], dxy['mx'], dxy['mn'], (dxy['at']/dxy['cl']-1)*100 if dxy['cl']>0 else 0)
            ]

            for n, at, cl, mx, mn, vr in ativos:
                div = 1000 if "DOL" in n else 1
                fmt = ".4f" if "DOL" in n else ".2f"
                cor = "#00ff88" if vr >= 0 else "#ff4d4d"
                html += f"""<tr>
                    <td style="text-align:left; padding-left:15px;">{n}</td>
                    <td class="price-col">{(at/div):{fmt}}</td>
                    <td>{(cl/div):{fmt}}</td>
                    <td>{(mx/div):{fmt}}</td>
                    <td>{(mn/div):{fmt}}</td>
                    <td style="color:{cor};">{vr:+.2f}%</td>
                </tr>"""
            st.markdown(html + "</table></div>", unsafe_allow_html=True)

        with c_side:
            # Painel Lateral e Barra Dual
            st.markdown(f"""
            <div class="calc-panel">
                <div style="color:#d4a017; font-size:12px; text-align:center;">AXIS ATUAL</div>
                <div style="color:#fff; font-size:28px; text-align:center; font-weight:bold;">{st.session_state.a_dol:.2f}</div>
                <hr style="border:0.5px solid #444;">
                <div style="color:#00f2ff; font-size:12px; text-align:center;">PREÇO JUSTO</div>
                <div style="color:#fff; font-size:24px; text-align:center;">{p_justo:.2f}</div>
                
                <div class="force-container-dual">
                    <div class="center-line"></div>
                    <div style="width:50%;"><div class="fill-green" style="width:{p_v}%;"></div></div>
                    <div style="width:50%;"><div class="fill-red" style="width:{p_r}%;"></div></div>
                </div>
                <div class="blink" style="text-align:center; color:{('#00ff88' if p_v > p_r else '#ff4d4d')}; font-weight:bold;">
                    {('▲ COMPRA' if p_v > 80 else '▼ VENDA' if p_r > 80 else 'AGUARDANDO')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    time.sleep(2) # Atualização sem rerun
