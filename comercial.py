import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAÇÃO DO TERMINAL
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

# Conexão com a nuvem (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_valores_mestre():
    try:
        df = conn.read(worksheet="Sheet1", ttl="2s")
        return float(df.iloc[0, 0]), float(df.iloc[0, 1])
    except:
        return 5.4000, 5.3700

# 2. ESTILO CSS (COM BOTÃO DISCRETO)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700;800&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 0.5rem !important; max-width: 850px !important; margin: auto; padding-bottom: 80px; }
    
    /* BOTÃO DE ACESSO TRANSLÚCIDO */
    .stButton>button {
        background-color: transparent !important;
        color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.02) !important;
        position: fixed; top: 5px; left: 5px; z-index: 10001;
        font-size: 10px !important;
    }
    .stButton>button:hover { color: rgba(255, 255, 255, 0.5) !important; border-color: rgba(255, 255, 255, 0.2) !important; }

    .terminal-header { text-align: center; font-size: 14px; letter-spacing: 8px; color: #444; border-bottom: 1px solid #111; padding-bottom: 10px; margin-bottom: 20px; }
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 0; border-bottom: 1px solid #111; }
    .data-label { font-size: 11px; color: #FFFFFF; font-weight: 700; letter-spacing: 2px; width: 35%; }
    .data-value { font-size: 32px; font-weight: 700; width: 65%; text-align: right; }
    .sub-grid { display: flex; gap: 25px; justify-content: flex-end; width: 65%; }
    .sub-item { text-align: right; min-width: 105px; }
    .sub-label { font-size: 9px; color: #444; display: block; margin-bottom: 4px; font-weight: 700; }
    .sub-val { font-size: 24px; font-weight: 700; }
    .c-pari { color: #FFB900; } .c-equi { color: #00FFFF; } .c-max { color: #00FF80; } .c-min { color: #FF4B4B; } .c-jus { color: #0080FF; }
    .footer-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 40px; background: #080808; border-top: 1px solid #222; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; font-size: 11px; z-index: 9999; }
    .ticker-wrap { flex-grow: 1; overflow: hidden; white-space: nowrap; margin: 0 30px; }
    .ticker { display: inline-block; animation: marquee 35s linear infinite; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-250%); } }
    .up { color: #00FF80; } .down { color: #FF4B4B; }
    .pulse { animation: pulse-green 2s infinite; color: #00FF80; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def round_to_half_tick(price):
    return round(price * 2000) / 2000

# 3. PAINEL DE CONTROLE ACIONÁVEL
v_aj_at, v_ref_at = carregar_valores_mestre()

# Botão quase invisível no topo
if st.button("SET"):
    with st.expander("SALA DE COMANDO", expanded=True):
        key = st.text_input("PASSWORD", type="password")
        if key == "1234": # Altere sua senha aqui
            n_aj = st.number_input("AJUSTE ANTERIOR", value=v_aj_at, format="%.4f")
            n_ref = st.number_input("REFERENCIAL", value=v_ref_at, format="%.4f")
            if st.button("CONFIRMAR ATUALIZAÇÃO"):
                df_up = pd.DataFrame({"ajuste": [n_aj], "referencial": [n_ref]})
                conn.update(worksheet="Sheet1", data=df_up)
                st.success("DADOS ENVIADOS!")
                time.sleep(1)
                st.rerun()

def get_market_data():
    try:
        tkrs = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X", "USDJPY=X"]
        data = {}
        for t in tkrs:
            tk = yf.Ticker(t)
            inf = tk.fast_info
            p = inf['last_price']
            prev = inf['previous_close']
            data[t] = {"p": p, "v": ((p - prev) / prev) * 100}
        spread = data["DX-Y.NYB"]["v"] - data["EWZ"]["v"]
        return data, spread
    except: return None, 0.0

placeholder = st.empty()

while True:
    ajuste_mestre, ref_mestre = carregar_valores_mestre()
    m, spread = get_market_data()
    
    if m:
        spot = m["BRL=X"]["p"]
        paridade = ajuste_mestre * (1 + (spread/100))
        equi = round_to_half_tick(ref_mestre + 0.0220)
        f_max, f_jus, f_min = [round_to_half_tick(spot + x) for x in [0.0420, 0.0310, 0.0220]]
        t_max, t_jus, t_min = [round_to_half_tick(ref_mestre + x) for x in [0.0420, 0.0310, 0.0220]]

        with placeholder.container():
            st.markdown('<div class="terminal-header">TERMINAL <span style="color:#FFF; font-weight:800;">DOLAR</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=
