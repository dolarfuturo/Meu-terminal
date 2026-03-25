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
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 8px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 6px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 16px; font-weight: 950; text-align: center; margin-top: 5px; min-height: 16px; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS OTIMIZADO ---
@st.cache_data(ttl=2) # Cache de 2 segundos para evitar gargalo de rede
def fetch_fast(s):
    try:
        t = yf.Ticker(s)
        # Busca apenas 1 dia de dados 1m para ser leve
        d = t.history(period="1d", interval="1m")
        if d.empty: return {"at": 0.0, "cl": 1.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {
            "at": d['Close'].iloc[-1] * m,
            "cl": t.info.get('previousClose', d['Open'].iloc[0]) * m,
            "op": d['Open'].iloc[0] * m,
            "mx": d['High'].max() * m,
            "mn": d['Low'].min() * m
        }
    except: return {"at": 0.0, "cl": 1.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

@st.cache_data(ttl=600)
def calcular_sentinela():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="5d", interval="1d")
        if df.empty: return 37.85
        return (df['High'].iloc[-2] + df['Low'].iloc[-2]) / 2
    except: return 37.85

# --- LÓGICA DE CÁLCULO ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    st.markdown("### ⚙️ PAINEL K97")
    a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
    st.button("SALVAR")

spot_live = fetch_fast("USDBRL=X")
ewz_live = fetch_fast("EWZ")

def processar_k97():
    v_spreed = (spot_live['mx'] - spot_live['mn']) / 8
    v_spot = ((spot_live['at'] / spot_live['cl']) - 1)
    v_ewz = ((ewz_live['at'] / a_ewz) - 1) if a_ewz > 0 else 0
    v_final = (v_spot * 0.6) - (v_ewz * 0.4)
    
    # Exaustão
    dist_base = abs(a_dol - ((spot_live['mx'] + spot_live['mn']) / 2))
    diff = spot_live['at'] - a_dol
    p_v, p_r = 0, 0
    if dist_base > 0:
        if diff < 0: p_v = min(100, (abs(diff)/(dist_base*2))*100)
        else: p_r = min(100, (abs(diff)/(dist_base*2))*100)
    
    seta, cor = ("", "#000")
    if p_v >= 100: seta, cor = "▲ COMPRA", "#00ff88"
    elif p_r >= 100: seta, cor = "▼ VENDA", "#ff4d4d"
    
    return v_spreed, v_final, p_v, p_r, seta, cor

v_spreed, v_final, p_v, p_r, seta, cor = processar_k97()

# --- UI ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div><span class="bair-text">BAIR</span><span style="font-size:46px;color:#fff;">-</span><span class="terminal-text">K97</span></div><div class="clock-box"><span style="color:#d4a017; font-size:10px;">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div>""", unsafe_allow_html=True)

c_main, c_side = st.columns([3, 1])
with c_main:
    html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
    ativos = {"DOLFUT": "USDBRL=X", "DOLSPOT": "USDBRL=X", "EWZ": "EWZ", "DXY": "DX-Y.NYB", "SPX": "^GSPC"}
    for lbl, sym in ativos.items():
        d = spot_live if lbl in ["DOLFUT", "DOLSPOT"] else (ewz_live if lbl == "EWZ" else fetch_fast(sym))
        p = (d['at'] + v_spreed) if lbl == "DOLFUT" else d['at']
        var = ((p/d['cl'])-1)*100
        html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{p/1000 if 'DOL' in lbl else p:.4f}</td><td>{d['cl']/1000 if 'DOL' in lbl else d['cl']:.4f}</td><td>{d['mx']/1000 if 'DOL' in lbl else d['mx']:.4f}</td><td>{d['mn']/1000 if 'DOL' in lbl else d['mn']:.4f}</td><td style='color:{("#00ff88" if var>=0 else "#ff4d4d")};'>{var:+.2f}%</td></tr>"
    st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

with c_side:
    st.markdown(f"""<div class="calc-panel">
        <div class="calc-row" style="color:#ff4d4d;"><span>MAX FUT</span> <span>{spot_live['mx']+v_spreed:.2f}</span></div>
        <div style="text-align:center; padding:10px; color:#00f2ff; font-size:18px; border-top:1px solid #444; border-bottom:1px solid #444;">AXIS: {a_dol:.2f}</div>
        <div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MIN FUT</span> <span>{spot_live['mn']+v_spreed:.2f}</span></div>
    </div>""", unsafe_allow_html=True)
    
    st.markdown(f"""<div class="calc-panel">
        <div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{spot_live['at']+v_spreed:.2f}</span></div>
        <div class="calc-row"><span>SPREAD</span> <span style="color:#d4a017;">{v_spreed:.2f}</span></div>
        <div class="calc-row" style="border-bottom:none;"><span>VAR AXIS</span> <span style="color:#fff;">{((spot_live['at']+v_spreed)/a_dol-1)*100:+.2f}%</span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="calc-panel"><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width:{p_v}%;"></div></div><div class="bar-side"><div class="fill-red" style="width:{p_r}%;"></div></div></div><div class="sinal-indicator blink" style="color:{cor};">{seta}</div></div>""", unsafe_allow_html=True)

time.sleep(5)
st.rerun()
