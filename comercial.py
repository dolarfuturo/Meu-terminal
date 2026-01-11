import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide")

# Conexão Nuvem
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_valores():
    try:
        df = conn.read(worksheet="Sheet1", ttl="2s")
        return float(df.iloc[0, 0]), float(df.iloc[0, 1])
    except:
        return 5.4000, 5.3700

# 2. ESTILO CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700;800&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 850px !important; margin: auto; }
    
    /* BOTAO ADMIN DISCRETO */
    .stButton>button {
        background-color: transparent !important;
        color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 5px; font-size: 10px !important;
    }
    .stButton>button:hover { color: #00FF80 !important; border-color: #00FF80 !important; }

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
    @keyframes pulse-green { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

def round_to_half_tick(price):
    return round(price * 2000) / 2000

# 3. PAINEL DE CONTROLE (BOTÃO VISÍVEL NO TOPO)
col_btn, col_empty = st.columns([1, 4])
with col_btn:
    if st.button("ADMIN ACCESS"):
        st.session_state['show_admin'] = not st.session_state.get('show_admin', False)

if st.session_state.get('show_admin'):
    with st.expander("CONFIGURAÇÕES DO TERMINAL", expanded=True):
        pwd = st.text_input("PASSWORD", type="password")
        if pwd == "1234":
            v_aj, v_ref = carregar_valores()
            n_aj = st.number_input("AJUSTE ANTERIOR", value=v_aj, format="%.4f")
            n_ref = st.number_input("REFERENCIAL", value=v_ref, format="%.4f")
            if st.button("SALVAR E ATUALIZAR"):
                df_up = pd.DataFrame({"ajuste": [n_aj], "referencial": [n_ref]})
                conn.update(worksheet="Sheet1", data=df_up)
                st.success("DADOS ATUALIZADOS!")
                time.sleep(1)
                st.rerun()

def get_market_data():
    try:
        tkrs = ["BRL=X", "DX-Y.NYB", "EWZ", "EURUSD=X"]
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
    aj_m, ref_m = carregar_valores()
    m, spread = get_market_data()
    
    if m:
        spot = m["BRL=X"]["p"]
        paridade = aj_m * (1 + (spread/100))
        equi = round_to_half_tick(ref_m + 0.0220)
        f_max, f_jus, f_min = [round_to_half_tick(spot + x) for x in [0.0420, 0.0310, 0.0220]]
        t_max, t_jus, t_min = [round_to_half_tick(ref_m + x) for x in [0.0420, 0.0310, 0.0220]]

        with placeholder.container():
            st.markdown('<div class="terminal-header">TERMINAL <span style="color:#FFF; font-weight:800;">DOLAR</span></div>', unsafe_allow_html=True)
            
            # Linhas de Dados
            st.markdown(f'<div class="data-row"><div class="data-label">PARIDADE GLOBAL</div><div class="data-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="data-row"><div class="data-label">EQUILIBRIO</div><div class="data-value c-equi">{equi:.4f}</div></div>', unsafe_allow_html=True)
            
            # Preço Justo
            html_justo = f'''
            <div class="data-row">
                <div class="data-label">PREÇO JUSTO</div>
                <div class="sub-grid">
                    <div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{f_min:.4f}</span></div>
                    <div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{f_jus:.4f}</span></div>
                    <div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{f_max:.4f}</span></div>
                </div>
            </div>
            '''
            st.markdown(html_justo, unsafe_allow_html=True)

            # Referencial
            html_ref = f'''
            <div class="data-row">
                <div class="data-label">REFERENCIAL INSTITUCIONAL</div>
                <div class="sub-grid">
                    <div class="sub-item"><span class="sub-label">MINIMA</span><span class="sub-val c-min">{t_min:.4f}</span></div>
                    <div class="sub-item"><span class="sub-label">JUSTO</span><span class="sub-val c-jus">{t_jus:.4f}</span></div>
                    <div class="sub-item"><span class="sub-label">MAXIMA</span><span class="sub-val c-max">{t_max:.4f}</span></div>
                </div>
            </div>
            '''
            st.markdown(html_ref, unsafe_allow_html=True)

            # Rodapé
            agora = datetime.now().strftime("%H:%M:%S")
            st.markdown(f'<div class="footer-bar"><div><span class="pulse">●</span> LIVE</div><div class="ticker-wrap"><div class="ticker">DXY: {m["DX-Y.NYB"]["p"]:.2f} | EWZ: {m["EWZ"]["p"]:.2f} | SPREAD: {spread:+.2f}%</div></div><div style="color:#444;">{agora}</div></div>', unsafe_allow_html=True)

    time.sleep(2)
