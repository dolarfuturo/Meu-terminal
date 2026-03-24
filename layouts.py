import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: COMPACTAÇÃO DE 1,5CM E SETA DISCRETA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    
    /* Tabelas e Containers com espaçamento reduzido */
    .main-grid { border: 2px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 11px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 13px; }
    .asset-name { font-size: 14px; color: #fff; text-align: left; font-weight: bold; padding-left: 8px; }
    
    /* Header Slim */
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 2px 10px; border-bottom: 2px solid #ffffff; margin-bottom: 6px; }
    .bair-text { font-size: 36px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 36px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 2px 6px; border-radius: 4px; background: #0a141a; min-width: 75px; }
    .clock-label { font-size: 8px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 13px; font-weight: bold; display: block; }
    
    /* Blocos Laterais "Colados" */
    .calc-panel { border: 2.2px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 2px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #333; font-size: 12px; font-weight: bold; }
    
    /* Barra K97 e Seta de 20px (aprox 1.5cm) */
    .bar-wrapper-dual { background: #0a141a; padding: 8px 8px 4px 8px; border: 2.2px solid #ffffff; border-radius: 4px; margin-top: 0px; text-align: center; position: relative; }
    .marker-container { display: flex; justify-content: space-between; position: absolute; width: calc(100% - 16px); top: 1px; font-size: 8px; color: #777; }
    .force-container-dual { background: #111; height: 12px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 3px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; }
    
    .sinal-indicator { font-size: 20px; font-weight: 950; line-height: 1; margin-top: 2px; }
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }

    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 6px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #fff; }
</style>
""", unsafe_allow_html=True)

# --- LOGICA E UI ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1]*m, "cl": d['Open'].iloc[0]*m, "mx": d['High'].max()*m, "mn": d['Low'].min()*m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0}

a_dol = 5246.00 
spot = fetch("USDBRL=X")
diff = spot['at'] - a_dol
p_v, p_r = (min(100, abs(diff)/15*100), 0) if diff < 0 else (0, min(100, abs(diff)/15*100))
seta, cor = ("▼ VENDA", "#ff4d4d") if spot['at'] < (a_dol + 10) else ("▲ COMPRA", "#00ff88")

# Header
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="terminal-text">-K97</span></div><div class="clock-box"><span class="clock-label">SP</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div>""", unsafe_allow_html=True)

c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Var</th></tr></thead><tbody><tr><td class="asset-name">DOLFUT</td><td class="price-col">'+f"{spot['at']:.2f}"+'</td><td style="color:#00ff88;">+0.12%</td></tr></tbody></table></div>', unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span>MAX</span><span>{spot['mx']:.2f}</span></div><div style="text-align:center;color:#00f2ff;font-weight:bold;font-size:14px;padding:2px;">AXIS: {a_dol}</div><div class="calc-row" style="border:none;"><span>MIN</span><span>{spot['mn']:.2f}</span></div></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="bar-wrapper-dual"><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width:{p_v}%;"></div></div><div class="bar-side"><div class="fill-red" style="width:{p_r}%;"></div></div></div><div class="sinal-indicator blink" style="color:{cor};">{seta}</div></div>""", unsafe_allow_html=True)

st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">K97 TERMINAL ATIVO • DOLFUT {spot["at"]:.2f} • AXIS {a_dol}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
