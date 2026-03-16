import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

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
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .monitor-bar { background: #0a141a; border: 2.2px solid #ffffff; padding: 6px; text-align: center; color: #00f2ff; font-weight: bold; border-radius: 4px; margin-bottom: 8px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def calcular_eixo_automatico():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d")
        if df.empty: return 37.85, 38.10, 37.60
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        idx = -2 if (df.index[-1].date() == agora.date() and agora.hour < 18) else -1
        mx, mn = df['High'].iloc[idx], df['Low'].iloc[idx]
        return (mx + mn) / 2, mx, mn
    except: return 37.85, 38.10, 37.60

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    # Lógica: Se EWZ cai (p_ewz_atual menor que eixo), var_atual fica positiva
    var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 1.5
    dolar_vivo = eixo_dol * (1 + (var_atual / 100))
    var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 4.5
    dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
    ewz_medio_dia = (max_ewz + min_ewz) / 2
    var_medio = ((eixo_ewz / ewz_medio_dia) - 1) * 100 
    dolar_medio = eixo_dol * (1 + (var_medio / 100)) 
    v_neg, v_pos = ((eixo_ewz / max_ewz) - 1) * 100 / 1.5, ((eixo_ewz / min_ewz) - 1) * 100 / 1.5
    alvo_max, alvo_min = eixo_dol * (1 + (v_pos / 100)), eixo_dol * (1 + (v_neg / 100))
    return {
        "vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, 
        "v_atual": var_atual, "ewz_med": ewz_medio_dia, "max": alvo_max, "min": alvo_min,
        "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), "p50_up": (eixo_dol + alvo_max) / 2, 
        "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25), "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), 
        "p50_down": (eixo_dol + alvo_min) / 2, "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
    }

def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0}

# --- SIDEBAR ---
eixo_sug, _, _ = calcular_eixo_automatico()
with st.sidebar:
    with st.form("ajuste_axis"):
        a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        st.form_submit_button("SALVAR")

# --- HEADER ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div style="display:flex; align-items:center;"><span class="bair-text">BAIR</span><span style="color:white; font-size:46px; margin:0 10px;">-</span><span class="terminal-text">TERMINAL DOLAR</span></div><div style="display:flex; gap:10px;"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

ewz_live = fetch("EWZ")
if ewz_live:
    res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol)
    c_main, c_side = st.columns([3, 1])
    
    with c_main:
        st.markdown('<div class="monitor-bar">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        # DOLFUT CALCULADO (CONVERTIDO)
        v_d = ((res['vivo']/a_dol)-1)*100
        cd = "#00ff00" if v_d >= 0 else "#ff0000"
        html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{cd}; font-weight:bold;'>{v_d:+.2f}%</td></tr>"
        
        ticker_items = [f"DOLFUT: {v_d:+.2f}%"]
        outros = {"SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
        
        for lbl, sym in outros.items():
            d = fetch(sym)
            if lbl == "EWZ":
                # INVERSÃO SOLICITADA: Se EWZ cai, Var é Positiva (+)
                v = ((a_ewz / d['at']) - 1) * 100 if d['at'] > 0 else 0
                ref = a_ewz
            else:
                v = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                ref = d['cl']
            
            c = "#00ff00" if v >= 0 else "#ff0000"
            f = ".4f" if "USD" in lbl or lbl == "SPOT" else ".2f"
            html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:{f}}</td><td>{ref:{f}}</td><td>{d['cl']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{c}; font-weight:bold;'>{v:+.2f}%</td></tr>"
            ticker_items.append(f"{lbl}: {v:+.2f}%")
        
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        st.markdown('<div class="monitor-bar">PROJEÇÕES</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div><div style="text-align:center; padding:10px; color:#00f2ff; font-size:18px; border-y:1.5px solid #444;">AXIS: {a_dol:.2f}</div><div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div><div class="calc-row"><span>P. JUSTO</span> <span style="color:#fff;">{res['fraja']:.2f}</span></div><div style="display:flex; justify-content:space-around; font-size:11px; margin-top:5px;"><span style="color:#00ff88;">{ewz_live['mx']:.2f}</span><span style="color:#00f2ff;">{res['ewz_med']:.2f}</span><span style="color:#ff4d4d;">{ewz_live['mn']:.2f}</span></div></div>""", unsafe_allow_html=True)

    t_html = " • ".join(ticker_items)
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{t_html} • {t_html}</div></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
