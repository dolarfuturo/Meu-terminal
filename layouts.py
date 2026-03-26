import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- CSS: DESIGN PADRÃO TERMINAL CRYPTO (NOME E RELÓGIOS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=swap');

    * { font-family: 'JetBrains Mono', monospace !important; }
    .stApp { background-color: #050a0e !important; }

    /* CABEÇALHO CENTRALIZADO (IGUAL AO CRYPTO) */
    .header-container {
        text-align: center;
        padding-top: 5px;
        background-color: #050a0e;
    }
    .main-title { font-size: 42px; font-weight: 900; margin-bottom: 0px; letter-spacing: -1px; }
    .bair-blue { color: #00f2ff; }
    .sep-white { color: #ffffff; }
    .terminal-gold { color: #ffd700; }

    /* RELÓGIOS COM BANDEIRAS (IGUAL AO CRYPTO) */
    .clock-row {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin: 10px 0;
        font-size: 16px;
        font-weight: bold;
    }
    .clock-item { display: flex; align-items: center; gap: 8px; color: #ffffff; }
    .time-val { color: #ffffff; }
    .br-time { color: #00ff00; }

    /* LINHA AMARELA FINA */
    .yellow-divider {
        border-bottom: 1.5px solid #ffd700;
        width: 100%;
        margin-bottom: 15px;
    }

    /* PRESERVAÇÃO DOS ELEMENTOS DO DOLLAR (TABELAS E GRIDS) */
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 6px; background: #0a141a; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-size: 14px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }

    /* BARRA DE FORÇA */
    .bar-wrapper-dual { background: #0a141a; padding: 12px 10px 6px 10px; border: 2.5px solid #ffffff; border-radius: 8px; text-align: center; position: relative; }
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
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
        return {"at": d['Close'].iloc[-1] * m, "cl": (ref_close or d['Open'].iloc[0]) * m, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- SIDEBAR ADM (AS DUAS SETAS ORIGINAIS) ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_ewz = st.number_input("AXIS EWZ:", value=37.85, format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
    st.button("SALVAR")

placeholder = st.empty()

while True:
    tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
    spot_live = fetch("USDBRL=X")
    
    # Valores de exemplo para os cálculos (res)
    res = {"v_v": -0.38, "max_fut": 5226.60, "min_fut": 5225.80, "p75_up": 5226.50, "p25_up": 5246.10, "p25_down": 5245.90, "p75_down": 5225.90, "vivo": 5226.60, "spreed": 0.20, "medio": 5226.10, "fraja": 5236.10, "var_axis": -0.37, "p_v": 30, "p_r": 10, "seta": "", "seta_cor": "#000"}

    with placeholder.container():
        # --- CABEÇALHO PADRONIZADO CENTRALIZADO (ESTILO CRYPTO) ---
        st.markdown(f"""
            <div class="header-container">
                <div class="main-title">
                    <span class="bair-blue">BAIR</span> 
                    <span class="sep-white">-</span> 
                    <span class="terminal-gold">TERMINAL DOLLAR</span>
                </div>
                <div class="clock-row">
                    <div class="clock-item">
                        <span>🇧🇷</span> <span>BRASÍLIA:</span> 
                        <span class="time-val br-time">{datetime.now(tz_sp).strftime('%H:%M:%S')}</span>
                    </div>
                    <div class="clock-item">
                        <span>🇺🇸</span> <span>NEW YORK:</span> 
                        <span class="time-val">{datetime.now(tz_ny).strftime('%H:%M:%S')}</span>
                    </div>
                    <div class="clock-item">
                        <span>🇬🇧</span> <span>LONDON:</span> 
                        <span class="time-val">{datetime.now(tz_ld).strftime('%H:%M:%S')}</span>
                    </div>
                </div>
                <div class="yellow-divider"></div>
            </div>
        """, unsafe_allow_html=True)

        # --- CORPO DO TERMINAL DOLLAR (MANTIDO IGUAL) ---
        c_main, c_side = st.columns([3, 1])
        with c_main:
            # Tabela de Ativos
            html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
            html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>5.2262</td><td>5.2460</td><td>5.2460</td><td>5.2266</td><td>5.2258</td><td style='color:#ff4d4d;'>-0.38%</td></tr>"
            st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)
            
        with c_side:
            # Painéis Laterais
            st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MAX FUT</span> <span>{res['max_fut']:.2f}</span></div><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {a_dol:.2f}</div><div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MIN FUT</span> <span>{res['min_fut']:.2f}</span></div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="calc-panel"><div style="padding: 10px 8px; border-bottom: 1px solid #444;"><div style="display: flex; justify-content: space-between; align-items: center;"><span style="color:#ffffff; font-weight: bold;">DOLFUT</span> <span style="color:#00f2ff; font-size: 18px; font-weight: 950;">5226.60</span></div></div></div>""", unsafe_allow_html=True)

    time.sleep(2)
