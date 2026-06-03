import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime
import pytz

# =============================================================================
# BLOCO 1: CSS E CONFIGURAÇÕES
# =============================================================================
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    [data-testid="column"] { display: flex; flex-direction: column; justify-content: flex-start; gap: 0px !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; position: relative; }
    .main-title { margin: 0px; line-height: 1.2; font-size: 28px; font-family: monospace; padding-bottom: 5px; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .clock-row { display: flex; justify-content: center; gap: 15px; padding: 2px 0; font-weight: bold; font-size: 11px; font-family: monospace; }
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 5px; text-transform: uppercase; font-size: 11px; }
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; margin-top: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; }
    .bar-wrapper-full { background: #0a141a; padding: 6px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; margin-top: 5px; }
    .thermometer-box { border: 1.5px solid #00f2ff; border-radius: 4px; padding: 8px; background: #0a141a; text-align: center; margin-top: 8px; font-family: monospace; }
    .force-container-dual { background: #111; height: 10px; width: 100%; border-radius: 2px; position: relative; display: flex; border: 1px solid #444; }
    .fill-green { background: #00ff88; height: 100%; }
    .fill-red { background: #ff4d4d; height: 100%; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# BLOCO 2: MEMÓRIA E PERSISTÊNCIA
# =============================================================================
def salvar_eixos(div_spreed):
    with open("config_axis.txt", "w") as f: f.write(f"{div_spreed}")

def carregar_eixos():
    if os.path.exists("config_axis.txt"):
        with open("config_axis.txt", "r") as f: return float(f.read().split(",")[0])
    return 8.0

div_spreed_salvo = carregar_eixos()
if 'div_spreed_mem' not in st.session_state: st.session_state.div_spreed_mem = div_spreed_salvo
if 'last_p' not in st.session_state: st.session_state.last_p = {}
if 'market_data' not in st.session_state: st.session_state.market_data = {}

# =============================================================================
# BLOCO 3: CAPTURA DE DADOS
# =============================================================================
def fetch(s):
    fallback = {"at": 0.0, "cl": 1.0, "op": 0.0, "mx": 0.0, "mn": 0.0}
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return st.session_state.market_data.get(s, fallback)
        m = 1000 if s == "USDBRL=X" else 1
        data = {"at": float(d['Close'].iloc[-1] * m), "cl": float(t.info.get('previousClose', d['Open'].iloc[0]) * m), "op": float(d['Open'].iloc[0] * m), "mx": float(d['High'].max() * m), "mn": float(d['Low'].min() * m)}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s, fallback)

# =============================================================================
# BLOCO 4: NÚCLEO MATEMÁTICO (K97)
# =============================================================================
def calcular_k97_total(spreed_do_dia, spot_data, ewz_data):
    # Cálculo simplificado para exibir o termômetro
    dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
    axis = dolar_medio + spreed_do_dia
    
    # Lógica do Termômetro
    vivo_val = spot_data['at']
    if vivo_val > axis:
        term_str = "FORÇA COMPRA"
        term_color = "#00ff88"
    else:
        term_str = "FORÇA VENDA"
        term_color = "#ff4d4d"
        
    return {
        "axis_central": axis, "vivo": vivo_val, "medio": dolar_medio,
        "p_v": 60, "p_r": 40, "term_str": term_str, "term_color": term_color,
        "max_fut_1": axis + 2, "max_fut_2": axis + 4, "min_fut_1": axis - 2, "min_fut_2": axis - 4
    }

# =============================================================================
# BLOCO 5: SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    div_s = st.number_input("FRP (PARA JUSTO):", value=st.session_state.div_spreed_mem, format="%.2f")
    if st.button("SALVAR"):
        st.session_state.div_spreed_mem = div_s
        salvar_eixos(div_s)
        st.rerun()

# =============================================================================
# BLOCO 6: INTERFACE FINAL
# =============================================================================
placeholder = st.empty()
while True:
    spot = fetch("USDBRL=X")
    ewz = fetch("EWZ")
    res = calcular_k97_total(st.session_state.div_spreed_mem, spot, ewz)
    
    with placeholder.container():
        c1, c2 = st.columns([2.8, 1.2])
        with c1:
            st.markdown('<div class="section-title">GRADE PRINCIPAL</div>', unsafe_allow_html=True)
            st.markdown(f"DOLFUT: {res['axis_central']:.2f}")
            st.markdown(f'''<div class="bar-wrapper-full">
                <div class="force-container-dual">
                    <div class="fill-green" style="width: {res["p_v"]}%;"></div>
                    <div class="fill-red" style="width: {res["p_r"]}%;"></div>
                </div>
            </div>''', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
            st.markdown('<div class="calc-panel">...NÍVEIS...</div>', unsafe_allow_html=True)
            
            # TERMÔMETRO K97
            st.markdown(f'''
            <div class="thermometer-box">
                <div style="color: #00f2ff; font-size: 10px; font-weight: bold;">🌡️ TERMÔMETRO K97</div>
                <div style="color: {res['term_color']}; font-size: 14px; font-weight: bold; margin-top: 5px;">{res['term_str']}</div>
            </div>
            ''', unsafe_allow_html=True)
    time.sleep(5)
