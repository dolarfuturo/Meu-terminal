import streamlit as st
import requests
import time
import os
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO DA CHAVE ---
API_KEY_TWELVE = "7805835d10ff47dfb88596a0ee89edc6"

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="K97 - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- MOTOR DE DADOS ---
def fetch_twelve(symbol_original):
    symbols_map = {
        "USDBRL=X": "USD/BRL", "EWZ": "EWZ", "DX-Y.NYB": "DXY", 
        "GBPUSD=X": "GBP/USD", "JPYUSD=X": "JPY/USD", "EURUSD=X": "EUR/USD", 
        "GC=F": "XAU/USD", "BZ=F": "LCO/USD"
    }
    symbol = symbols_map.get(symbol_original, symbol_original)
    try:
        url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={API_KEY_TWELVE}"
        d = requests.get(url).json()
        if "price" not in d: return st.session_state.market_data.get(symbol_original)
        m = 1000 if symbol == "USD/BRL" else 1
        data = {
            "at": float(d['price']) * m, "cl": float(d['previous_close']) * m,
            "op": float(d['open']) * m, "mx": float(d['high']) * m, "mn": float(d['low']) * m
        }
        st.session_state.market_data[symbol_original] = data
        return data
    except: return st.session_state.market_data.get(symbol_original)

# --- PERSISTÊNCIA ---
def salvar_eixos(div_spreed, dol):
    with open("config_axis.txt", "w") as f: f.write(f"{div_spreed},{dol}")

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

# --- CSS COMPLETO ---
st.markdown("""
<style>
    .block-container { padding-top: 3.5rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; position: relative; }
    .main-title { margin: 0px; font-size: 28px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .clock-row { display: flex; justify-content: center; gap: 15px; font-size: 11px; font-family: monospace; font-weight: bold;}
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 5px; font-size: 11px; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; font-size: 10px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 12px; }
    .price-col { font-weight: bold; color: #ffffff !important; }
    .f-up { background-color: #00ff00aa !important; }
    .f-dn { background-color: #ff0000aa !important; }
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-top: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; }
    .bar-wrapper-full { background: #0a141a; padding: 6px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; margin-top: 5px; }
    .force-container-dual { background: #111; height: 10px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .txt-green { color: #00ff88 !important; } .txt-yellow { color: #ffff00 !important; } .txt-red { color: #ff4d4d !important; }
</style>
""", unsafe_allow_html=True)

# --- CÁLCULOS ---
def calcular_k97_total(div_spreed, p_ewz_atual, eixo_dol, spot_data):
    try:
        if not spot_data or p_ewz_atual == 0: return None
        amp = spot_data['mx'] - spot_data['mn']
        v_spreed = amp / 8
        folga = v_spreed / 2 
        max_original, min_original = eixo_dol + (amp * 0.75), eixo_dol - (amp * 0.25)
        dolar_medio = ((max_original + min_original) / 2) - v_spreed
        elastico = abs(eixo_dol - dolar_medio) if abs(eixo_dol - dolar_medio) != 0 else 1.0
        media_pura = (spot_data['mx'] + spot_data['mn']) / 2
        alvo_low = spot_data['mn'] + (eixo_dol - (eixo_dol - media_pura - folga))
        alvo_high = spot_data['mx'] + ((eixo_dol - media_pura + folga))
        
        diff = spot_data['at'] - eixo_dol
        dist_base = abs(eixo_dol - media_pura) + folga
        p_v, p_r = 0, 0
        if dist_base > 0:
            calc = (abs(diff) / (dist_base * div_spreed)) * 100
            if diff < 0: p_v = min(100, calc)
            else: p_r = min(100, calc)
            
        v_spot = ((spot_data['at'] / spot_data['cl']) - 1)
        ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
        v_ewz = ((p_ewz_atual / ewz_ref) - 1)
        v_final = (v_spot * 0.6) - (v_ewz * 0.4)
        fraja = eixo_dol * (1 + (v_final / 2))
        
        return {
            "vivo": (eixo_dol + fraja) / 2, "dolfut_calc": eixo_dol * (1 + v_final), "fraja": fraja, "medio": dolar_medio, 
            "max_fut_5": eixo_dol + (elastico * 10), "max_fut_4": eixo_dol + (elastico * 8), "max_fut_3": eixo_dol + (elastico * 6), "max_fut_2": eixo_dol + (elastico * 4), "max_fut_1": eixo_dol + (elastico * 2),
            "min_fut_1": eixo_dol - (elastico * 2), "min_fut_2": eixo_dol - (elastico * 4), "min_fut_3": eixo_dol - (elastico * 6), "min_fut_4": eixo_dol - (elastico * 8), "min_fut_5": eixo_dol - (elastico * 10),
            "v_v": v_final * 100, "spreed": v_spreed, "p_v": p_v, "p_r": p_r, "max_grade": max_original, "min_grade": min_original, "alvo_low": alvo_low, "alvo_high": alvo_high
        }
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    i_div = st.number_input("DIVISOR SPREED:", value=st.session_state.div_spreed_mem)
    i_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol_mem)
    if st.button("SALVAR"):
        st.session_state.div_spreed_mem, st.session_state.a_dol_mem = i_div, i_dol
        salvar_eixos(i_div, i_dol); st.rerun()

