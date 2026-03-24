import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: LAYOUT COMPACTO E SETA DISCRETA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 12px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 8px; text-align: center; font-size: 14px; }
    .asset-name { font-size: 15px; color: #fff; text-align: left; font-weight: bold; padding-left: 10px; }
    
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 5px 10px; border-bottom: 2px solid #ffffff; margin-bottom: 8px; }
    .bair-text { font-size: 38px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; } 
    .terminal-text { font-size: 38px; color: #d4a017; font-weight: 950; font-family: 'monospace'; }
    
    /* BLOCOS MAIS PRÓXIMOS */
    .calc-panel { border: 2px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 6px; }
    .calc-row { display: flex; justify-content: space-between; padding: 3px 6px; border-bottom: 1px solid #333; font-size: 12px; font-weight: bold; }
    
    /* BARRA E SETA MINIMALISTA */
    .bar-wrapper-dual { background: #0a141a; padding: 10px 8px 5px 8px; border: 2px solid #ffffff; border-radius: 4px; margin-top: 0px; text-align: center; position: relative; }
    .marker-container { display: flex; justify-content: space-between; position: absolute; width: calc(100% - 16px); top: 1px; font-size: 8px; color: #666; }
    .force-container-dual { background: #111; height: 14px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1.5px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; }
    
    .sinal-indicator { font-size: 20px; font-weight: 900; line-height: 1; margin-top: 2px; } /* SETA BEM DISCRETA */
    .blink { animation: blinker 2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }

    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; padding: 5px 0; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 13px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DADOS (SIMPLIFICADA) ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1]*m, "cl": d['Open'].iloc[0]*m, "mx": d['High'].max()*m, "mn": d['Low'].min()*m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0}

def calcular_k97(eixo_dol, spot_at, spot_cl, spot_mx, spot_mn):
    v_spreed = (spot_mx - spot_mn) / 8
    alvo_max, alvo_min = spot_mx + v_spreed, spot_mn + v_spreed
    p50_up = (alvo_max + eixo_dol) / 2
    
    # Barra
    diff = spot_at - eixo_dol
    p_v, p_r = (min(100, abs(diff)/10), 0) if diff < 0 else (0, min(100, abs(diff)/10))
    
    # Seta Binária Discreta
    if spot_at < p50_up: seta, cor = "▼ VENDA", "#ff4d4d"
    else: seta, cor = "▲ COMPRA", "#00ff88"
    
    return {"max": alvo_max, "min": alvo_min, "p50": p50_up, "p_v": p_v, "p_r": p_r, "seta": seta, "cor": cor, "spreed": v_spreed}

# --- EXECUÇÃO ---
a_dol = 5246.00 # Axis fixo para exemplo
spot = fetch("USDBRL=X")
res = calcular_k97(a_dol, spot['at'], spot['cl'], spot['mx'], spot['mn'])

# Header
st.markdown(f'<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="terminal-text">-K97</span></div></div>', unsafe_allow_html=True)

c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div class="main-grid"><table class="terminal-table">...TABELA ATIVOS...</table></div>', unsafe_allow_html=True)

with c2:
    # Blocos aproximados com margin-bottom reduzido
    st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁX</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#00ff88;"><span>MÍN</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span>SPOT</span> <span style="color:#00f2ff;">{spot['at']:.2f}</span></div><div class="calc-row"><span>SPREAD</span> <span style="color:#ff4d4d;">{res['spreed']:.2f}</span></div></div>""", unsafe_allow_html=True)
    
    # Bloco da Seta e Barra colados
    st.markdown(f"""
    <div class="bar-wrapper-dual">
        <div class="force-container-dual">
            <div class="center-line"></div>
            <div class="bar-side"><div class="fill-green" style="width:{res['p_v']}%;"></div></div>
            <div class="bar-side"><div class="fill-red" style="width:{res['p_r']}%;"></div></div>
        </div>
        <div class="sinal-indicator blink" style="color:{res['cor']};">{res['seta']}</div>
    </div>
    """, unsafe_allow_html=True)

# Rodapé
st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text" style="color:#fff;">DOL: {spot['at']:.2f} • EWZ: 37.85 • DXY: 104.20</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
