import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: ESTILIZAÇÃO REFINADA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; color: #00f2ff; font-weight: bold; }
    .bair-text { font-size: 42px; letter-spacing: 2px; } 
    .terminal-text { font-size: 26px; color: #d4a017; }
    .clock-container { display: flex; gap: 20px; color: #888; font-family: 'monospace'; font-size: 12px; }
    .clock-box { text-align: center; border: 1px solid #ffffff; padding: 5px; border-radius: 4px; background: #0a141a; }
    .clock-time { color: #fff; font-size: 16px; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 10px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 6px 8px; border-bottom: 1px solid #444; font-size: 14px; font-weight: bold; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 20px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 45s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .monitor-bar { background: #0a141a; border: 2px solid #ffffff; padding: 8px; text-align: center; color: #00f2ff; font-weight: bold; font-family: monospace; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS COM FILTRO OPERACIONAL ---
def fetch_operacional(symbol):
    try:
        d = yf.Ticker(symbol).history(period="1d", interval="1m", prepost=False)
        if d.empty: return None
        d.index = d.index.tz_convert('America/Sao_Paulo')
        d_op = d.between_time(dt_time(10, 30), dt_time(17, 0))
        if d_op.empty:
            return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
        return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d_op['High'].max(), "mn": d_op['Low'].min()}
    except: return None

# --- CALIBRAGEM INICIAL ---
ewz_ref = fetch_operacional("EWZ")
mx_r = ewz_ref['mx'] if ewz_ref else 38.10
mn_r = ewz_ref['mn'] if ewz_ref else 37.60
eixo_s = (mx_r + mn_r) / 2

with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    with st.form("ajuste_eixo"):
        e_ewz = st.number_input("EIXO EWZ:", value=float(eixo_s), format="%.2f")
        e_dol = st.number_input("EIXO DOLFUT:", value=5246.00, format="%.2f")
        salvar = st.form_submit_button("SALVAR VARIÁVEIS")
    st.divider()
    st.write(f"**REF MAX (10:30-17h):** {mx_r:.2f}")
    st.write(f"**REF MIN (10:30-17h):** {mn_r:.2f}")

# --- LÓGICA K97 ---
def calc_k97(e_ewz, ewz_at, mx_e, mn_e, e_dol):
    v_at = ((e_ewz / ewz_at) - 1) * 100 / 1.5
    d_v = e_dol * (1 + (v_at / 100))
    v_mx = ((e_ewz / mx_e) - 1) * 100 / 1.5
    v_mn = ((e_ewz / mn_e) - 1) * 100 / 1.5
    a_mx, a_mn = e_dol * (1 + (v_mn / 100)), e_dol * (1 + (v_mx / 100))
    return {
        "vivo": d_v, "max": a_mx, "min": a_mn,
        "fraja": e_dol * (1 + (((e_ewz / ewz_at) - 1) * 100 / 4.5 / 100)),
        "medio": e_dol * (1 + (((e_ewz / ((mx_e + mn_e) / 2)) - 1) * 100 / 100)),
        "v_at": v_at, "v_med": ((e_ewz / ((mx_e + mn_e) / 2)) - 1) * 100,
        "p75_u": (e_dol + (a_mx - e_dol)*0.75), "p50_u": (e_dol + a_mx) / 2, "p25_u": (e_dol + (a_mx - e_dol)*0.25),
        "p75_d": (e_dol + (a_mn - e_dol)*0.75), "p50_d": (e_dol + a_mn) / 2, "p25_d": (e_dol + (a_mn - e_dol)*0.25)
    }

# --- UI ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div><span class="bair-text">BAIR</span> - <span class="terminal-text">TERMINAL DOLAR</span></div><div class="clock-container"><div class="clock-box">BRASÍLIA<span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box">NEW YORK<span class="clock-time">{datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M')}</span></div><div class="clock-box">LONDRES<span class="clock-time">{datetime.now(pytz.timezone('Europe/London')).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

if ewz_ref:
    res = calc_k97(e_ewz, ewz_ref['at'], mx_r, mn_r, e_dol)
    c1, c2 = st.columns([3, 1])
    c1.markdown('<div class="monitor-bar">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
    c2.markdown('<div class="monitor-bar">CÁLCULOS DE PROJEÇÕES</div>', unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1])
    with col_main:
        html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        v_v = ((res['vivo'] / e_dol) - 1) * 100
        c_v = "#00ff00" if v_v >= 0 else "#ff0000"
        html += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(e_dol/1000):.4f}</td><td>{(e_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{c_v}; font-weight:bold;'>{v_v:+.2f}%</td></tr>"
        
        # GRADE COMPLETA DE ATIVOS
        ativos_lista = {
            "SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", 
            "GBP/USD": "GBPUSD=X", "EUR/USD": "EURUSD=X", "JPY/USD": "JPYUSD=X",
            "GOLD": "GC=F", "BRENT": "BZ=F", "WTI": "CL=F",
            "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "IBOV": "^BVSP"
        }
        t_items = [f"<span style='color:#fff;'>DOLFUT:</span> <span style='color:{c_v};'>{v_v:+.2f}%</span>"]
        
        for l, s in ativos_lista.items():
            d = fetch_operacional(s)
            if d:
                fmt = ".3f" if l == "GOLD" else (".4f" if "USD" in l or l == "SPOT" else ".2f")
                v = ((d['at']/d['cl'])-1)*100
                c = "#00ff00" if v >= 0 else "#ff0000"
                html += f"<tr><td class='asset-name'>{l}</td><td class='price-col'>{d['at']:{fmt}}</td><td>{d['cl']:{fmt}}</td><td>{d['cl']:{fmt}}</td><td>{d['mx']:{fmt}}</td><td>{d['mn']:{fmt}}</td><td style='color:{c}; font-weight:bold;'>{v:+.2f}%</td></tr>"
                t_items.append(f"<span style='color:#fff;'>{l}:</span> <span style='color:{c};'>{v:+.2f}%</span>")
        st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

    with col_side:
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ff7675;"><span>75% UP</span> <span>{res['p75_u']:.2f}</span></div><div class="calc-row" style="color:#fab1a0;"><span>50% UP</span> <span>{res['p50_u']:.2f}</span></div><div class="calc-row" style="color:#ffeaa7;"><span>25% UP</span> <span>{res['p25_u']:.2f}</span></div><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 16px;">EIXO: {e_dol:.2f}</div><div class="calc-row" style="color:#ffeaa7;"><span>25% DN</span> <span>{res['p25_d']:.2f}</span></div><div class="calc-row" style="color:#81ecec;"><span>50% DN</span> <span>{res['p50_d']:.2f}</span></div><div class="calc-row" style="color:#55efc4;"><span>75% DN</span> <span>{res['p75_d']:.2f}</span></div><div class="calc-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="calc-panel" style="border-color: #d4a017;"><div class="calc-row" style="color:#00f2ff;"><span>MÉDIA DOLFUT</span> <span>{res['medio']:.2f}</span></div><div class="calc-row" style="color:{("#00ff00" if res['v_med'] >= 0 else "#ff0000")}; font-size:12px;"><span>VAR MÉDIA</span> <span>{res['v_med']:+.2f}%</span></div><div class="calc-row" style="color:#d4a017; border-bottom: none;"><span>PREÇO JUSTO</span> <span>{res['fraja']:.2f}</span></div></div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(t_items)} • {" • ".join(t_items)}</div></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
