import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- FUNÇÕES DE PERSISTÊNCIA ---
def salvar_eixos(div_spreed, dol):
    with open("config_axis.txt", "w") as f:
        f.write(f"{div_spreed},{dol}")

def carregar_eixos():
    if os.path.exists("config_axis.txt"):
        try:
            with open("config_axis.txt", "r") as f:
                dados = f.read().split(",")
                return float(dados[0]), float(dados[1])
        except: pass
    return 8.0, 5246.0

div_spreed_salvo, eixo_dol_salvo = carregar_eixos()

if 'market_data' not in st.session_state: st.session_state.market_data = {}
if 'last_p' not in st.session_state: st.session_state.last_p = {}
if 'div_spreed_mem' not in st.session_state: st.session_state.div_spreed_mem = div_spreed_salvo
if 'a_dol_mem' not in st.session_state: st.session_state.a_dol_mem = eixo_dol_salvo

# --- CSS ---
st.markdown("""
<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; position: relative; }
    .main-title { margin: 0px; line-height: 1.2; font-size: 28px; font-family: monospace; padding-bottom: 5px; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .clock-row { display: flex; justify-content: center; gap: 15px; padding: 2px 0; font-weight: bold; font-size: 11px; font-family: monospace; color: #AAA; }
    .br-green { color: #00ff00; }
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 5px; text-transform: uppercase; font-size: 11px; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; font-size: 10px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 12px; }
    .asset-name { font-size: 12px; color: #fff; text-align: left; font-weight: bold; padding-left: 8px; }
    .price-col { font-weight: bold; color: #ffffff !important; }
    .f-up { background-color: #00ff00aa !important; }
    .f-dn { background-color: #ff0000aa !important; }
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-top: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; }
    .bar-wrapper-full { background: #0a141a; padding: 6px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; margin-top: 5px; }
    .force-container-dual { background: #111; height: 10px; width: 100%; position: relative; display: flex; border: 1px solid #444; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; }
    .fill-green { background: #00ff88; float: right; height: 100%; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; }
    .elastic-row { display: flex; justify-content: space-between; padding: 5px 10px; font-family: monospace; font-size: 12px; font-weight: bold; color: #00f2ff; border-top: 1px solid #333; margin-top: 5px; }
    .ticker-wrapper { width: 100%; background: #000; border-top: 1px solid #fff; padding: 4px 0; overflow: hidden; margin-top: 10px; }
    .ticker-text { white-space: nowrap; animation: marquee 30s linear infinite; font-family: monospace; font-size: 12px; color: #fff; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return st.session_state.market_data.get(s)
        m = 1000 if s == "USDBRL=X" else 1
        data = {"at": d['Close'].iloc[-1] * m, "cl": t.info.get('previousClose', d['Open'].iloc[0]) * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s)

def calcular_k97_total(div_spreed, p_ewz_atual, eixo_dol, spot_data):
    try:
        if not spot_data: return None
        amp = float(spot_data['mx'] - spot_data['mn'])
        v_spreed = amp / 8
        
        # ELASTICO
        max_t = eixo_dol + (amp * 0.75)
        min_t = eixo_dol - (amp * 0.25)
        dolar_medio = ((max_t + min_t) / 2) - v_spreed
        elastico = abs(eixo_dol - dolar_medio)
        
        # LÓGICA Y
        y_val = (eixo_dol + elastico) - spot_data['mx']
        
        high_e = (eixo_dol + elastico) - y_val
        low_e = (eixo_dol - elastico) + y_val # O segredo está nesse sinal de + aqui para simetria

        # BARRA DE FORÇA
        diff = spot_data['at'] - eixo_dol
        dist_barra = (abs(eixo_dol - ((spot_data['mx'] + spot_data['mn'])/2))) + (v_spreed/2)
        p_v, p_r = 0, 0
        if dist_barra > 0:
            calc_pct = (abs(diff) / (dist_barra * div_spreed)) * 100
            if diff < 0: p_v = min(100, calc_pct)
            else: p_r = min(100, calc_pct)

        return {
            "low_e": low_e, "high_e": high_e, "medio": dolar_medio, "spreed": v_spreed,
            "p_v": p_v, "p_r": p_r, "vivo": (eixo_dol + (eixo_dol * 1.002)) / 2, # Simplificado para exemplo
            "max_fut_1": eixo_dol + (elastico * 2), "min_fut_1": eixo_dol - (elastico * 2)
        }
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("ADM")
    a_dol = st.number_input("AXIS:", value=st.session_state.a_dol_mem)
    div_s = st.number_input("DIVISOR:", value=st.session_state.div_spreed_mem)
    if st.button("SALVAR"):
        st.session_state.a_dol_mem = a_dol
        st.session_state.div_spreed_mem = div_s
        salvar_eixos(div_s, a_dol)
        st.rerun()

# --- LOOP ---
placeholder = st.empty()
while True:
    spot = fetch("USDBRL=X")
    res = calcular_k97_total(div_s, 1, a_dol, spot)
    
    with placeholder.container():
        if res:
            st.markdown('<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL</span></h1></div>', unsafe_allow_html=True)
            c1, c2 = st.columns([2.8, 1.2])
            with c1:
                st.markdown('<div class="section-title">MONITORAMENTO</div>', unsafe_allow_html=True)
                st.markdown(f'''
                <div class="bar-wrapper-full">
                    <div class="force-container-dual">
                        <div class="center-line"></div>
                        <div class="bar-side"><div class="fill-green" style="width:{res['p_v']}%;"></div></div>
                        <div class="bar-side"><div class="fill-red" style="width:{res['p_r']}%;"></div></div>
                    </div>
                    <div class="elastic-row">
                        <span>LOW: {res['low_e']:.2f}</span>
                        <span>HIGH: {res['high_e']:.2f}</span>
                    </div>
                </div>''', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="calc-panel"><div class="calc-row">AXIS: {a_dol:.2f}</div><div class="calc-row">MEDIO: {res["medio"]:.2f}</div></div>', unsafe_allow_html=True)

    time.sleep(5)
