import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet - RIGOROSAMENTE IGUAL AO CRYPTO
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- CSS: ESTILIZAÇÃO ESPELHADA NO CRYPTO ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container { padding-top: 0rem !important; padding-left: 1rem !important; padding-right: 1rem !important; } 
    .stApp { background-color: #0E1117 !important; }
    
    .header-container { text-align: center; padding: 5px 0px; border-bottom: 2px solid #FFD700; background-color: #0E1117; }
    .main-title { margin: 0px; line-height: 1.1; font-size: 30px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    
    .clock-row { display: flex; justify-content: center; gap: 20px; padding: 5px 0; font-weight: bold; font-size: 12px; font-family: monospace; color: #AAA; }
    
    .table-container { width: 100%; overflow-x: auto; margin-top: 10px; }
    .terminal-table { width: 100%; border-collapse: collapse; font-family: monospace; border: 1px solid #FFD700; }
    .terminal-table thead th { background-color: #1A1C23 !important; color: #FFD700; padding: 8px; border: 1px solid #FFD700; font-size: 11px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #FFD700; padding: 6px; text-align: center; font-weight: bold; font-size: 13px; color: white; }
    
    .calc-box { border: 1px solid #FFD700; background: #0E1117; margin-top: 10px; padding: 5px; }
    .calc-row { display: flex; justify-content: space-between; padding: 4px 10px; border-bottom: 1px solid #333; font-size: 12px; font-family: monospace; font-weight: bold; }
    
    /* BARRA DE FORÇA */
    .bar-wrapper-dual { background: #050505; padding: 5px; border: 1px solid #FFD700; text-align: center; margin-top: 5px; }
    .force-container-dual { background: #111; height: 10px; width: 100%; position: relative; display: flex; border: 1px solid #444; }
    .fill-green { background: #00ff88; height: 100%; float: right; }
    .fill-red { background: #ff4d4d; height: 100%; float: left; }
    .sinal-indicator { font-size: 12px; font-weight: bold; margin-top: 4px; font-family: monospace; }
    
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.2; } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS (SEM ALTERAÇÃO) ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1] * m, "cl": t.info.get('previousClose', d['Open'].iloc[0]) * m, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97_total(eixo_dol, spot_data):
    try:
        v_spreed = (spot_data['mx'] - spot_data['mn']) / 8
        v_spot = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        max_fut = spot_data['mx'] + v_spreed
        min_fut = spot_data['mn'] + v_spreed
        p_v = min(100, (abs(spot_data['at'] - eixo_dol)/20)*100) if spot_data['at'] < eixo_dol else 0
        p_r = min(100, (abs(spot_data['at'] - eixo_dol)/20)*100) if spot_data['at'] > eixo_dol else 0
        seta = "▲ COMPRA" if p_v > 80 else "▼ VENDA" if p_r > 80 else "AGUARDAR"
        return {"max_fut": max_fut, "min_fut": min_fut, "v_v": v_spot * 100, "spreed": v_spreed, "p_v": p_v, "p_r": p_r, "seta": seta}
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00)

placeholder = st.empty()

while True:
    spot_live = fetch("USDBRL=X")
    res = calcular_k97_total(a_dol, spot_live)
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))

    with placeholder.container():
        st.markdown(f"""
            <div class="header-container">
                <h1 class="main-title"><span class="bair-blue">BAIR</span> <span class="terminal-gold">- TERMINAL DOLLAR</span></h1>
                <div class="clock-row">
                    <span>🇧🇷 BRASÍLIA: <span style="color:#00ff00">{now.strftime('%H:%M:%S')}</span></span>
                    <span>🇺🇸 NEW YORK: <span>{now.astimezone(pytz.timezone('America/New_York')).strftime('%H:%M:%S')}</span></span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if res:
            # TABELA ÚNICA - LARGURA TOTAL IGUAL AO CRYPTO
            html = f"""<div class="table-container"><table class="terminal-table">
                <thead><tr><th>ATIVO</th><th>PREÇO</th><th>VAR</th><th>MÁXIMA</th><th>MÍNIMA</th><th>PROJ MAX</th><th>PROJ MIN</th><th>SPREAD</th></tr></thead>
                <tbody><tr>
                    <td>DOLFUT</td>
                    <td style="background:rgba(0,255,0,0.3); color:#00BFFF">{spot_live['at']:.2f}</td>
                    <td style="color:{'#00ff00' if res['v_v']>=0 else '#ff4d4d'}">{res['v_v']:.2f}%</td>
                    <td>{spot_live['mx']:.2f}</td>
                    <td>{spot_live['mn']:.2f}</td>
                    <td style="color:#ff4d4d">{res['max_fut']:.2f}</td>
                    <td style="color:#00ff00">{res['min_fut']:.2f}</td>
                    <td>{res['spreed']:.2f}</td>
                </tr></tbody></table></div>"""
            st.markdown(html, unsafe_allow_html=True)

            # BLOCO DE FORÇA EMBAIXO
            st.markdown(f"""
                <div class="bar-wrapper-dual">
                    <div class="force-container-dual">
                        <div style="width:50%; height:100%; border-right:1px solid #fff;">
                            <div class="fill-green" style="width:{res['p_v']}%"></div>
                        </div>
                        <div style="width:50%; height:100%;">
                            <div class="fill-red" style="width:{res['p_r']}%"></div>
                        </div>
                    </div>
                    <div class="sinal-indicator blink" style="color:#FFD700">{res['seta']} | K97 SYSTEM</div>
                </div>
            """, unsafe_allow_html=True)

    time.sleep(10)
