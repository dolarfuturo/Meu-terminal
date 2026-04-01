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
    return 1.0, 5264.50  # Default: Divisor 1.0 (X1) e Axis Dol

div_spreed_salvo, eixo_dol_salvo = carregar_eixos()

if 'market_data' not in st.session_state:
    st.session_state.market_data = {}
if 'last_p' not in st.session_state:
    st.session_state.last_p = {}
if 'div_spreed_mem' not in st.session_state:
    st.session_state.div_spreed_mem = div_spreed_salvo
if 'a_dol_mem' not in st.session_state:
    st.session_state.a_dol_mem = eixo_dol_salvo

# --- CSS: DESIGN TERMINAL ---
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    .stApp { background-color: #050a0e !important; }
    .header-container { text-align: center; padding: 5px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; position: relative; }
    .main-title { margin: 0px; line-height: 1.0; font-size: 28px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .clock-row { display: flex; justify-content: center; gap: 20px; padding: 5px 0; font-weight: bold; font-size: 11px; font-family: monospace; }
    .clock-item { color: #AAA; }
    .br-green { color: #00ff00; }
    .white-time { color: #ffffff; }
    .date-container { position: absolute; bottom: 5px; right: 0; width: 20%; text-align: center; font-family: monospace; font-size: 11px; font-weight: bold; color: #ffffff; }
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 3px; margin-bottom: 5px; text-transform: uppercase; font-size: 11px; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 11px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 13px; transition: background-color 0.3s; }
    .asset-name { font-size: 13px; color: #fff; text-align: left; font-weight: bold; padding-left: 10px; }
    .price-col { font-weight: bold; color: #ffffff !important; }
    .f-up { background-color: #00ff00aa !important; }
    .f-dn { background-color: #ff0000aa !important; }
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 3px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; align-items: center; background-color: transparent !important; }
    .row-med { font-size: 9px !important; color: #ffffff; opacity: 0.9; padding: 2px 6px !important; }
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
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 5px 0; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .txt-green { color: #00ff88 !important; }
    .txt-yellow { color: #ffff00 !important; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return st.session_state.market_data.get(s)
        m = 1000 if s == "USDBRL=X" else 1
        data = {"at": d['Close'].iloc[-1] * m, "cl": t.info.get('previousClose', d['Open'].iloc[0]) * m, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s)

def calcular_k97_total(div_spreed, eixo_dol, spot_data):
    try:
        if not spot_data: return None
        amp = spot_data['mx'] - spot_data['mn']
        v_spreed = amp / 8
        folga = v_spreed / 2 
        
        max_original, min_original = eixo_dol + (amp * 0.75), eixo_dol - (amp * 0.25)
        dolar_medio = ((max_original + min_original) / 2) - v_spreed
        elastico_calculado = abs(eixo_dol - dolar_medio)
        if elastico_calculado == 0: elastico_calculado = 1.0
        
        media_pura_barra = (spot_data['mx'] + spot_data['mn']) / 2
        dist_base_barra = abs(eixo_dol - media_pura_barra) + folga
        
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = 0, 0
        seta_txt, seta_cor, piscando = "", "#000000", False
        
        if dist_base_barra > 0:
            # O AXIS EWZ virou div_spreed. Se for 1, a barra enche com 1 elástico.
            calculo_pct = (abs(diff) / (dist_base_barra * div_spreed)) * 100
            if diff < 0: p_v = min(100, calculo_pct)
            else: p_r = min(100, calculo_pct)
        
        if p_v >= 100: seta_txt, seta_cor, piscando = "▲ REGIÃO DE COMPRA", "#00ff88", True
        elif p_r >= 100: seta_txt, seta_cor, piscando = "▼ REGIÃO DE VENDA", "#ff4d4d", True

        v_spot_pct = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        
        return {
            "vivo": eixo_dol * (1 + v_spot_pct), 
            "medio": dolar_medio, 
            "max_fut_5": eixo_dol + (elastico_calculado * 10),
            "max_fut_4": eixo_dol + (elastico_calculado * 8),
            "max_fut_3": eixo_dol + (elastico_calculado * 6),
            "max_fut_2": eixo_dol + (elastico_calculado * 4),
            "max_fut_1": eixo_dol + (elastico_calculado * 2),
            "min_fut_1": eixo_dol - (elastico_calculado * 2),
            "min_fut_2": eixo_dol - (elastico_calculado * 4),
            "min_fut_3": eixo_dol - (elastico_calculado * 6),
            "min_fut_4": eixo_dol - (elastico_calculado * 8),
            "min_fut_5": eixo_dol - (elastico_calculado * 10),
            "v_spot": v_spot_pct * 100, 
            "spreed": v_spreed, "p_v": p_v, "p_r": p_r, 
            "seta": seta_txt, "seta_cor": seta_cor, "piscando": piscando, 
            "max_grade": max_original, "min_grade": min_original
        }
    except: return None

# --- UI E LOOP ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    # NOVO NOME CONFORME SOLICITADO
    input_div_val = st.number_input("DIVISOR SPREED:", value=st.session_state.div_spreed_mem, format="%.1f", step=0.5)
    input_dol_val = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol_mem, format="%.2f")
    
    if st.button("SALVAR CONFIGURAÇÕES"):
        st.session_state.div_spreed_mem, st.session_state.a_dol_mem = input_div_val, input_dol_val
        salvar_eixos(input_div_val, input_dol_val)
        st.success("Salvo!")
        time.sleep(0.5)
        st.rerun()

div_s, a_dol = st.session_state.div_spreed_mem, st.session_state.a_dol_mem
placeholder = st.empty()

while True:
    tz_sp = pytz.timezone('America/Sao_Paulo')
    spot_live = fetch("USDBRL=X")
    now = datetime.now()
    dt_br = now.astimezone(tz_sp).strftime("%H:%M:%S")
    data_hoje = now.astimezone(tz_sp).strftime("%d/%m/%Y")

    with placeholder.container():
        st.markdown(f'''<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1><div class="clock-row"><span class="clock-item">🇧🇷 BRASÍLIA: <span class="br-green">{dt_br}</span></span></div><div class="date-container">📅 {data_hoje}</div></div>''', unsafe_allow_html=True)

        if spot_live:
            res = calcular_k97_total(div_s, a_dol, spot_live)
            if res:
                c_main, c_side = st.columns([3.2, 0.8])
                with c_main:
                    st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                    # (Grade segue a mesma lógica de tabela do seu original)
                    st.write("---") # Exemplo simplificado para foco na lógica da barra
                with c_side:
                    st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                    st.markdown(f'''<div class="calc-panel">
                        <div class="calc-row txt-green"><span>MAX FUT 5</span> <span>{res['max_fut_5']:.2f}</span></div>
                        <div class="calc-row txt-yellow"><span>MAX FUT 4</span> <span>{res['max_fut_4']:.2f}</span></div>
                        <div class="calc-row txt-green"><span>MAX FUT 3</span> <span>{res['max_fut_3']:.2f}</span></div>
                        <div class="calc-row txt-yellow"><span>MAX FUT 2</span> <span>{res['max_fut_2']:.2f}</span></div>
                        <div class="calc-row txt-green"><span>MAX FUT 1</span> <span>{res['max_fut_1']:.2f}</span></div>
                        <div style="text-align:center; padding: 4px; color: #00f2ff; font-size: 10px; font-weight: bold; border-top:1px solid #444; border-bottom:1px solid #444;">AXIS: {a_dol:.2f}</div>
                        <div class="calc-row txt-green"><span>MIN FUT 1</span> <span>{res['min_fut_1']:.2f}</span></div>
                        <div class="calc-row txt-yellow"><span>MIN FUT 2</span> <span>{res['min_fut_2']:.2f}</span></div>
                        <div class="calc-row txt-green"><span>MIN FUT 3</span> <span>{res['min_fut_3']:.2f}</span></div>
                        <div class="calc-row txt-yellow"><span>MIN FUT 4</span> <span>{res['min_fut_4']:.2f}</span></div>
                        <div class="calc-row txt-green" style="border-bottom: none;"><span>MIN FUT 5</span> <span>{res['min_fut_5']:.2f}</span></div>
                    </div>''', unsafe_allow_html=True)
                    
                    st.markdown(f'''<div class="bar-wrapper-dual">
                        <div class="force-scale"><span>100%</span><span>50%</span><span>0%</span><span>50%</span><span>100%</span></div>
                        <div class="force-container-dual">
                            <div class="center-line"></div>
                            <div class="bar-side"><div class="fill-green" style="width: {res["p_v"]}%;"></div></div>
                            <div class="bar-side"><div class="fill-red" style="width: {res["p_r"]}%;"></div></div>
                        </div>
                        <div class="sinal-indicator {"blink" if res["piscando"] else ""}" style="color:{res["seta_cor"]};">{res["seta"]}</div>
                    </div>''', unsafe_allow_html=True)
        time.sleep(5)
