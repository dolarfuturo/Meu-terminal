import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO (PRESERVADA) ---
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
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 14px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- ENGINE DE VARIAÇÃO ---
def get_var(symbol):
    try:
        t = yf.Ticker(symbol)
        d = t.history(period="1d", interval="1m", prepost=True)
        cl = t.info.get('previousClose') or d['Open'].iloc[0]
        at = d['Close'].iloc[-1]
        return ((at / cl) - 1) * 100
    except: return 0.0

# --- PAINEL ADM ---
with st.sidebar:
    st.markdown("### ⚙️ CONFIGURAÇÃO")
    axis_dol = st.number_input("AXIS DOLFUT (BASE):", value=5246.00, format="%.2f")

# --- CÁLCULO SINTÉTICO ---
var_spot = get_var("USDBRL=X")
var_ewz = get_var("EWZ")
var_ewz_inv = var_ewz * -1

# A MÁGICA: 60% Spot + 40% EWZ Invertido
var_final = (var_spot * 0.6) + (var_ewz_inv * 0.4)
preco_calculado = axis_dol * (1 + (var_final / 100))

# --- UI ---
st.markdown('<div class="header-bair"><span class="bair-text">BAIR</span> <span class="terminal-text">TERMINAL</span></div>', unsafe_allow_html=True)

c1, c2 = st.columns([3, 1])

with c1:
    html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Preço Projetado</th><th>Variação</th></tr></thead><tbody>"""
    
    # LINHA DO DOLFUT (SINTÉTICA)
    cor = "#00ff00" if var_final >= 0 else "#ff4d4d"
    html += f"""<tr>
        <td class="asset-name">DOLFUT (CALCULADO)</td>
        <td class="price-col">{preco_calculado:.2f}</td>
        <td style="color:{cor}; font-weight:bold;">{var_final:+.2f}%</td>
    </tr>"""
    
    # REFERÊNCIAS REAIS
    html += f"<tr><td class='asset-name'>VAR SPOT (60%)</td><td>-</td><td>{var_spot:+.2f}%</td></tr>"
    html += f"<tr><td class='asset-name'>VAR EWZ INV (40%)</td><td>-</td><td>{var_ewz_inv:+.2f}%</td></tr>"
    
    st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="calc-panel">
        <div class="calc-row"><span>EIXO BASE</span><span>{axis_dol:.2f}</span></div>
        <div class="calc-row" style="color:#00f2ff;"><span>DOLFUT VIVO</span><span>{preco_calculado:.2f}</span></div>
        <div class="calc-row"><span>VAR FINAL</span><span>{var_final:+.2f}%</span></div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(5)
st.rerun()
