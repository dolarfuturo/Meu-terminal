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
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0}
        return {"at": d['Close'].iloc[-1], "cl": t.info.get('previousClose', d['Close'].iloc[0]), "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0}

def calcular_ajuste_real(a_dol, spot):
    try:
        # CONVERSÃO PARA PONTOS (Escala de 5.31 para 5310)
        s_at = spot['at'] * 1000
        s_mx = spot['mx'] * 1000
        s_mn = spot['mn'] * 1000
        s_cl = spot['cl'] * 1000

        # --- SUAS FÓRMULAS ---
        # SPREED = (Max - Min / 8 do spot)
        spreed = (s_mx - s_mn) / 8
        
        # MAX FUT = AXIS + Max do spot + SPREED
        max_fut = a_dol + (s_mx - s_cl) + spreed # Diferença do spot aplicada ao AXIS
        
        # MIN FUT = AXIS - Min do spot + SPREED
        # Ajustado para que a queda do spot subtraia do AXIS
        min_fut = a_dol - (s_cl - s_mn) + spreed
        
        # MEDIA DOL (Preço do Spot / 2 não faz sentido no terminal, então mantemos a média dos pontos)
        media_dol = (s_mx + s_mn) / 2
        
        # DOLFUT VIVO
        v_final = (s_at / s_cl) - 1 if s_cl > 0 else 0
        dolar_vivo = a_dol * (1 + v_final)

        return {
            "vivo": dolar_vivo, "medio": media_dol, "max": max_fut, "min": min_fut,
            "v_v": v_final * 100, "p50_up": (a_dol + max_fut) / 2, "p50_down": (a_dol + min_fut) / 2
        }
    except: return None

# --- UI ---
with st.sidebar:
    a_dol = st.number_input("AXIS DOLFUT:", value=5308.00, format="%.2f")

st.markdown("""<div class="header-bair"><div><span class="bair-text">BAIR</span><span style="color:white; font-size:46px;">-</span><span class="terminal-text">TERMINAL</span></div></div>""", unsafe_allow_html=True)

spot_live = fetch("USDBRL=X")
res = calcular_ajuste_real(a_dol, spot_live)

if res:
    c1, c2 = st.columns([3, 1])
    with c1:
        # Tabela Principal Limpa
        html = f"""<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Axis Ref</th><th>Var Spot</th></tr></thead><tbody>
        <tr><td class="asset-name">DOLFUT VIVO</td><td class="price-col">{res['vivo']:.2f}</td><td>{a_dol:.2f}</td><td style='color:{"#00ff00" if res['v_v'] >= 0 else "#ff4d4d"}'>{res['v_v']:+.2f}%</td></tr>
        </tbody></table></div>"""
        st.markdown(html, unsafe_allow_html=True)

    with c2:
        # PAINEL DE ALVOS (SETA VERMELHA)
        st.markdown(f"""<div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>50% ALVO</span> <span>{res['p50_up']:.2f}</span></div>
            <div style="text-align:center; padding:15px; color:#00f2ff; font-size:20px; font-weight:bold; border-top:2px solid #fff; border-bottom:2px solid #fff; margin:10px 0;">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffa500;"><span>50% ALVO</span> <span>{res['p50_down']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)
        
        # MÉDIA DOL (SETA VERDE)
        st.markdown(f"""<div class="calc-panel">
            <div class="calc-row" style="border-bottom:none; background:#112211;"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff;">{res['medio']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)

time.sleep(5)
st.rerun()
