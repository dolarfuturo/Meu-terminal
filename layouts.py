import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO ---
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
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 12px 8px; border-bottom: 1px solid #444; font-size: 15px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {
            "at": d['Close'].iloc[-1], 
            "cl": t.info.get('previousClose', d['Open'].iloc[0]),
            "op": d['Open'].iloc[0], 
            "mx": d['High'].max(), 
            "mn": d['Low'].min()
        }
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- PAINEL ADM ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_dol = st.number_input("AXIS DOLFUT:", value=5308.00, format="%.2f")

# --- EXECUÇÃO ---
tz_sp = pytz.timezone('America/Sao_Paulo')
spot = fetch("USDBRL=X")
ewz = fetch("EWZ")

# CÁLCULOS DAS SETAS
spreed = (spot['mx'] - spot['mn']) / 8
max_fut = a_dol + spot['mx'] + spreed
min_fut = a_dol - spot['mn'] + spreed
media_dol_val = (spot['mx'] + spot['mn']) / 2

# UI HEADER
st.markdown(f"""<div class="header-bair"><div><span class="bair-text">BAIR</span> <span style="color:#fff">-</span> <span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div>""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    assets = {"DOLFUT": "BRL=F", "DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
    table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
    for lbl, sym in assets.items():
        d = spot if lbl == "DOLSPOT" else (ewz if lbl == "EWZ" else fetch(sym))
        var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
        color = "#00ff00" if var >= 0 else "#ff4d4d"
        table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['op']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td style='color:{color};'>{var:+.2f}%</td></tr>"
    st.markdown(table + "</tbody></table></div>", unsafe_allow_html=True)

with col2:
    # SETA VERMELHA: APENAS MÁXIMA, AXIS E MÍNIMA
    st.markdown(f"""
    <div class="calc-panel">
        <div class="calc-row" style="color:#ff4d4d; border-bottom: 2px solid #fff;"><span>MÁXIMA</span> <span>{max_fut:.2f}</span></div>
        <div style="text-align:center; padding: 45px 0; color: #00f2ff; font-size: 26px; font-weight: bold;">AXIS: {a_dol:.2f}</div>
        <div class="calc-row" style="color:#00ff88; border-top: 2px solid #fff; border-bottom:none;"><span>MÍNIMA</span> <span>{min_fut:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # SETA VERDE: DOLFUT, MÉDIA DOL E P.JUSTO
    st.markdown(f"""
    <div class="calc-panel">
        <div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{fetch("BRL=F")['at']:.2f}</span></div>
        <div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff;">{media_dol_val:.2f}</span></div>
        <div class="calc-row" style="border-bottom:none;"><span>P. JUSTO</span> <span>5246.07</span></div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(5)
st.rerun()
