import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: LAYOUT ULTRA COMPACTO E SETA DISCRETA ---
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
    
    /* BLOCOS MAIS PRÓXIMOS */
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 6px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
    
    /* BARRA E SETA DISCRETA */
    .bar-wrapper-dual { background: #0a141a; padding: 10px 10px 4px 10px; border: 2.5px solid #ffffff; border-radius: 8px; margin-top: 0px; text-align: center; position: relative; }
    .marker-container { display: flex; justify-content: space-between; position: absolute; width: calc(100% - 20px); top: 2px; font-size: 9px; color: #888; font-weight: bold; }
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    
    .sinal-indicator { font-size: 20px; font-weight: 950; line-height: 1; margin-top: 2px; } /* SETA DIMINUÍDA */
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }

    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
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
        return {"at": d['Close'].iloc[-1]*m, "cl": (ref_close or d['Open'].iloc[0])*m, "op": d['Open'].iloc[0]*m, "mx": d['High'].max()*m, "mn": d['Low'].min()*m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97_total(eixo_dol, spot_data):
    try:
        v_spreed = (spot_data['mx'] - spot_data['mn']) / 8
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        alvo_max = spot_data['mx'] + v_spreed
        p50_up = (alvo_max + eixo_dol) / 2

        # Barra
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = (min(100, abs(diff)/10), 0) if diff < 0 else (0, min(100, abs(diff)/10))

        # SETA BINÁRIA SEMPRE VISÍVEL
        if spot_data['at'] < p50_up:
            seta, cor = "▼ VENDA", "#ff4d4d"
        else:
            seta, cor = "▲ COMPRA", "#00ff88"
        
        return {"max": alvo_max, "p50_up": p50_up, "p_v": p_v, "p_r": p_r, "seta": seta, "cor": cor, "spreed": v_spreed}
    except: return None

# --- UI ---
a_dol = 5246.00 # Exemplo Axis
spot_live = fetch("USDBRL=X")
ewz_live = fetch("EWZ")
res = calcular_k97_total(a_dol, spot_live)

# Header
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="terminal-text">-K97</span></div></div>""", unsafe_allow_html=True)

if res:
    c_main, c_side = st.columns([3, 1])
    with c_main:
        # Tabela simplificada para o código
        st.markdown('<div class="main-grid">... TABELA DE ATIVOS ...</div>', unsafe_allow_html=True)

    with c_side:
        # Blocos aproximados (margin-bottom: 4px)
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{spot_live['mn']:.2f}</span></div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span>SPOT</span> <span style="color:#00f2ff;">{spot_live['at']:.2f}</span></div><div class="calc-row" style="border:none;"><span>SPREAD</span> <span style="color:#ff4d4d;">{res['spreed']:.2f}</span></div></div>""", unsafe_allow_html=True)
        
        # Barra e Seta unidas
        st.markdown(f"""
        <div class="bar-wrapper-dual">
            <div class="marker-container">
                <div style="width: 50%; display: flex; justify-content: space-around; flex-direction: row-reverse;"><span>80</span><span>50</span></div>
                <div style="width: 2px;">|</div>
                <div style="width: 50%; display: flex; justify-content: space-around;"><span>50</span><span>80</span></div>
            </div>
            <div class="force-container-dual">
                <div class="center-line"></div>
                <div class="bar-side"><div class="fill-green" style="width: {res['p_v']}%;"></div></div>
                <div class="bar-side"><div class="fill-red" style="width: {res['p_r']}%;"></div></div>
            </div>
            <div class="sinal-indicator blink" style="color:{res['cor']};">{res['seta']}</div>
        </div>
        """, unsafe_allow_html=True)

# Rodapé
st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text" style="color:#fff;">DOLFUT: 0.00% • DXY: 0.10%</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
