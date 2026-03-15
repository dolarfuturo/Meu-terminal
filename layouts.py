import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: ESTILO LARANJA + RELÓGIOS + MARQUEE ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2px solid #1c3d4d; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #1c3d4d; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #1c3d4d; padding: 12px; text-align: center; font-size: 15px; }
    
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; color: #00f2ff; font-size: 26px; font-weight: bold; }
    .clock-container { display: flex; gap: 20px; color: #888; font-family: 'monospace'; font-size: 12px; }
    .clock-box { text-align: center; border: 1px solid #1c3d4d; padding: 5px; border-radius: 4px; background: #0a141a; }
    .clock-time { color: #fff; font-size: 16px; display: block; }

    .calc-panel { border: 2px solid #1c3d4d; border-radius: 8px; padding: 10px; background: #0a141a; font-family: monospace; }
    .calc-row { display: flex; justify-content: space-between; padding: 6px 8px; border-bottom: 1px solid #1c3d4d; font-size: 14px; font-weight: bold; }

    .ticker-wrapper { background: #000; border: 1px solid #1c3d4d; color: #d4a017; padding: 5px; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 30s linear infinite; font-family: 'monospace'; font-size: 12px; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE CÁLCULO K97 ---
@st.cache_data(ttl=600)
def calcular_eixo_automatico():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d")
        if df.empty: return 37.85, 38.10, 37.60
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        idx = -2 if agora.hour < 18 else -1
        mx, mn = df['High'].iloc[idx], df['Low'].iloc[idx]
        return (mx + mn) / 2, mx, mn
    except: return 37.85, 38.10, 37.60

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ref_ewz, min_ref_ewz, eixo_dol):
    var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 1.5
    dolar_vivo = eixo_dol * (1 + (var_atual / 100))
    var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 4.5
    dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
    
    ewz_medio_dia = (max_ref_ewz + min_ref_ewz) / 2
    var_medio = ((eixo_ewz / ewz_medio_dia) - 1) * 100 
    dolar_medio = eixo_dol * (1 + (var_medio / 100)) 
    
    v_neg = ((eixo_ewz / max_ref_ewz) - 1) * 100 / 1.5
    v_pos = ((eixo_ewz / min_ref_ewz) - 1) * 100 / 1.5
    alvo_max = eixo_dol * (1 + (v_pos / 100))
    alvo_min = eixo_dol * (1 + (v_neg / 100))
    
    return {
        "vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, 
        "v_atual": var_atual, "ewz_med": ewz_medio_dia, "v_med": var_medio,
        "max": alvo_max, "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), 
        "p50_up": (eixo_dol + alvo_max) / 2, "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25),
        "min": alvo_min, "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), 
        "p50_down": (eixo_dol + alvo_min) / 2, "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
    }

# --- DADOS E RELÓGIOS ---
eixo_sug, mx_sug, mn_sug = calcular_eixo_automatico()
br_t = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M')
ny_t = datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M')
ld_t = datetime.now(pytz.timezone('Europe/London')).strftime('%H:%M')

with st.sidebar:
    st.header("⚙️ AJUSTE K97")
    e_ewz = st.number_input("EIXO EWZ:", value=float(eixo_sug), format="%.2f")
    mx_ref_input = st.number_input("MAX EIXO (REF):", value=float(mx_sug), format="%.2f")
    mn_ref_input = st.number_input("MIN EIXO (REF):", value=float(mn_sug), format="%.2f")
    st.divider()
    e_dol = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f")

st.markdown(f"""<div class="header-bair"><div>BAIR - <span style="color: #d4a017;">TERMINAL DOLAR</span></div><div class="clock-container"><div class="clock-box">BRASÍLIA<span class="clock-time">{br_t}</span></div><div class="clock-box">NEW YORK<span class="clock-time">{ny_t}</span></div><div class="clock-box">LONDRES<span class="clock-time">{ld_t}</span></div></div></div>""", unsafe_allow_html=True)

def fetch(s):
    try:
        d = yf.Ticker(s).history(period="1d", interval="1m", prepost=True)
        return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return None

ewz_live = fetch("EWZ")
if ewz_live:
    res = calcular_k97_total(e_ewz, ewz_live['at'], mx_ref_input, mn_ref_input, e_dol)
    
    html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
    
    # Sintéticos baseados nos inputs do Eixo
    html_table += f"<tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>SINTÉTICO 2.0 (VIVO)</td><td style='color:#d4a017;'>{res['vivo']:.2f}</td><td>{e_dol:.2f}</td><td>{e_dol:.2f}</td><td>{res['max']:.2f}</td><td>{res['min']:.2f}</td><td style='color:#00f2ff;'>{res['v_atual']:+.2f}%</td></tr>"
    html_table += f"<tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>SINTÉTICO MÉDIO (50%)</td><td style='color:#d4a017;'>{res['medio']:.2f}</td><td>{e_dol:.2f}</td><td>{e_dol:.2f}</td><td>---</td><td>---</td><td style='color:#00f2ff;'>{res['v_med']:+.2f}%</td></tr>"
    html_table += f"<tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>SINTÉTICO 3.6 (FRAJA)</td><td style='color:#d4a017;'>{res['fraja']:.2f}</td><td>{e_dol:.2f}</td><td>{e_dol:.2f}</td><td>---</td><td>---</td><td style='color:#00f2ff;'>FRAJA</td></tr>"
    
    outros = {"SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GOLD": "GC=F", "BRENT": "BZ=F"}
    ticker_tape = f"VIVO: {res['vivo']:.2f} | FRAJA: {res['fraja']:.2f} | "
    
    for label, sym in outros.items():
        d = fetch(sym)
        if d:
            v = ((d['at']/d['cl'])-1)*100
            c = "#00f2ff" if v >= 0 else "#ff4d4d"
            html_table += f"<tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>{label}</td><td style='color:#d4a017;'>{d['at']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td style='color:{c};'>{v:+.2f}%</td></tr>"
            ticker_tape += f" • {label}: {v:+.2f}%"

    html_table += "</tbody></table></div>"
    
    col_main, col_side = st.columns([3, 1])
    with col_main:
        st.markdown(html_table, unsafe_allow_html=True)
        st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{ticker_tape * 3}</div></div>', unsafe_allow_html=True)
    with col_side:
        st.markdown(f"""<div class="calc-panel"><div style="color: #d4a017; text-align: center; font-size: 14px; font-weight: bold; margin-bottom: 10px;">PROJEÇÕES K97</div><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ff7675;"><span>75% UP</span> <span>{res['p75_up']:.2f}</span></div><div class="calc-row" style="color:#fab1a0;"><span>50% UP</span> <span>{res['p50_up']:.2f}</span></div><div class="calc-row" style="color:#ffeaa7;"><span>25% UP</span> <span>{res['p25_up']:.2f}</span></div><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 16px;">EIXO: {e_dol:.2f}</div><div class="calc-row" style="color:#ffeaa7;"><span>25% DN</span> <span>{res['p25_down']:.2f}</span></div><div class="calc-row" style="color:#81ecec;"><span>50% DN</span> <span>{res['p50_down']:.2f}</span></div><div class="calc-row" style="color:#55efc4;"><span>75% DN</span> <span>{res['p75_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)

time.sleep(2)
st.rerun()
