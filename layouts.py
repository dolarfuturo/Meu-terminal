import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO COMPACTA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; text-transform: uppercase; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {
            "at": d['Close'].iloc[-1], "cl": t.info.get('previousClose', d['Open'].iloc[0]), 
            "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()
        }
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- PAINEL ADM ---
with st.sidebar:
    st.markdown("### ⚙️ AJUSTES")
    with st.form("vars"):
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        v_spreed = st.number_input("SPREED:", value=10.00, format="%.2f")
        st.form_submit_button("ATUALIZAR")

# --- PROCESSAMENTO ---
ewz_live = fetch("EWZ")
spot_live = fetch("USDBRL=X")

# CÁLCULOS DA IMAGEM
max_spot = spot_live['mx']
min_spot = spot_live['mn']

max_fut = a_dol + max_spot + v_spreed
min_fut = a_dol - min_spot + v_spreed
p50_up = (max_fut + a_dol) / 2
p50_down = (min_fut + a_dol) / 2

# Variação DOLFUT (60/40)
v_spot = ((spot_live['at'] / spot_live['cl']) - 1) if spot_live['cl'] > 0 else 0
v_ewz = ((ewz_live['at'] / fetch("EWZ")['cl']) - 1) if fetch("EWZ")['cl'] > 0 else 0
v_final = (v_spot * 0.6) - (v_ewz * 0.4)
dolar_vivo = a_dol * (1 + v_final)
dolar_fraja = a_dol * (1 + (v_final / 2))

# --- UI ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span style="color:white; font-size:46px;">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-box"><span class="clock-label">BRASÍLIA</span><br><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div>""", unsafe_allow_html=True)

c1, c2 = st.columns([3, 1])
with c1:
    html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
    ativos = {"DOLFUT": {"at": dolar_vivo, "cl": a_dol, "mx": max_fut, "mn": min_fut}, "DOLSPOT": spot_live, "EWZ": ewz_live}
    ticker_items = []
    for lbl, d in ativos.items():
        var = ((d['at']/d['cl'])-1)*100 if d['cl'] > 0 else 0
        color = "#00ff00" if var >= 0 else "#ff4d4d"
        fmt = ".4f" if "DOL" in lbl else ".2f"
        html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:{fmt}}</td><td>{d['cl']:{fmt}}</td><td>{d['mx']:{fmt}}</td><td>{d['mn']:{fmt}}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
        ticker_items.append(f"{lbl}: {var:+.2f}%")
    st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="calc-panel">
        <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{max_fut:.2f}</span></div>
        <div class="calc-row" style="color:#ffa500;"><span>50% UP</span> <span>{p50_up:.2f}</span></div>
        <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {a_dol:.2f}</div>
        <div class="calc-row" style="color:#ffa500;"><span>50% DOWN</span> <span>{p50_down:.2f}</span></div>
        <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{min_fut:.2f}</span></div>
    </div>
    <div class="calc-panel">
        <div class="calc-row"><span style="color:#ffffff;">DOLFUT VIVO</span> <span style="color:#00f2ff;">{dolar_vivo:.2f}</span></div>
        <div class="calc-row" style="border-bottom: none;"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#ffffff;">{dolar_fraja:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
