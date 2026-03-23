import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO SHARK ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 16px; font-weight: 800; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: 900; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 10px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #444; font-size: 15px; font-weight: 900; }
    .axis-title { text-align:center; padding: 15px; color: #00f2ff; font-size: 22px; font-weight: 950; border-top:2px solid #fff; border-bottom:2px solid #fff; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {"at": d['Close'].iloc[-1], "cl": t.info.get('previousClose', d['Open'].iloc[0]), 
                "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- LÓGICA DE CÁLCULO SHARK ---
def calcular_niveis_shark(a_dol, spot_data):
    try:
        # 1. SPREDD DO SPOT (MAX - MIN / 8)
        mx_s, mn_s = spot_data['mx'], spot_data['mn']
        spreedd = (mx_s - mn_s) / 8
        
        # 2. PROJEÇÃO FUTURO (MAX/MIN FUT)
        # Max Fut = AXIS + Max Spot + SPREDD
        # Min Fut = AXIS - Min Spot + SPREDD
        max_f = a_dol + mx_s + spreedd
        min_f = a_dol - mn_s + spreedd
        
        # 3. MÉDIA DOL (MAX + MIN DO SPOT / 2)
        media_dol = (mx_s + mn_s) / 2
        
        return {"max_f": max_f, "min_f": min_f, "media_dol": media_dol, "spreedd": spreedd}
    except: return None

# --- SIDEBAR ADM ---
with st.sidebar:
    st.markdown("### ⚙️ AJUSTE DE EIXO")
    a_dol = st.number_input("AXIS DOLFUT:", value=5308.00, step=1.0, format="%.2f")

# --- UI HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""<div class="header-bair"><div><span class="bair-text">BAIR</span> <span style='color:#fff; font-size:40px;'>-</span> <span class="terminal-text">TERMINAL DOLLAR</span></div><div style='display:flex; gap:10px;'><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

# Captura dados
spot_live = fetch("USDBRL=X")
shark = calcular_niveis_shark(a_dol, spot_live)

if shark:
    c_main, c_side = st.columns([3, 1])
    
    with c_main:
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        outros = {"DOLFUT": "BRL=X", "DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "XAU/USD": "GC=F"}
        for lbl, sym in outros.items():
            d = spot_live if lbl == "DOLSPOT" else fetch(sym)
            var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
            color = "#00ff00" if var >= 0 else "#ff4d4d"
            f = ".4f" if "DOL" in lbl else ".2f"
            html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['op']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{color};'>{var:+.2f}%</td></tr>"
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        # PAINEL SUPERIOR (SETA VERMELHA - LIMPO)
        st.markdown(f"""
        <div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d; font-size: 18px;"><span>MÁXIMA</span> <span>{shark['max_f']:.2f}</span></div>
            <div class="axis-title">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#00ff88; font-size: 18px; border-bottom: none;"><span>MÍNIMA</span> <span>{shark['min_f']:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # PAINEL INFERIOR (SETA VERDE - MÉDIA AJUSTADA)
        st.markdown(f"""
        <div class="calc-panel">
            <div class="calc-row" style="color:#ffffff;"><span>DOLFUT</span> <span style="color:#00f2ff;">{spot_live['at']*1000:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>MÉDIA DOL</span> <span style="color:#00f2ff;">{shark['media_dol']:.2f}</span></div>
            <div class="calc-row" style="border-bottom: none; color:#d4a017;"><span>SPREDD SPOT</span> <span style="color:#fff;">{shark['spreedd']:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

time.sleep(5)
st.rerun()