# --- LOOP ---
placeholder = st.empty()
while True:
    tz_sp = pytz.timezone('America/Sao_Paulo')
    spot_live = fetch_twelve("USDBRL=X")
    ewz_live = fetch_twelve("EWZ")
    now = datetime.now()
    
    with placeholder.container():
        st.markdown(f'<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - K97</span></h1><div class="clock-row"><span style="color:#00ff00">BR: {now.astimezone(tz_sp).strftime("%H:%M:%S")}</span></div></div>', unsafe_allow_html=True)
        res = calcular_k97_total(st.session_state.div_spreed_mem, ewz_live['at'] if ewz_live else 0, st.session_state.a_dol_mem, spot_live)
        if res:
            c1, c2 = st.columns([2.8, 1.2])
            with c1:
                st.markdown('<div class="section-title">MONITORAMENTO DA GRADE</div>', unsafe_allow_html=True)
                html = '<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>'
                
                # Linha DOLFUT
                html += f"<tr><td style='text-align:left; font-weight:bold;'>DOLFUT</td><td class='price-col'>{(res['dolfut_calc']/1000):.4f}</td><td>{(st.session_state.a_dol_mem/1000):.4f}</td><td>{(st.session_state.a_dol_mem/1000):.4f}</td><td>{(res['max_grade']/1000):.4f}</td><td>{(res['min_grade']/1000):.4f}</td><td style='color:{("#00ff00" if res["v_v"] >= 0 else "#ff4d4d")}'>{res['v_v']:+.2f}%</td></tr>"
                
                ticker_items = [f"DOLFUT: {res['v_v']:+.2f}%"]
                outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "OURO": "GC=F", "BRENT": "BZ=F"}
                for lbl, sym in outros.items():
                    d = fetch_twelve(sym)
                    if d:
                        m = 1000 if "DOL" in lbl else 1
                        var = ((d['at'] / d['cl']) - 1) * 100
                        html += f"<tr><td style='text-align:left; font-weight:bold;'>{lbl}</td><td class='price-col'>{d['at']/m:.4f}</td><td>{d['cl']/m:.4f}</td><td>{d['op']/m:.4f}</td><td>{d['mx']/m:.4f}</td><td>{d['mn']/m:.4f}</td><td style='color:{("#00ff00" if var >= 0 else "#ff4d4d")}'>{var:+.2f}%</td></tr>"
                        ticker_items.append(f"{lbl}: {var:+.2f}%")
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
                st.markdown(f'<div class="bar-wrapper-full"><div class="force-container-dual"><div class="bar-side"><div class="fill-green" style="width:{res["p_v"]}%;"></div></div><div class="bar-side"><div class="fill-red" style="width:{res["p_r"]}%;"></div></div></div><div style="display:flex; justify-content:space-between; font-size:10px; color:#AAA;"><span>LOW: {res["alvo_low"]:.2f}</span><span>HIGH: {res["alvo_high"]:.2f}</span></div></div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                calc_html = '<div class="calc-panel">'
                for i in range(5, 0, -1): calc_html += f'<div class="calc-row txt-red"><span>MAX FUT {i}</span><span>{res[f"max_fut_{i}"]:.2f}</span></div>'
                calc_html += f'<div style="text-align:center; color:#00f2ff; font-size:10px; padding:4px;">AXIS: {st.session_state.a_dol_mem:.2f}</div>'
                for i in range(1, 6): calc_html += f'<div class="calc-row txt-green"><span>MIN FUT {i}</span><span>{res[f"min_fut_{i}"]:.2f}</span></div>'
                st.markdown(calc_html + '</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="calc-panel"><div class="calc-row"><span>DOLB3</span><span style="color:#00f2ff;">{res["vivo"]:.2f}</span></div><div class="calc-row"><span>JUSTO</span><span>{res["fraja"]:.2f}</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)}</div></div>', unsafe_allow_html=True)
    time.sleep(12)
