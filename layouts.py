import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração de Layout - Wide para usar a largura total
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR", initial_sidebar_state="collapsed")

# --- CSS: ESTILO SLIM COM SIDEBAR PRESERVADA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    
    /* Ajuste da Sidebar (Painel ADM) */
    [data-testid="stSidebar"] { background-color: #0a141a !important; border-right: 1px solid #444; }
    
    /* Redução de margens para caber no frame do site */
    .block-container {
        padding: 0.5rem 0.8rem !important;
        max-width: 100% !important;
    }

    /* Grid e Tabela Slim */
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #444; padding: 5px; text-align: center; font-size: 11px; }
    .terminal-table td { border: 1px solid #333; padding: 5px 8px; text-align: center; font-size: 13px; }
    
    .asset-name { font-size: 13px; color: #fff; text-align: left; font-weight: bold; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    
    /* Header Compacto */
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 2px 0; border-bottom: 2px solid #ffffff; margin-bottom: 8px; }
    .bair-text { font-size: 28px; color: #00f2ff; font-weight: 900; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 28px; color: #d4a017; font-weight: 900; font-family: 'monospace'; letter-spacing: -1px; }
    
    /* Relógios menores */
    .clock-box { text-align: center; border: 1px solid #ffffff; padding: 2px 6px; border-radius: 3px; background: #0a141a; min-width: 70px; }
    .clock-label { font-size: 8px; color: #d4a017; display: block; }
    .clock-time { color: #fff; font-size: 13px; font-weight: bold; }
    
    /* Painéis de Projeção Slim */
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 5px; border-bottom: 1px solid #333; font-size: 11px; font-weight: bold; }
    .monitor-bar { background: #0a141a; border: 1px solid #ffffff; padding: 2px; text-align: center; color: #00f2ff; font-weight: bold; font-size: 11px; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
@st.cache_data(ttl=5)
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        ref = t.info.get('previousClose')
        if d.empty: return {"at": 0.0, "cl": ref or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {"at": d['Close'].iloc[-1], "cl": ref or d['Open'].iloc[0], "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- LÓGICA DE CÁLCULO ---
def calcular_k97(eixo_ewz, p_ewz, mx_ewz, mn_ewz, eixo_dol):
    if p_ewz == 0: return None
    v_at = ((eixo_ewz / p_ewz) - 1) * 100 / 1.5
    v_pos = ((eixo_ewz / mn_ewz) - 1) * 100 / 1.5 if mn_ewz > 0 else 0
    v_neg = ((eixo_ewz / mx_ewz) - 1) * 100 / 1.5 if mx_ewz > 0 else 0
    max_d, min_d = eixo_dol * (1 + (v_pos / 100)), eixo_dol * (1 + (v_neg / 100))
    return {
        "vivo": eixo_dol * (1 + (v_at / 100)), 
        "max": max_d, "min": min_d, 
        "p50_up": (eixo_dol + max_d) / 2, 
        "p50_down": (eixo_dol + min_d) / 2
    }

# --- SIDEBAR (PAINEL ADM) ---
with st.sidebar:
    st.header("⚙️ PAINEL ADM")
    a_ewz = st.number_input("AXIS EWZ", value=36.42, format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT", value=5274.0, format="%.1f")
    st.info("Ajuste os eixos e feche a aba para ver o terminal.")

# --- HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""
<div class="header-bair">
    <div><span class="bair-text">BAIR</span><span style="color:#fff; font-size:28px;">-</span><span class="terminal-text">TERMINAL</span></div>
    <div style="display: flex; gap: 5px;">
        <div class="clock-box"><span class="clock-label">BSB</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">NY</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">LDN</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- GRID PRINCIPAL ---
placeholder = st.empty()

while True:
    with placeholder.container():
        ewz = fetch("EWZ")
        res = calcular_k97(a_ewz, ewz['at'], ewz['mx'], ewz['mn'], a_dol)
        
        if res:
            c_main, c_side = st.columns([2.6, 1])
            
            with c_main:
                st.markdown('<div class="monitor-bar">GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                
                # DOLFUT
                var_dol = ((res['vivo']/a_dol)-1)*100
                html += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{("#00ff00" if var_dol >= 0 else "#ff4d4d")}; font-weight:bold;'>{var_dol:+.2f}%</td></tr>"
                
                # Globais
                outros = {"SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "XAU/USD": "GC=F"}
                for lbl, sym in outros.items():
                    d = fetch(sym)
                    v = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                    html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['op']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td style='color:{("#00ff00" if v >= 0 else "#ff4d4d")};'>{v:+.2f}%</td></tr>"
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

            with c_side:
                st.markdown('<div class="monitor-bar">PROJEÇÕES</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="calc-panel">
                    <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span><span>{res['max']:.2f}</span></div>
                    <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span><span>{res['p50_up']:.2f}</span></div>
                    <div style="text-align:center; padding:4px; color:#00f2ff; font-weight:bold; font-size:13px; border-bottom:1px solid #444;">AXIS: {a_dol:.2f}</div>
                    <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span><span>{res['p50_down']:.2f}</span></div>
                    <div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MÍNIMA</span><span>{res['min']:.2f}</span></div>
                </div>
                <div class="calc-panel">
                    <div class="calc-row"><span>DOLFUT</span><span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
                </div>
                """, unsafe_allow_html=True)

    time.sleep(5)
    st.rerun()
