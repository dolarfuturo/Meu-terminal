import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração de Layout
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR", initial_sidebar_state="collapsed")

# --- CSS: VOLTANDO AO VISUAL QUE VOCÊ GOSTA (CORRIGIDO) ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    [data-testid="stSidebar"] { background-color: #0a141a !important; border-right: 1px solid #ffffff; }
    .block-container { padding: 1rem !important; max-width: 100% !important; }

    /* Estilo das Tabelas do seu Print */
    .main-grid { border: 2px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 15px; }
    
    .asset-name { font-size: 16px; color: #fff; text-align: left; font-weight: bold; padding-left: 10px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    
    /* Header */
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 15px; }
    .bair-text { font-size: 42px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; } 
    .terminal-text { font-size: 42px; color: #d4a017; font-weight: 950; font-family: 'monospace'; }
    
    /* Relógios */
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 12px; border-radius: 4px; background: #0a141a; min-width: 90px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 18px; font-weight: bold; }
    
    /* Painéis de Projeção */
    .calc-panel { border: 2px solid #ffffff; border-radius: 8px; padding: 10px; background: #0a141a; font-family: monospace; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    .monitor-bar { background: #0a141a; border: 2px solid #ffffff; padding: 5px; text-align: center; color: #00f2ff; font-weight: bold; margin-bottom: 10px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS SEGURO ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        ref = t.info.get('previousClose')
        if d.empty:
            return {"at": 0.0, "cl": ref or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {
            "at": d['Close'].iloc[-1], 
            "cl": ref or d['Open'].iloc[0], 
            "op": d['Open'].iloc[0], 
            "mx": d['High'].max(), 
            "mn": d['Low'].min()
        }
    except Exception:
        return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97(eixo_ewz, p_ewz, mx_ewz, mn_ewz, eixo_dol):
    if p_ewz <= 0: return None
    try:
        v_at = ((eixo_ewz / p_ewz) - 1) * 100 / 1.5
        v_pos = ((eixo_ewz / mn_ewz) - 1) * 100 / 1.5 if mn_ewz > 0 else 0
        v_neg = ((eixo_ewz / mx_ewz) - 1) * 100 / 1.5 if mx_ewz > 0 else 0
        max_d = eixo_dol * (1 + (v_pos / 100))
        min_d = eixo_dol * (1 + (v_neg / 100))
        return {
            "vivo": eixo_dol * (1 + (v_at / 100)),
            "max": max_d, "min": min_d,
            "p50_up": (eixo_dol + max_d) / 2,
            "p50_down": (eixo_dol + min_d) / 2
        }
    except: return None

# --- SIDEBAR ADM ---
with st.sidebar:
    st.header("⚙️ PAINEL ADM")
    a_ewz = st.number_input("AXIS EWZ", value=36.42, format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT", value=5274.0, format="%.1f")

# --- HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""
<div class="header-bair">
    <div><span class="bair-text">BAIR</span><span style="color:#fff;"> - </span><span class="terminal-text">TERMINAL DOLAR</span></div>
    <div style="display: flex; gap: 10px;">
        <div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- CORPO DO TERMINAL ---
placeholder = st.empty()

while True:
    with placeholder.container():
        ewz_data = fetch("EWZ")
        res = calcular_k97(a_ewz, ewz_data['at'], ewz_data['mx'], ewz_data['mn'], a_dol)
        
        c_main, c_side = st.columns([3, 1])
        
        with c_main:
            st.markdown('<div class="monitor-bar">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
            html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
            
            ativos = {"DOLFUT": "BZ=F", "SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F"}
            
            for lbl, sym in ativos.items():
                d = fetch(sym)
                # Se for DOLFUT, usa o cálculo do eixo
                price = res['vivo'] if lbl == "DOLFUT" and res else d['at']
                close = a_dol if lbl == "DOLFUT" else d['cl']
                var = ((price / close) - 1) * 100 if close > 0 else 0
                
                color = "#00ff00" if var >= 0 else "#ff4d4d"
                fmt = ".4f" if "USD" in lbl or lbl == "SPOT" else ".2f"
                
                html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{price:{fmt}}</td><td>{close:{fmt}}</td><td>{d['op']:{fmt}}</td><td>{d['mx']:{fmt}}</td><td>{d['mn']:{fmt}}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
            
            st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

        with c_side:
            st.markdown('<div class="monitor-bar">CÁLCULOS DE PROJEÇÕES</div>', unsafe_allow_html=True)
            if res:
                st.markdown(f"""
                <div class="calc-panel">
                    <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span><span>{res['max']:.2f}</span></div>
                    <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span><span>{res['p50_up']:.2f}</span></div>
                    <div style="text-align:center; padding:10px; color:#00f2ff; font-weight:bold; font-size:18px;">AXIS: {a_dol:.2f}</div>
                    <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span><span>{res['p50_down']:.2f}</span></div>
                    <div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MÍNIMA</span><span>{res['min']:.2f}</span></div>
                </div>
                <div style="margin-top:10px;" class="calc-panel">
                    <div class="calc-row"><span>DOLFUT</span><span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Aguardando dados...")

    time.sleep(5)
    st.rerun()
