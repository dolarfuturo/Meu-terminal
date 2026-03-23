import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO ---
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
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 10px 8px; border-bottom: 1px solid #444; font-size: 14px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {"at": d['Close'].iloc[-1], "cl": t.info.get('previousClose', d['Close'].iloc[0]), "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- CÁLCULOS SOLICITADOS ---
def calcular_terminal(a_dol, spot):
    try:
        # Pega os valores reais do spot (ex: 5.31)
        s_mx = spot['mx']
        s_mn = spot['mn']
        
        # 1. SPREED = (Max - Min / 8 do spot)
        spreed = (s_mx - s_mn) / 8
        
        # 2. MAX FUT = AXIS + Max do spot + SPREED
        max_fut = a_dol + s_mx + spreed
        
        # 3. MIN FUT = AXIS - Min do spot + SPREED
        min_fut = a_dol - s_mn + spreed
        
        # 4. MEDIA DOL = (Max + Min do spot / 2)
        media_dol = (s_mx + s_mn) / 2
        
        # Para o Dolfut Vivo, mantemos a variação do Spot aplicada ao AXIS
        var_spot = (spot['at'] / spot['cl']) - 1 if spot['cl'] > 0 else 0
        dolfut_vivo = a_dol * (1 + var_spot)
        
        return {
            "max": max_fut,
            "min": min_fut,
            "medio": media_dol,
            "vivo": dolfut_vivo,
            "p50_max": (a_dol + max_fut) / 2,
            "p50_min": (a_dol + min_fut) / 2,
            "var": var_spot * 100
        }
    except: return None

# --- UI ---
with st.sidebar:
    a_dol = st.number_input("AXIS DOLFUT:", value=5308.00, format="%.2f")

st.markdown(f"""<div class="header-bair"><div><span class="bair-text">BAIR</span><span style="color:white; font-size:46px;">-</span><span class="terminal-text">TERMINAL</span></div></div>""", unsafe_allow_html=True)

spot_data = fetch("USDBRL=X")
res = calcular_terminal(a_dol, spot_data)

if res:
    c1, c2 = st.columns([3, 1])
    with c1:
        # Tabela Principal
        html = f"""<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Max Spot</th><th>Min Spot</th><th>Var %</th></tr></thead><tbody>
        <tr><td class="asset-name">DOLFUT (Calculado)</td><td class="price-col">{res['vivo']:.2f}</td><td>{spot_data['mx']:.4f}</td><td>{spot_data['mn']:.4f}</td><td>{res['var']:+.2f}%</td></tr>
        </tbody></table></div>"""
        st.markdown(html, unsafe_allow_html=True)

    with c2:
        # BLOCO SETA VERMELHA
        st.markdown(f"""<div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>50% ALVO</span> <span>{res['p50_max']:.2f}</span></div>
            <div style="text-align:center; padding:15px; color:#00f2ff; font-size:20px; font-weight:bold; border-y:2px solid #fff; margin:10px 0;">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffa500;"><span>50% ALVO</span> <span>{res['p50_min']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)
        
        # BLOCO SETA VERDE
        st.markdown(f"""<div class="calc-panel">
            <div class="calc-row"><span>DOLFUT VIVO</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
            <div class="calc-row" style="border-bottom:none; background:#112211;"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff;">{res['medio']:.4f}</span></div>
        </div>""", unsafe_allow_html=True)

time.sleep(5)
st.rerun()
