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
        info = t.info
        cl = info.get('previousClose', d['Close'].iloc[0] if not d.empty else 0)
        if d.empty: return {"at": 0.0, "cl": cl, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {"at": d['Close'].iloc[-1], "cl": cl, "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_ajustes(eixo_dol, spot):
    try:
        # Normalizando Spot para escala milhar (5.31 -> 5310)
        s_at = spot['at'] * 1000 if spot['at'] < 100 else spot['at']
        s_mx = spot['mx'] * 1000 if spot['mx'] < 100 else spot['mx']
        s_mn = spot['mn'] * 1000 if spot['mn'] < 100 else spot['mn']
        s_cl = spot['cl'] * 1000 if spot['cl'] < 100 else spot['cl']

        # --- SEU CÁLCULO EXATO ---
        spreed = (s_mx - s_mn) / 8
        max_fut = eixo_dol + s_mx + spreed
        min_fut = eixo_dol - s_mn + spreed
        media_dol = (s_mx + s_mn) / 2
        
        # Variação para o Dolfut Vivo
        var_v = ((s_at / s_cl) - 1)
        dolar_vivo = eixo_dol * (1 + var_v)

        return {
            "max": max_fut, "min": min_fut, "medio": media_dol, "vivo": dolar_vivo,
            "v_v": var_v * 100,
            "p75_up": eixo_dol + (max_fut - eixo_dol) * 0.75,
            "p50_up": eixo_dol + (max_fut - eixo_dol) * 0.50,
            "p25_up": eixo_dol + (max_fut - eixo_dol) * 0.25,
            "p25_down": eixo_dol - (eixo_dol - min_fut) * 0.25,
            "p50_down": eixo_dol - (eixo_dol - min_fut) * 0.50,
            "p75_down": eixo_dol - (eixo_dol - min_fut) * 0.75,
        }
    except: return None

# --- PAINEL ADM ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_dol = st.number_input("AXIS DOLFUT:", value=5308.00, format="%.2f")

# --- UI HEADER ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

spot_live = fetch("USDBRL=X")
res = calcular_ajustes(a_dol, spot_live)

if res:
    c_main, c_side = st.columns([3, 1])
    with c_main:
        html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        # DOLFUT
        html += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{res['vivo']:.2f}</td><td>{a_dol:.2f}</td><td>{res['max']:.2f}</td><td>{res['min']:.2f}</td><td style='color:{("#00ff00" if res['v_v'] >= 0 else "#ff4d4d")};'>{res['v_v']:+.2f}%</td></tr>"
        # DOLSPOT
        var_s = ((spot_live['at']/spot_live['cl'])-1)*100
        html += f"<tr><td class='asset-name'>DOLSPOT</td><td class='price-col'>{spot_live['at']:.4f}</td><td>{spot_live['cl']:.4f}</td><td>{spot_live['mx']:.4f}</td><td>{spot_live['mn']:.4f}</td><td style='color:{("#00ff00" if var_s >= 0 else "#ff4d4d")};'>{var_s:+.2f}%</td></tr>"
        st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        # BLOCO SETA VERMELHA (MAX/MIN)
        st.markdown(f"""<div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div>
            <div style="text-align:center; padding:10px; color:#00f2ff; font-size:18px; font-weight:bold; border-y:1.5px solid #444;">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)
        
        # BLOCO SETA VERDE (MÉDIA DOL)
        st.markdown(f"""<div class="calc-panel">
            <div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
            <div class="calc-row" style="background:#0a2a1a;"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff;">{res['medio']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)

time.sleep(5)
st.rerun()
