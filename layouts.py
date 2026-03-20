import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO COMPACTA (PRESERVADA) ---
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
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch_data(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        cl = t.info.get('previousClose') or d['Open'].iloc[0]
        at = d['Close'].iloc[-1]
        return {"at": at, "cl": cl, "mx": d['High'].max(), "mn": d['Low'].min(), "op": d['Open'].iloc[0]}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- PAINEL ADM ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    with st.form("ajuste_vars"):
        a_ewz = st.number_input("AXIS EWZ:", value=37.85, format="%.2f")
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        st.form_submit_button("SALVAR")

# --- LÓGICA DE VARIAÇÃO PURA ---
spot = fetch_data("USDBRL=X")
ewz = fetch_data("EWZ")

# 1. Variação do Spot (60%)
v_spot = ((spot['at'] / spot['cl']) - 1) * 100 if spot['cl'] > 0 else 0

# 2. Variação do EWZ (Invertida) (40%)
# Aqui pegamos a variação real do EWZ e invertemos o sinal
v_ewz_real = ((ewz['at'] / ewz['cl']) - 1) * 100 if ewz['cl'] > 0 else 0
v_ewz_inv = v_ewz_real * -1

# 3. Variação Final do Dol Fut (Fórmula Ponderada)
v_final_dol = (v_spot * 0.6) + (v_ewz_inv * 0.4)

# 4. Preço Calculado (Sintético) sobre o Axis
dolfut_vivo = a_dol * (1 + (v_final_dol / 100))

# --- UI HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

c_main, c_side = st.columns([3, 1])

with c_main:
    html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
    
    # LINHA DOLFUT (CALCULADA PELA VARIAÇÃO PONDERADA)
    cor_v = "#00ff00" if v_final_dol >= 0 else "#ff4d4d"
    html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(dolfut_vivo/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>-</td><td>-</td><td style='color:{cor_v}; font-weight:bold;'>{v_final_dol:+.2f}%</td></tr>"
    
    ticker = [f"DOLFUT: {v_final_dol:+.2f}%"]
    outros = {"DOLSPOT": spot, "EWZ": ewz, "DXY": fetch_data("DX-Y.NYB"), "EUR/USD": fetch_data("EURUSD=X")}
    
    for lbl, d in outros.items():
        v = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
        f = ".4f" if "USD" in lbl or "DOL" in lbl else ".2f"
        html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['op']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{("#00ff00" if v >= 0 else "#ff4d4d")}; font-weight:bold;'>{v:+.2f}%</td></tr>"
        ticker.append(f"{lbl}: {v:+.2f}%")
        
    st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

with c_side:
    st.markdown(f"""<div class="calc-panel">
        <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-bottom:1.5px solid #444; margin-bottom: 5px;">AXIS: {a_dol:.2f}</div>
        <div class="calc-row" style="padding: 10px 8px;"><span style="color:#ffffff;">DOLFUT VIVO</span> <span style="color:#00f2ff; font-size: 16px; font-weight: 950;">{dolfut_vivo:.2f}</span></div>
        <div class="calc-row"><span style="color:#ffff00;">VAR SPOT (60%)</span> <span>{v_spot:+.2f}%</span></div>
        <div class="calc-row" style="border-bottom: none;"><span style="color:#d4a017;">VAR EWZ (40%)</span> <span>{v_ewz_inv:+.2f}%</span></div>
    </div>""", unsafe_allow_html=True)

st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker)}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
