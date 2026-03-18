import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: ALINHAMENTO MILIMÉTRICO ---
st.markdown("""
<style>
    header[data-testid="stHeader"] { visibility: hidden !important; }
    .stApp { background-color: #050a0e !important; }
    .block-container { padding: 0.5rem 1rem !important; }
    
    /* Força o alinhamento superior das colunas */
    [data-testid="stHorizontalBlock"] { align-items: stretch !important; gap: 10px !important; }
    [data-testid="column"] > div:first-child { margin-top: 0 !important; }

    /* Grade Principal */
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; height: 100%; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    
    /* Blocos da Direita - Ajuste de Altura para Alinhar */
    .right-container { display: flex; flex-direction: column; height: 100%; justify-content: space-between; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; }
    .panel-top { flex-grow: 1; margin-bottom: 10px; display: flex; flex-direction: column; justify-content: space-between; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }

    /* Header e Títulos */
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 10px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    
    /* RODAPÉ COLADO (Subido) */
    .ticker-wrapper { 
        width: 100%; background: #000; border: 2px solid #ffffff; 
        padding: 6px 0; overflow: hidden; white-space: nowrap; 
        margin-top: 5px; /* Reduzido para subir o rodapé */
    }
    .ticker-text { display: inline-block; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        pc = t.info.get('previousClose', d['Open'].iloc[0] if not d.empty else 0)
        if d.empty: return {"at": pc, "cl": pc, "mx": pc, "mn": pc, "op": pc}
        return {"at": d['Close'].iloc[-1], "cl": pc, "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97(e_ewz, p_ewz, mx_e, mn_e, e_dol):
    try:
        v_at = ((e_ewz / p_ewz) - 1) * 100 / 1.5
        v_fr = ((e_ewz / p_ewz) - 1) * 100 / 4.5
        ewz_m = (mx_e + mn_e) / 2
        v_m = ((e_ewz / ewz_m) - 1) * 100
        v_neg = ((e_ewz / mx_e) - 1) * 100 / 1.5
        v_pos = ((e_ewz / mn_e) - 1) * 100 / 1.5
        a_mx, a_mn = e_dol * (1 + (v_pos / 100)), e_dol * (1 + (v_neg / 100))
        return {
            "vivo": e_dol * (1 + (v_at / 100)), "fraja": e_dol * (1 + (v_fr / 100)), "medio": e_dol * (1 + (v_m / 100)),
            "ewz_med": ewz_m, "max": a_mx, "min": a_mn,
            "p75_up": (e_dol + (a_mx - e_dol)*0.75), "p50_up": (e_dol + a_mx) / 2, 
            "p25_up": (e_dol + (a_mx - e_dol)*0.25), "p75_down": (e_dol + (a_mn - e_dol)*0.75), 
            "p50_down": (e_dol + a_mn) / 2, "p25_down": (e_dol + (a_mn - e_dol)*0.25)
        }
    except: return None

# --- SIDEBAR ADM ---
with st.sidebar:
    a_ewz = st.number_input("AXIS EWZ", value=36.42)
    a_dol = st.number_input("AXIS DOLFUT", value=5246.0)

# --- HEADER ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span style="color:#fff; font-size:46px; margin:0 10px;">-</span><span class="terminal-text">TERMINAL DOLAR</span></div><div class="clock-box"><span style="font-size:10px; color:#d4a017; font-weight:bold; display:block;">BRASÍLIA</span><span style="color:#fff; font-size:17px; font-weight:bold;">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div>""", unsafe_allow_html=True)

ewz_live = fetch("EWZ")
res = calcular_k97(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol)

if res:
    c_main, c_side = st.columns([3, 1])
    
    with c_main:
        html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style="color:#d4a017">Price</th><th style="color:#d4a017">Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        ativos = {"DOLFUT": "BRL=X", "SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
        t_items = []

        for lbl, sym in ativos.items():
            d = fetch(sym)
            var = ((d['at']/d['cl'])-1)*100 if d['cl'] > 0 else 0
            color = "#00ff00" if var >= 0 else "#ff4d4d"
            val_at = (res['vivo']/1000) if lbl == "DOLFUT" else d['at']
            html += f"<tr><td class='asset-name'>{lbl}</td><td style='color:#00f2ff; font-weight:bold;'>{val_at:.4f}</td><td>{d['cl']:.4f}</td><td>{d['op']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
            t_items.append(f"<span style='color:#fff;'>{lbl}:</span> <span style='color:{color};'>{var:+.2f}%</span>")
        st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        st.markdown(f"""<div class="right-container">
            <div class="calc-panel panel-top">
                <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
                <div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div>
                <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
                <div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div>
                <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444;">AXIS: {a_dol:.2f}</div>
                <div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div>
                <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
                <div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div>
                <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
            </div>
            <div class="calc-panel" style="height: 125px;">
                <div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff; font-size:16px;">{res['vivo']:.2f}</span></div>
                <div class="calc-row"><span>MÉDIA DOL</span> <span style="color:#ffff00;">{res['medio']:.2f}</span></div>
                <div class="calc-row" style="border-bottom:none;"><span>P. JUSTO</span> <span style="color:#fff;">{res['fraja']:.2f}</span></div>
                <div style="display:flex; justify-content:space-around; padding-top:5px; border-top:1px solid #444; margin-top:5px;">
                    <span style="color:#00ff88; font-size:11px;">{ewz_live['mx']:.2f}</span>
                    <span style="color:#00f2ff; font-size:11px;">{res['ewz_med']:.2f}</span>
                    <span style="color:#ff4d4d; font-size:11px;">{ewz_live['mn']:.2f}</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Rodapé Colado
    t_str = " • ".join(t_items)
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{t_str} • {t_str} • {t_str}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
