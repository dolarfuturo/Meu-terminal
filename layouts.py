import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO COMPACTA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; }
    .title-box { display: flex; align-items: center; gap: 8px; line-height: 1; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .sep-text { font-size: 46px; color: #ffffff; font-weight: 950; margin: 0 5px; }
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    .clock-container { display: flex; gap: 10px; color: #888; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; margin-bottom: 2px; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ewz-mini-container { display: flex; justify-content: space-around; padding: 4px 0; border-top: 1px solid #444; margin-top: 4px; }
    .ewz-mini-val { font-size: 11px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {
            "at": d['Close'].iloc[-1] * m, "cl": t.info.get('previousClose', d['Open'].iloc[0]) * m, 
            "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m
        }
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- PAINEL ADM ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
    st.button("ATUALIZAR")

# --- CAPTURA E CÁLCULOS (SOMA E SUBTRAÇÃO PURA) ---
spot = fetch("USDBRL=X")
ewz = fetch("EWZ")

# 1. SPREED
spreedd = (spot['mx'] - spot['mn']) / 8 if spot['mx'] > 0 else 0

# 2. PROJEÇÕES CONFORME IMAGEM (SEM MULTIPLICAÇÃO)
max_fut = a_dol + spot['mx'] + spreedd
min_fut = a_dol - spot['mn'] + spreedd

# Pontos intermediários (Apenas divisões da distância para o AXIS)
dist_max = max_fut - a_dol
dist_min = a_dol - min_fut

p75_up = a_dol + (dist_max * 0.75)
p50_up = a_dol + (dist_max * 0.50)
p25_up = a_dol + (dist_max * 0.25)

p75_down = a_dol - (dist_min * 0.75)
p50_down = a_dol - (dist_min * 0.50)
p25_down = a_dol - (dist_min * 0.25)

# 3. JUSTO E VIVO (Mantendo sua lógica de variação 60/40)
v_spot = ((spot['at'] / spot['cl']) - 1) if spot['cl'] > 0 else 0
v_ewz = ((ewz['at'] / ewz['cl']) - 1) if ewz['cl'] > 0 else 0
v_final = (v_spot * 0.6) - (v_ewz * 0.4)
dolfut_vivo = a_dol * (1 + v_final)
p_justo = a_dol * (1 + (v_final / 2))

# --- UI ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-box"><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div>""", unsafe_allow_html=True)

c_main, c_side = st.columns([3, 1])

with c_main:
    html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
    # DOLFUT
    html += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(dolfut_vivo/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(max_fut/1000):.4f}</td><td>{(min_fut/1000):.4f}</td><td style='color:{("#00ff00" if v_final >= 0 else "#ff4d4d")};'>{v_final*100:+.2f}%</td></tr>"
    # SPOT
    v_s_pct = ((spot['at']/spot['cl'])-1)*100 if spot['cl']>0 else 0
    html += f"<tr><td class='asset-name'>DOLSPOT</td><td class='price-col'>{spot['at']/1000:.4f}</td><td>{spot['cl']/1000:.4f}</td><td>{spot['op']/1000:.4f}</td><td>{spot['mx']/1000:.4f}</td><td>{spot['mn']/1000:.4f}</td><td style='color:{("#00ff00" if v_s_pct >= 0 else "#ff4d4d")};'>{v_s_pct:+.2f}%</td></tr>"
    st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

with c_side:
    st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{max_fut:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{p75_up:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{p50_up:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{p25_up:.2f}</span></div><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {a_dol:.2f}</div><div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{p25_down:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{p50_down:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{p75_down:.2f}</span></div><div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{min_fut:.2f}</span></div></div>""", unsafe_allow_html=True)
    
    st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{dolfut_vivo:.2f}</span></div><div class="calc-row"><span>P. JUSTO</span> <span style="color:#ffffff;">{p_justo:.2f}</span></div><div class="calc-row" style="border-bottom: none;"><span style="color:#ff4d4d;">SPREED</span> <span style="color:#00f2ff; font-weight:bold;">{spreedd:.2f}</span></div></div>""", unsafe_allow_html=True)

time.sleep(5)
st.rerun()
