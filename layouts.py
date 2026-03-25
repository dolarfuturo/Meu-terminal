import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. SETUP NEXUS CHASSIS
st.set_page_config(layout="wide", page_title="BAIR NEXUS", initial_sidebar_state="collapsed")

if 'a_ewz' not in st.session_state: st.session_state.a_ewz = 37.85
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00

# 2. CSS: O CHASSI COMPLETO (ESTÁTICO)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background-color: #050a0e !important; }
    .nexus-card { border: 2.5px solid #ffffff; border-radius: 8px; padding: 10px; background: #0d1b22; margin-bottom: 8px; }
    .terminal-table { width: 100%; border-collapse: collapse; font-family: monospace; color: #e0e0e0; }
    .terminal-table th { background: #0a141a; color: #d4a017; border: 1.5px solid #ffffff; padding: 10px; font-size: 13px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 16px; font-weight: bold; }
    .asset-name { text-align: left !important; padding-left: 15px !important; color: #fff; }
    .price-cyan { color: #00f2ff !important; }
    
    .header-bair { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #fff; padding-bottom: 5px; margin-bottom: 10px; }
    .bair-text { font-size: 45px; color: #00f2ff; font-weight: 950; font-family: monospace; }
    .term-text { font-size: 45px; color: #d4a017; font-weight: 950; font-family: monospace; }
    .clock-box { border: 2px solid #fff; padding: 5px 15px; border-radius: 5px; background: #0a141a; color: #fff; font-size: 25px; font-weight: bold; }
    
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 6px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 50s linear infinite; font-family: monospace; font-size: 14px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .stExpander { border: 2px solid #d4a017 !important; background: #0a141a !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# 3. GATILHO SET (SETA)
with st.expander("▶ AJUSTAR EIXOS (SET ADM)"):
    with st.form("nexus_set"):
        c1, c2 = st.columns(2)
        n_ewz = c1.number_input("AXIS EWZ", value=st.session_state.a_ewz, format="%.2f")
        n_dol = c2.number_input("AXIS DOLFUT", value=st.session_state.a_dol, format="%.2f")
        if st.form_submit_button("SALVAR"):
            st.session_state.a_ewz, st.session_state.a_dol = n_ewz, n_dol
            st.rerun()

# 4. MOTOR DE DADOS
def fetch_nexus(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at":0.0,"cl":0.01,"mx":0.0,"mn":0.0,"op":0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1]*m, "cl": t.info.get('previousClose', d['Open'].iloc[0])*m, "op": d['Open'].iloc[0]*m, "mx": d['High'].max()*m, "mn": d['Low'].min()*m}
    except: return {"at":0.0,"cl":0.01,"mx":0.0,"mn":0.0,"op":0.0}

# 5. LOOP NEXUS (SEM PISCAR)
nexus_stage = st.empty()

while True:
    spot = fetch_nexus("USDBRL=X")
    ewz = fetch_nexus("EWZ")
    dxy = fetch_nexus("DX-Y.NYB")
    
    # Cálculos Originais do seu Código
    v_spreed = (spot['mx'] - spot['mn']) / 8
    v_spot = (spot['at'] / spot['cl'] - 1) if spot['cl'] > 0 else 0
    v_ewz = (ewz['at'] / ewz['cl'] - 1) if ewz['cl'] > 0 else 0
    v_calc = (v_spot * 0.6) - (v_ewz * 0.4)
    p_justo = st.session_state.a_dol * (1 + (v_calc / 2))
    dolfut_com_spread = spot['at'] + v_spreed
    
    # Força
    diff = spot['at'] - st.session_state.a_dol
    p_r = min(100, (diff / 12) * 100) if diff > 0 else 0
    p_v = min(100, (abs(diff) / 12) * 100) if diff < 0 else 0

    with nexus_stage.container():
        st.markdown(f"""<div class="header-bair"><div><span class="bair-text">BAIR</span><span class="term-text">-TERMINAL</span></div><div class="clock-box">{datetime.now().strftime('%H:%M:%S')}</div></div>""", unsafe_allow_html=True)

        col_main, col_side = st.columns([3, 1])
        
        with col_main:
            # Tabela
            html = """<div class="nexus-card"><table class="terminal-table"><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>MAX</th><th>MIN</th><th>VAR%</th></tr>"""
            data = [
                ("DOLFUT (CALC)", p_justo, st.session_state.a_dol, spot['mx'], spot['mn'], v_calc*100),
                ("DOLSPOT", spot['at'], spot['cl'], spot['mx'], spot['mn'], v_spot*100),
                ("EWZ", ewz['at'], ewz['cl'], ewz['mx'], ewz['mn'], v_ewz*100),
                ("DXY", dxy['at'], dxy['cl'], dxy['mx'], dxy['mn'], (dxy['at']/dxy['cl']-1)*100 if dxy['cl']>0 else 0)
            ]
            ticker_list = []
            for n, at, cl, mx, mn, vr in data:
                div = 1000 if "DOL" in n else 1
                f = ".4f" if "DOL" in n else ".2f"
                cor = "#00ff88" if vr >= 0 else "#ff4d4d"
                html += f"<tr><td class='asset-name'>{n}</td><td class='price-cyan'>{(at/div):{f}}</td><td>{(cl/div):{f}}</td><td>{(mx/div):{f}}</td><td>{(mn/div):{f}}</td><td style='color:{cor}'>{vr:+.2f}%</td></tr>"
                ticker_list.append(f"{n}: <span style='color:{cor}'>{vr:+.2f}%</span>")
            st.markdown(html + "</table></div>", unsafe_allow_html=True)

        with col_side:
            # Painéis de Cálculo
            st.markdown(f"""
            <div class="calc-panel">
                <div class="calc-row" style="color:#ff4d4d;"><span>MAX FUT</span> <span>{(spot['mx']+v_spreed):.2f}</span></div>
                <div class="calc-row" style="color:#ffa500;"><span>75% UP</span> <span>{(spot['mx']):.2f}</span></div>
                <div style="text-align:center; padding:8px; color:#00f2ff; font-size:18px; font-weight:bold; border-top:1px solid #444; border-bottom:1px solid #444;">AXIS: {st.session_state.a_dol:.2f}</div>
                <div class="calc-row" style="color:#ffa500;"><span>75% DN</span> <span>{(spot['mn']+v_spreed*2):.2f}</span></div>
                <div class="calc-row" style="color:#00ff88; border:none;"><span>MIN FUT</span> <span>{(spot['mn']+v_spreed):.2f}</span></div>
            </div>
            <div class="calc-panel">
                <div style="display:flex; justify-content:space-between; padding:5px 8px;">
                    <span style="color:#fff;">DOLFUT</span> <span style="color:#00f2ff; font-size:18px; font-weight:bold;">{dolfut_com_spread:.2f}</span>
                </div>
                <div class="calc-row"><span>JUSTO</span> <span>{p_justo:.2f}</span></div>
                <div class="calc-row" style="border:none;"><span>SPREAD</span> <span style="color:#00f2ff;">{v_spreed:.2f}</span></div>
            </div>
            <div class="nexus-card" style="text-align:center; padding:10px;">
                <div class="force-container-dual"><div class="center-line"></div>
                    <div style="width:50%"><div class="fill-green" style="width:{p_v}%"></div></div>
                    <div style="width:50%"><div class="fill-red" style="width:{p_r}%"></div></div>
                </div>
                <div style="color:{('#00ff88' if p_v>p_r else '#ff4d4d')}; font-weight:bold; font-size:14px; margin-top:5px;">
                    {('▲ COMPRA' if p_v>85 else '▼ VENDA' if p_r>85 else 'AGUARDANDO')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Ticker Marquee Inferior
        t_html = "  •  ".join(ticker_list)
        st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{t_html} • {t_html}</div></div>', unsafe_allow_html=True)

    time.sleep(2)
