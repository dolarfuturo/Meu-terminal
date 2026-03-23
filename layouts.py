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
    .title-box { display: flex; align-items: center; gap: 8px; line-height: 1; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .sep-text { font-size: 46px; color: #ffffff; font-weight: 950; margin: 0 5px; }
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    .clock-container { display: flex; gap: 10px; color: #888; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; margin-bottom: 2px; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 8px 8px; border-bottom: 1px solid #444; font-size: 14px; font-weight: bold; align-items: center; }
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
        cl = t.info.get('previousClose', d['Close'].iloc[0] if not d.empty else 0)
        if d.empty: return {"at": 0.0, "cl": cl, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {"at": d['Close'].iloc[-1], "cl": cl, "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97_total(a_dol, spot_data):
    try:
        # Converter spot para escala milhar
        s_at = spot_data['at'] * 1000
        s_mx = spot_data['mx'] * 1000
        s_mn = spot_data['mn'] * 1000
        s_cl = spot_data['cl'] * 1000

        # --- REGRAS DO USUÁRIO ---
        spreed = (s_mx - s_mn) / 8
        max_fut = a_dol + s_mx + spreed
        min_fut = a_dol - s_mn + spreed
        dolar_medio = (s_mx + s_mn) / 2
        
        # Dolfut Vivo (Variação Spot aplicada ao AXIS)
        v_final = (s_at / s_cl) - 1 if s_cl > 0 else 0
        dolar_vivo = a_dol * (1 + v_final)

        return {
            "vivo": dolar_vivo,
            "medio": dolar_medio, 
            "max": max_fut, 
            "min": min_fut, 
            "v_v": v_final * 100,
            "p50_up": (a_dol + max_fut) / 2,
            "p50_down": (a_dol + min_fut) / 2
        }
    except: return None

# --- PAINEL ADM ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_dol = st.number_input("AXIS DOLFUT:", value=5308.00, format="%.2f")

# --- UI HEADER ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

spot_live = fetch("USDBRL=X")
res = calcular_k97_total(a_dol, spot_live)

if res:
    c_main, c_side = st.columns([3, 1])
    with c_main:
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{res['vivo']:.2f}</td><td>{a_dol:.2f}</td><td>{res['max']:.2f}</td><td>{res['min']:.2f}</td><td style='color:{("#00ff00" if res['v_v'] >= 0 else "#ff4d4d")}; font-weight:bold;'>{res['v_v']:+.2f}%</td></tr>"
        
        outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ"}
        ticker = []
        for lbl, sym in outros.items():
            d = spot_live if lbl == "DOLSPOT" else fetch(sym)
            var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
            color = "#00ff00" if var >= 0 else "#ff4d4d"
            html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
            ticker.append(f"<span style='color:#fff;'>{lbl}:</span> <span style='color:{color};'>{var:+.2f}%</span>")
        
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        # BLOCO SETA VERMELHA (LIMPO)
        st.markdown(f"""<div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MAX (50%)</span> <span>{res['p50_up']:.2f}</span></div>
            <div style="text-align:center; padding: 15px; color: #00f2ff; font-size: 20px; font-weight: bold; border-top:1.5px solid #ffffff; border-bottom:1.5px solid #ffffff; margin: 10px 0;">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MIN (50%)</span> <span>{res['p50_down']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)
        
        # BLOCO SETA VERDE (MÉDIA DOL CORRIGIDA)
        st.markdown(f"""<div class="calc-panel">
            <div class="calc-row" style="padding: 10px 8px;"><span style="color:#ffffff;">DOLFUT VIVO</span> <span style="color:#00f2ff; font-size: 16px; font-weight: 950;">{res['vivo']:.2f}</span></div>
            <div class="calc-row" style="border-bottom: none; background: #0a221a;"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff; font-size: 16px;">{res['medio']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker)}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
