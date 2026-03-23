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
    .title-box { display: flex; align-items: center; gap: 8px; line-height: 1; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .sep-text { font-size: 46px; color: #ffffff; font-weight: 950; margin: 0 5px; }
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    .clock-container { display: flex; gap: 10px; color: #888; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; margin-bottom: 2px; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 10px 8px; border-bottom: 1px solid #444; font-size: 15px; font-weight: bold; align-items: center; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ewz-mini-container { display: flex; justify-content: space-around; padding: 4px 0; border-top: 1px solid #444; margin-top: 4px; }
    .ewz-mini-val { font-size: 11px; font-weight: bold; font-family: monospace; }
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
    st.markdown("### ⚙️ PAINEL ADM")
    with st.form("ajuste_vars"):
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        st.form_submit_button("SALVAR")

# --- LÓGICA DE DADOS ---
tz_sp = pytz.timezone('America/Sao_Paulo')
spot = fetch("USDBRL=X")
ewz = fetch("EWZ")

# --- CÁLCULOS AJUSTADOS CONFORME SOLICITADO ---
# Spreed baseado na máxima e mínima reais do spot no painel
spreed_val = (spot['mx'] - spot['mn']) / 8
max_fut_val = a_dol + spot['mx'] + spreed_val
min_fut_val = a_dol - spot['mn'] + spreed_val
media_dol_val = (spot['mx'] + spot['mn']) / 2

# UI HEADER
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

c_main, c_side = st.columns([3, 1])

with c_main:
    html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
    outros = {"DOLFUT": "BRL=F", "DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
    ticker_items = []
    
    for lbl, sym in outros.items():
        d = spot if lbl == "DOLSPOT" else (ewz if lbl == "EWZ" else fetch(sym))
        var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
        color = "#00ff00" if var >= 0 else "#ff4d4d"
        html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['op']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
        ticker_items.append(f"{lbl}: {var:+.2f}%")
    st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

with c_side:
    # BLOCO SUPERIOR: APENAS AXIS, MAX E MIN (SEM 25/75%)
    st.markdown(f"""
    <div class="calc-panel">
        <div class="calc-row" style="color:#ff4d4d; border-bottom: 1.5px solid #ffffff;"><span>MAX FUT</span> <span>{max_fut_val:.2f}</span></div>
        <div style="text-align:center; padding: 35px 10px; color: #00f2ff; font-size: 26px; font-weight: bold; margin: 10px 0;">AXIS: {a_dol:.2f}</div>
        <div class="calc-row" style="color:#00ff88; border-top: 1.5px solid #ffffff; border-bottom: none;"><span>MIN FUT</span> <span>{min_fut_val:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # BLOCO INFERIOR: MÉDIA DOL AJUSTADA + RESTANTE
    st.markdown(f"""
    <div class="calc-panel">
        <div class="calc-row"><span style="color:#ffffff;">DOLFUT</span> <span style="color:#00f2ff;">{fetch("BRL=F")['at']:.2f}</span></div>
        <div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff;">{media_dol_val:.2f}</span></div>
        <div class="calc-row" style="border-bottom: none;"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#ffffff;">5246.07</span></div>
        <div class="ewz-mini-container">
            <span class="ewz-mini-val" style="color:#00ff88;">{ewz['mx']:.2f}</span>
            <span class="ewz-mini-val" style="color:#00f2ff;">{(ewz['mx']+ewz['mn'])/2:.2f}</span>
            <span class="ewz-mini-val" style="color:#ff4d4d;">{ewz['mn']:.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
