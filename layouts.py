import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- SISTEMA DE CACHE ---
if 'market_data' not in st.session_state:
    st.session_state.market_data = {}
if 'last_p' not in st.session_state:
    st.session_state.last_p = {}

# --- CSS: MANTIDO ORIGINAL ---
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    .stApp { background-color: #050a0e !important; }
    .header-container { text-align: center; padding: 5px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; }
    .main-title { margin: 0px; line-height: 1.0; font-size: 28px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .clock-row { display: flex; justify-content: center; gap: 20px; padding: 5px 0; font-weight: bold; font-size: 11px; font-family: monospace; }
    .clock-item { color: #AAA; }
    .br-green { color: #00ff00; }
    .white-time { color: #ffffff; }
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 3px; margin-bottom: 5px; text-transform: uppercase; font-size: 11px; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 11px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 13px; transition: background-color 0.3s; }
    .asset-name { font-size: 13px; color: #fff; text-align: left; font-weight: bold; padding-left: 10px; }
    .price-col { font-weight: bold; color: #ffffff !important; }
    .bar-wrapper-dual { background: #0a141a; padding: 8px 8px 4px 8px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; position: relative; }
    .force-scale { display: flex; justify-content: space-between; font-size: 9px; font-family: monospace; color: #AAA; margin-bottom: 2px; padding: 0 2px; }
    .force-container-dual { background: #111; height: 12px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 2px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 13px; font-weight: 900; line-height: 1; margin-top: 4px; min-height: 14px; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return st.session_state.market_data.get(s)
        ref_close = t.info.get('previousClose')
        m = 1000 if s == "USDBRL=X" else 1
        data = {
            "at": d['Close'].iloc[-1] * m, 
            "cl": (ref_close or d['Open'].iloc[0]) * m, 
            "op": d['Open'].iloc[0] * m, 
            "mx": d['High'].max() * m, 
            "mn": d['Low'].min() * m
        }
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s)

def calcular_k97_total(eixo_dol, spot_data):
    try:
        if not spot_data: return None
        amp = spot_data['mx'] - spot_data['mn']
        v_spreed = amp / 8
        
        # 1. MÉDIA DA GRADE (BLOCOS)
        x1, x2 = amp * 0.77, amp * 0.23
        max_original, min_original = eixo_dol + x1, eixo_dol - x2
        media_grade = ((max_original + min_original) / 2) - v_spreed
        
        # 2. MÉDIA PURA DO SPOT (CALIBRAGEM BARRA)
        media_pura_spot = (spot_data['mx'] + spot_data['mn']) / 2
        
        # PROJEÇÕES
        x_val = abs(eixo_dol - media_grade)
        res_calc = {
            "max_fut": eixo_dol + (x_val * 4),
            "max_med": (eixo_dol + (x_val * 4)) - x_val,
            "max_1": eixo_dol + (x_val * 2),
            "min_1": eixo_dol - (x_val * 2),
            "min_med": (eixo_dol - (x_val * 4)) + x_val,
            "min_fut": eixo_dol - (x_val * 4)
        }
        
        # BARRA DE FORÇA
        dist_base = abs(eixo_dol - media_pura_spot)
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = 0, 0
        if dist_base > 0:
            if diff < 0: p_v = min(100, (abs(diff)/(dist_base*2))*100)
            else: p_r = min(100, (abs(diff)/(dist_base*2))*100)
        
        seta = ""
        cor = "#000000"
        if p_v >= 100: seta, cor = "▲ REGIÃO DE COMPRA", "#00ff88"
        elif p_r >= 100: seta, cor = "▼ REGIÃO DE VENDA", "#ff4d4d"

        return {
            "res": res_calc, "medio": media_grade, "p_v": p_v, "p_r": p_r, 
            "seta": seta, "cor": cor, "spreed": v_spreed,
            "mx_g": max_original, "mn_g": min_original
        }
    except: return None

# --- UI ---
with st.sidebar:
    a_dol = st.number_input("AXIS DOLFUT:", value=5244.50, format="%.2f")

placeholder = st.empty()

while True:
    spot = fetch("USDBRL=X")
    if spot:
        res = calcular_k97_total(a_dol, spot)
        with placeholder.container():
            st.markdown(f'<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1></div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                # Tabela simples para evitar o erro de Value
                html = f"""<div class="main-grid"><table class="terminal-table">
                <tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th></tr>
                <tr><td class='asset-name'>DOLSPOT</td><td>{spot['at']/1000:.4f}</td><td>{spot['cl']/1000:.4f}</td><td>{spot['mx']/1000:.4f}</td><td>{spot['mn']/1000:.4f}</td></tr>
                <tr><td class='asset-name'>DOLFUT</td><td>-</td><td>{a_dol/1000:.4f}</td><td>{res['mx_g']/1000:.4f}</td><td>{res['mn_g']/1000:.4f}</td></tr>
                </table></div>"""
                st.markdown(html, unsafe_allow_html=True)
                
            with c2:
                st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                st.markdown(f"""<div class="calc-panel">
                    <div class="calc-row" style="color:#ff4d4d;"><span>MAX FUT</span> <span>{res['res']['max_fut']:.2f}</span></div>
                    <div class="calc-row" style="color:#ffff00;"><span>MAX 1</span> <span>{res['res']['max_1']:.2f}</span></div>
                    <div style="text-align:center; padding:5px; color:#00f2ff; font-weight:bold;">AXIS: {a_dol:.2f}</div>
                    <div class="calc-row" style="color:#ffff00;"><span>MIN 1</span> <span>{res['res']['min_1']:.2f}</span></div>
                    <div class="calc-row" style="color:#00ff88;"><span>MIN FUT</span> <span>{res['res']['min_fut']:.2f}</span></div>
                    <hr style="margin:5px 0; border:0.5px solid #444;">
                    <div class="calc-row"><span>MÉDIA GRADE</span> <span>{res['medio']:.2f}</span></div>
                    <div class="calc-row"><span>SPREED</span> <span>{res['spreed']:.2f}</span></div>
                </div>""", unsafe_allow_html=True)
                
                st.markdown(f"""<div class="bar-wrapper-dual">
                    <div class="force-scale"><span>100%</span><span>0%</span><span>100%</span></div>
                    <div class="force-container-dual">
                        <div class="center-line"></div>
                        <div class="bar-side"><div class="fill-green" style="width:{res['p_v']}%;"></div></div>
                        <div class="bar-side"><div class="fill-red" style="width:{res['p_r']}%;"></div></div>
                    </div>
                    <div class="sinal-indicator blink" style="color:{res['cor']};">{res['seta']}</div>
                </div>""", unsafe_allow_html=True)

    time.sleep(2)
