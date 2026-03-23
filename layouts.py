import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO MANTIDA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; font-weight: bold; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        # Forçamos a escala correta para Spot e Futuro se vierem em decimais
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        
        # Ajuste de escala para ativos que vêm como 5.30 em vez de 5300
        mult = 1000 if s in ["USDBRL=X", "BRL=X"] else 1
        
        return {
            "at": d['Close'].iloc[-1] * mult, 
            "cl": t.info.get('previousClose', d['Open'].iloc[0]) * mult, 
            "op": d['Open'].iloc[0] * mult,
            "mx": d['High'].max() * mult, 
            "mn": d['Low'].min() * mult
        }
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- PROCESSAMENTO DOS CÁLCULOS SHARK ---
spot_data = fetch("USDBRL=X") # DOLSPOT (Âncora)
ewz_data = fetch("EWZ")

# Variáveis da Sidebar (Painel ADM)
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_dol = st.number_input("AXIS DOLFUT:", value=5308.00, format="%.2f")
    a_ewz = st.number_input("AXIS EWZ:", value=35.38, format="%.2f")

# --- LÓGICA SOLICITADA ---
# 1. SPREDD = (Max Spot - Min Spot) / 8
mx_s = spot_data['mx']
mn_s = spot_data['mn']
spreedd = (mx_s - mn_s) / 8 if mx_s > 0 else 0

# 2. BLOCO VERMELHO: MAX/MIN FUTURO ANCORADO NO AXIS
# MAX FUT = AXIS + MAX SPOT + SPREDD
# MIN FUT = AXIS - MIN SPOT + SPREDD (usando o Axis como referência de saída)
max_futuro = a_dol + (mx_s - spot_data['cl']) + spreedd
min_futuro = a_dol - (spot_data['cl'] - mn_s) + spreedd

# 3. BLOCO VERDE: MÉDIA DOL
# MÉDIA DOL = (MAX SPOT + MIN SPOT) / 2
media_dol_shark = (mx_s + mn_s) / 2

# --- UI HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""<div class="header-bair"><div><span class="bair-text">BAIR</span> <span style='color:#fff; font-size:40px;'>-</span> <span class="terminal-text">TERMINAL DOLLAR</span></div><div style='display:flex; gap:10px;'><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

# --- GRID PRINCIPAL ---
c_main, c_side = st.columns([3, 1])

with c_main:
    html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
    
    ativos_monitor = {
        "DOLFUT": "BRL=X", 
        "DOLSPOT": "USDBRL=X", 
        "DXY": "DX-Y.NYB", 
        "EWZ": "EWZ", 
        "XAU/USD": "GC=F",
        "PETROLEO BRENT": "BZ=F"
    }

    for lbl, sym in ativos_monitor.items():
        d = spot_data if lbl == "DOLSPOT" else (ewz_data if lbl == "EWZ" else fetch(sym))
        var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
        color = "#00ff00" if var >= 0 else "#ff4d4d"
        # Formatação de decimais
        fmt = ".4f" if "DOL" in lbl or "USD" in lbl else ".2f"
        
        html_table += f"""<tr>
            <td class='asset-name'>{lbl}</td>
            <td class='price-col'>{d['at']:{fmt}}</td>
            <td>{d['cl']:{fmt}}</td>
            <td>{d['op']:{fmt}}</td>
            <td>{d['mx']:{fmt}}</td>
            <td>{d['mn']:{fmt}}</td>
            <td style='color:{color};'>{var:+.2f}%</td>
        </tr>"""
    st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

with c_side:
    # BLOCO SETA VERMELHA (PROJEÇÃO FUTURO)
    st.markdown(f"""
    <div class="calc-panel">
        <div class="calc-row" style="color:#ff4d4d; font-size:16px;"><span>MÁXIMA</span> <span>{max_futuro:.2f}</span></div>
        <div style="text-align:center; padding: 20px 0; color: #00f2ff; font-size: 24px; font-weight: 950; border-top:2px solid #fff; border-bottom:2px solid #fff; margin: 10px 0;">AXIS: {a_dol:.2f}</div>
        <div class="calc-row" style="color:#00ff88; font-size:16px; border-bottom: none;"><span>MÍNIMA</span> <span>{min_futuro:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # BLOCO SETA VERDE (MÉTRICAS SPOT)
    # Cálculo do P. Justo mantido conforme estrutura original mas usando a nova média
    p_justo = (media_dol_shark + a_dol) / 2
    
    st.markdown(f"""
    <div class="calc-panel">
        <div class="calc-row" style="color:#ffffff;"><span>DOL SPOT</span> <span style="color:#00f2ff;">{spot_data['at']:.2f}</span></div>
        <div class="calc-row" style="color:#ffff00;"><span>MÉDIA DOL</span> <span style="color:#00f2ff;">{media_dol_shark:.2f}</span></div>
        <div class="calc-row" style="border-bottom: none; color:#d4a017;"><span>P. JUSTO</span> <span style="color:#ffffff;">{p_justo:.2f}</span></div>
        <div style="font-size: 10px; color: #666; text-align: center; margin-top: 5px;">SPREDD APLICADO: {spreedd:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(5)
st.rerun()
