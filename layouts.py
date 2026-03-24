import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: LAYOUT ULTRA COMPACTO (ZOOM 92%) ---
st.markdown("""
<style>
    /* Zoom Global e Reset de Espaçamento */
    .stApp { 
        background-color: #050a0e !important; 
        zoom: 0.92; /* Diminui o layout como um todo */
    }
    
    .main-grid { border: 2px solid #ffffff; border-radius: 6px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 11px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 13px; }
    .asset-name { font-size: 14px; color: #fff; text-align: left; font-weight: bold; padding-left: 10px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    
    /* Header Menor */
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 4px 10px; border-bottom: 2px solid #ffffff; margin-bottom: 5px; }
    .bair-text { font-size: 38px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 38px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 2px 8px; border-radius: 4px; background: #0a141a; min-width: 85px; }
    .clock-label { font-size: 9px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 14px; font-weight: bold; display: block; }
    
    /* Blocos Colados (Mínima Margem) */
    .calc-panel { border: 2px solid #ffffff; border-radius: 6px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 3px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #333; font-size: 12px; font-weight: bold; align-items: center; }
    
    /* Barra e Seta 20px */
    .bar-wrapper-dual { background: #0a141a; padding: 10px 10px 4px 10px; border: 2px solid #ffffff; border-radius: 6px; margin-top: 0px; text-align: center; position: relative; }
    .marker-container { display: flex; justify-content: space-between; position: absolute; width: calc(100% - 20px); top: 1px; font-size: 8px; color: #888; }
    .force-container-dual { background: #111; height: 14px; width: 100%; border-radius: 3px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 3px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; }
    
    .sinal-indicator { font-size: 20px; font-weight: 950; line-height: 1; margin-top: 2px; }
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }

    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 5px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #fff; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        ref_close = t.info.get('previousClose')
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1] * m, "cl": (ref_close or d['Open'].iloc[0]) * m, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

@st.cache_data(ttl=600)
def calcular_sentinela():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d")
        mx, mn = df['High'].iloc[-2], df['Low'].iloc[-2]
        return (mx + mn) / 2
    except: return 37.85

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol, spot_data):
    try:
        v_spreed = (spot_data['mx'] - spot_data['mn']) / 8
        v_spot = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        v_ewz = ((p_ewz_atual / fetch("EWZ")['cl']) - 1) if fetch("EWZ")['cl'] > 0 else 0
        v_final = (v_spot * 0.6) - (v_ewz * 0.4)
        
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        alvo_max = spot_data['mx'] + v_spreed
        p50_up = (alvo_max + eixo_dol) / 2
        
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = (min(100, abs(diff)/10), 0) if diff < 0 else (0, min(100, abs(diff)/10))

        if spot_data['at'] < p50_up:
            seta, cor = "▼ VENDA", "#ff4d4d"
        else:
            seta, cor = "▲ COMPRA", "#00ff88"
            
        return {"vivo": spot_data['at'], "fraja": eixo_dol * (1 + (v_final/2)), "medio": dolar_medio, "max": alvo_max, "min": spot_data['mn'] + v_spreed, "p50_up": p50_up, "p50_down": (spot_data['mn'] + v_spreed + eixo_dol)/2, "p_v": p_v, "p_r": p_r, "seta": seta, "cor": cor, "spreed": v_spreed, "v_v": v_final*100}
    except: return None

# --- UI ---
eixo_sug = calcular_sentinela()
a_ewz = 37.85
a_dol = 5246.00 # Axis fixo

tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="terminal-text">-K97</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">SP</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">NY</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

spot_live = fetch("USDBRL=X")
ewz_live = fetch("EWZ")
res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol, spot_live)

if res:
    c_main, c_side = st.columns([3, 1])
    with c_main:
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        outros = {"DOLFUT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "EUR/USD": "EURUSD=X", "PETROLEO": "BZ=F"}
        for lbl, sym in outros.items():
            d = spot_live if lbl == "DOLFUT" else fetch(sym)
            var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
            color = "#00ff00" if var >= 0 else "#ff4d4d"
            html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{(d['at']/1000 if 'DOL' in lbl else d['at']):.4f}</td><td>{(d['cl']/1000 if 'DOL' in lbl else d['cl']):.4f}</td><td>{(d['mx']/1000 if 'DOL' in lbl else d['mx']):.4f}</td><td>{(d['mn']/1000 if 'DOL' in lbl else d['mn']):.4f}</td><td style='color:{color};'>{var:+.2f}%</td></tr>"
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁX</span> <span>{res['max']:.2f}</span></div><div style="text-align:center; padding:4px; color:#00f2ff; font-weight:bold; border-bottom:1px solid #333;">AXIS: {a_dol:.2f}</div><div class="calc-row" style="color:#00ff88; border:none;"><span>MÍN</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span>SPOT</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div><div class="calc-row" style="border:none;"><span>SPREAD</span> <span style="color:#ff4d4d;">{res['spreed']:.2f}</span></div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="bar-wrapper-dual"><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width:{res['p_v']}%;"></div></div><div class="bar-side"><div class="fill-red" style="width:{res['p_r']}%;"></div></div></div><div class="sinal-indicator blink" style="color:{res['cor']};">{res['seta']}</div></div>""", unsafe_allow_html=True)

time.sleep(5)
st.rerun()
