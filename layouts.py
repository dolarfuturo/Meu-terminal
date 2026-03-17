import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR", initial_sidebar_state="collapsed")

# --- CSS: ESTILIZAÇÃO FINAL E OCULTAÇÃO DE STATUS ---
st.markdown("""
<style>
    /* 1. ESCONDE A BARRA DE ATUALIZAÇÃO E ELEMENTOS DE INTERFACE */
    div[data-testid="stStatusWidget"] { display: none !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* 2. ESTILO DO TERMINAL */
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    
    /* Header BAIR */
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    
    /* Relógios */
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; }
    
    /* Painéis Laterais */
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    .monitor-bar { background: #0a141a; border: 2.2px solid #ffffff; padding: 6px; text-align: center; color: #00f2ff; font-weight: bold; font-size: 14px; border-radius: 4px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        ref = t.info.get('previousClose')
        if d.empty: return {"at": 0.0, "cl": ref or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {"at": d['Close'].iloc[-1], "cl": ref or d['Open'].iloc[0], "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97_total(eixo_ewz, p_ewz_at, max_e, min_e, eixo_dol):
    if p_ewz_at <= 0: return None
    try:
        v_at = ((eixo_ewz / p_ewz_at) - 1) * 100 / 1.5
        v_pos = ((eixo_ewz / min_e) - 1) * 100 / 1.5 if min_e > 0 else 0
        v_neg = ((eixo_ewz / max_e) - 1) * 100 / 1.5 if max_e > 0 else 0
        mx_d, mn_d = eixo_dol * (1 + (v_pos / 100)), eixo_dol * (1 + (v_neg / 100))
        return {
            "vivo": eixo_dol * (1 + (v_at / 100)), "max": mx_d, "min": mn_d,
            "p75_up": (eixo_dol + (mx_d - eixo_dol)*0.75), "p50_up": (eixo_dol + mx_d) / 2,
            "p25_up": (eixo_dol + (mx_d - eixo_dol)*0.25), "p75_down": (eixo_dol + (mn_d - eixo_dol)*0.75),
            "p50_down": (eixo_dol + mn_d) / 2, "p25_down": (eixo_dol + (mn_d - eixo_dol)*0.25)
        }
    except: return None

# --- PAINEL ADM ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_ewz = st.number_input("AXIS EWZ:", value=36.42, format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")

# --- HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""
<div class="header-bair">
    <div class="title-box"><span class="bair-text">BAIR</span><span style="color:#fff; font-size:46px; font-weight:950;">-</span><span class="terminal-text">TERMINAL DOLAR</span></div>
    <div style="display: flex; gap: 10px;">
        <div class="clock-box"><span class="clock-label">BSB</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">NY</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">LDN</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

placeholder = st.empty()

while True:
    with placeholder.container():
        ewz = fetch("EWZ")
        res = calcular_k97_total(a_ewz, ewz['at'], ewz['mx'], ewz['mn'], a_dol)
        
        c_main, c_side = st.columns([3, 1])
        with c_main:
            st.markdown('<div class="monitor-bar">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
            html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
            
            ativos = {"DOLFUT": "BZ=F", "SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "XAU/USD": "GC=F"}
            for lbl, sym in ativos.items():
                d = fetch(sym)
                price = res['vivo'] if lbl == "DOLFUT" and res else d['at']
                close = a_dol if lbl == "DOLFUT" else d['cl']
                var = ((price / close) - 1) * 100 if close > 0 else 0
                color = "#00ff00" if var >= 0 else "#ff4d4d"
                fmt = ".4f" if "USD" in lbl or lbl == "SPOT" else ".2f"
                html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{price:{fmt}}</td><td>{close:{fmt}}</td><td>{d['op']:{fmt}}</td><td>{d['mx']:{fmt}}</td><td>{d['mn']:{fmt}}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
            st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

        with c_side:
            st.markdown('<div class="monitor-bar">PROJEÇÕES</div>', unsafe_allow_html=True)
            if res:
                st.markdown(f"""
                <div class="calc-panel">
                    <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
                    <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
                    <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {a_dol:.2f}</div>
                    <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
                    <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
                </div>
                <div class="calc-panel">
                    <div class="calc-row" style="border-bottom:none;"><span>DOLFUT VIVO</span> <span style="color:#00f2ff; font-size:16px;">{res['vivo']:.2f}</span></div>
                </div>
                """, unsafe_allow_html=True)

    time.sleep(5)
    st.rerun()
