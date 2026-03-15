import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: ESTILIZAÇÃO COMPACTA E ALINHADA ---
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
    /* AJUSTE DE TEMPO E FLUIDEZ DO TICKER SOLICITADO */
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    
    .monitor-bar { background: #0a141a; border: 2.2px solid #ffffff; padding: 6px; text-align: center; color: #00f2ff; font-weight: bold; font-family: monospace; border-radius: 4px; margin-bottom: 8px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
@st.cache_data(ttl=300)
def calcular_referencias_axis():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=False)
        if df.empty: return 37.85, 38.10, 37.60
        df.index = df.index.tz_convert('America/Sao_Paulo')
        df_filtered = df.between_time(dt_time(10, 30), dt_time(17, 0))
        if not df_filtered.empty:
            mx = df_filtered['High'].max()
            mn = df_filtered['Low'].min()
            return (mx + mn) / 2, mx, mn
    except: pass
    return 37.85, 38.10, 37.60

def calcular_k97_total(axis_ewz, p_ewz_atual, max_ewz, min_ewz, axis_dol):
    v_atual = ((axis_ewz / p_ewz_atual) - 1) * 100 / 1.5
    dolar_vivo = axis_dol * (1 + (v_atual / 100))
    v_neg = ((axis_ewz / max_ewz) - 1) * 100 / 1.5
    v_pos = ((axis_ewz / min_ewz) - 1) * 100 / 1.5
    alvo_max, alvo_min = axis_dol * (1 + (v_pos / 100)), axis_dol * (1 + (v_neg / 100))
    return {
        "vivo": dolar_vivo, 
        "fraja": axis_dol * (1 + (((axis_ewz / p_ewz_atual) - 1) * 100 / 4.5 / 100)),
        "medio": axis_dol * (1 + (((axis_ewz / ((max_ewz + min_ewz) / 2)) - 1) * 100 / 100)),
        "max": alvo_max, "min": alvo_min,
        "p75_up": (axis_dol + (alvo_max - axis_dol)*0.75), "p50_up": (axis_dol + alvo_max) / 2, "p25_up": (axis_dol + (alvo_max - axis_dol)*0.25),
        "p75_down": (axis_dol + (alvo_min - axis_dol)*0.75), "p50_down": (axis_dol + alvo_min) / 2, "p25_down": (axis_dol + (alvo_min - axis_dol)*0.25)
    }

def fetch(s):
    try:
        d = yf.Ticker(s).history(period="1d", interval="1m", prepost=False)
        if d.empty: return None
        d.index = d.index.tz_convert('America/Sao_Paulo')
        d_op = d.between_time(dt_time(10, 30), dt_time(17, 0))
        if d_op.empty:
            return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
        return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d_op['High'].max(), "mn": d_op['Low'].min()}
    except: return None

# --- SIDEBAR ---
axis_auto, mx_ref, mn_ref = calcular_referencias_axis()
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    with st.form("ajuste_axis"):
        a_ewz = st.number_input("AXIS EWZ:", value=float(axis_auto), format="%.2f")
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        salvar = st.form_submit_button("SALVAR VARIÁVEIS")

# --- UI HEADER ---
tz_sp = pytz.timezone('America/Sao_Paulo')
br_t = datetime.now(tz_sp).strftime('%H:%M')
ny_t = datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M')
ld_t = datetime.now(pytz.timezone('Europe/London')).strftime('%H:%M')

st.markdown(f"""
<div class="header-bair">
    <div class="title-box">
        <span class="bair-text">BAIR</span>
        <span class="sep-text">-</span>
        <span class="terminal-text">TERMINAL DOLAR</span>
    </div>
    <div class="clock-container">
        <div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{br_t}</span></div>
        <div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{ny_t}</span></div>
        <div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{ld_t}</span></div>
    </div>
</div>""", unsafe_allow_html=True)

ewz_live = fetch("EWZ")
if ewz_live:
    res = calcular_k97_total(a_ewz, ewz_live['at'], mx_ref, mn_ref, a_dol)
    h1, h2 = st.columns([3, 1])
    h1.markdown('<div class="monitor-bar">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
    h2.markdown('<div class="monitor-bar">CÁLCULOS DE PROJEÇÕES</div>', unsafe_allow_html=True)

    c_main, c_side = st.columns([3, 1])
    with c_main:
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        v2_var = ((res['vivo'] / a_dol) - 1) * 100
        v2_cor = "#00ff00" if v2_var >= 0 else "#ff0000"
        html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{v2_cor}; font-weight:bold;'>{v2_var:+.2f}%</td></tr>"
        
        ativos_config = {"SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
        ticker_items = [f"<span style='color:#fff;'>DOLFUT:</span> <span style='color:{v2_cor};'>{v2_var:+.2f}%</span>"]
        
        for label, sym in ativos_config.items():
            d = fetch(sym)
            if d:
                fmt = ".3f" if label == "XAU/USD" else (".4f" if "USD" in label or label == "SPOT" else ".2f")
                v = ((d['at']/d['cl'])-1)*100
                c = "#00ff00" if v >= 0 else "#ff0000"
                html_table += f"<tr><td class='asset-name'>{label}</td><td class='price-col'>{d['at']:{fmt}}</td><td>{d['cl']:{fmt}}</td><td>{d['cl']:{fmt}}</td><td>{d['mx']:{fmt}}</td><td>{d['mn']:{fmt}}</td><td style='color:{c}; font-weight:bold;'>{v:+.2f}%</td></tr>"
                ticker_items.append(f"<span style='color:#fff;'>{label}:</span> <span style='color:{c};'>{v:+.2f}%</span>")
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        # BLOCO 1: PROJEÇÕES
        st.markdown(f"""
        <div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div>
            <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0; letter-spacing: 2px;">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)
        
        # BLOCO 2: CONSOLIDADO (CORES CUSTOMIZADAS E ALINHADAS)
        st.markdown(f"""
        <div class="calc-panel" style="border-color: #ffffff; margin-bottom: 0px;">
            <div class="calc-row" style="border-bottom: 1px solid #444; padding: 10px 8px;">
                <span style="color:#ffffff; font-size: 13px;">DOLFUT</span> 
                <span style="color:#00f2ff; font-size: 19px; font-weight: 950;">{res['vivo']:.2f}</span>
            </div>
            <div class="calc-row" style="border-bottom: 1px solid #444;">
                <span style="color:#ffff00; font-size: 12px;">MÉDIA DOL</span> 
                <span style="color:#00f2ff; font-size: 16px;">{res['medio']:.2f}</span>
            </div>
            <div class="calc-row" style="border-bottom: none;">
                <span style="color:#d4a017; font-size: 12px;">P. JUSTO</span> 
                <span style="color:#ffffff; font-size: 16px; font-weight: bold;">{res['fraja']:.2f}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    ticker_html = " • ".join(ticker_items)
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{ticker_html} • {ticker_html}</div></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
