import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: BORDAS BRANCAS, COLUNA PRICE MONITOR E TICKER LENTO ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    
    /* Blocos com bordas BRANCAS e Negrito */
    .main-grid { border: 3px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; font-weight: bold; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 16px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 14px; text-align: center; font-size: 17px; }
    
    /* Nome do Ativo maior e em destaque */
    .asset-name { font-size: 20px; color: #ffffff; text-align: left; padding-left: 15px; font-weight: 900; }

    /* Coluna PRICE na cor de monitoramento (Ciano) */
    .price-col { color: #00f2ff !important; font-size: 18px; }

    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; color: #00f2ff; font-size: 28px; font-weight: bold; }
    .clock-container { display: flex; gap: 20px; color: #888; font-family: 'monospace'; font-size: 12px; }
    .clock-box { text-align: center; border: 1px solid #ffffff; padding: 5px; border-radius: 4px; background: #0a141a; }
    .clock-time { color: #fff; font-size: 16px; display: block; }
    
    /* Painéis de Projeção com bordas Brancas */
    .calc-panel { border: 3px solid #ffffff; border-radius: 8px; padding: 12px; background: #0a141a; font-family: monospace; margin-bottom: 10px; font-weight: bold; }
    .calc-row { display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #444; font-size: 16px; }
    
    /* Ticker FULL WIDTH e LENTO (75s para leitura clara) */
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 12px 0; overflow: hidden; white-space: nowrap; margin-top: 25px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 75s linear infinite; font-family: 'monospace'; font-size: 16px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    .monitor-bar { background: #0a141a; border: 3px solid #ffffff; padding: 10px; text-align: center; color: #00f2ff; font-weight: bold; font-family: monospace; border-radius: 4px; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
@st.cache_data(ttl=600)
def calcular_referencias_eixo():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="5d", interval="1d")
        if df.empty: return 37.85, 38.10, 37.60
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        idx = -2 if agora.hour < 18 else -1
        mx, mn = df['High'].iloc[idx], df['Low'].iloc[idx]
        return (mx + mn) / 2, mx, mn
    except: return 37.85, 38.10, 37.60

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 1.5
    dolar_vivo = eixo_dol * (1 + (var_atual / 100))
    v_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 1.5
    v_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 1.5
    alvo_max, alvo_min = eixo_dol * (1 + (v_pos / 100)), eixo_dol * (1 + (v_neg / 100))
    return {
        "vivo": dolar_vivo, 
        "fraja": eixo_dol * (1 + (((eixo_ewz / p_ewz_atual) - 1) * 100 / 4.5 / 100)),
        "medio": eixo_dol * (1 + (((eixo_ewz / ((max_ewz + min_ewz) / 2)) - 1) * 100 / 100)),
        "v_atual": var_atual, "v_med": ((eixo_ewz / ((max_ewz + min_ewz) / 2)) - 1) * 100,
        "max": alvo_max, "min": alvo_min,
        "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), "p50_up": (eixo_dol + alvo_max) / 2, "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25),
        "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), "p50_down": (eixo_dol + alvo_min) / 2, "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
    }

def fetch(s):
    try:
        d = yf.Ticker(s).history(period="1d", interval="1m", prepost=True)
        return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return None

# --- SIDEBAR COM BOTÃO DE SALVAR ---
eixo_auto, mx_ref, mn_ref = calcular_referencias_eixo()
with st.sidebar:
    st.markdown("### ⚙️ AJUSTE DE VARIÁVEIS")
    with st.form("form_ajuste"):
        e_ewz = st.number_input("EIXO EWZ:", value=float(eixo_auto), format="%.2f")
        e_dol = st.number_input("EIXO DOLFUT:", value=5246.00, format="%.2f")
        salvar = st.form_submit_button("SALVAR ALTERAÇÕES")
    st.divider()
    st.write(f"**SENTINELA MAX:** {mx_ref:.2f}")
    st.write(f"**SENTINELA MIN:** {mn_ref:.2f}")

# --- UI PRINCIPAL ---
br_t = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M')
ny_t = datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M')
ld_t = datetime.now(pytz.timezone('Europe/London')).strftime('%H:%M')

st.markdown(f"""<div class="header-bair"><div>SHAKE VISION - <span style="color: #d4a017;">K97 TERMINAL</span></div><div class="clock-container"><div class="clock-box" style="border-color:#fff;">BRASÍLIA<span class="clock-time">{br_t}</span></div><div class="clock-box" style="border-color:#fff;">NEW YORK<span class="clock-time">{ny_t}</span></div><div class="clock-box" style="border-color:#fff;">LONDRES<span class="clock-time">{ld_t}</span></div></div></div>""", unsafe_allow_html=True)

ewz_live = fetch("EWZ")
if ewz_live:
    res = calcular_k97_total(e_ewz, ewz_live['at'], mx_ref, mn_ref, e_dol)
    h1, h2 = st.columns([3, 1])
    h1.markdown('<div class="monitor-bar">MONITORAMENTO DE ATIVOS</div>', unsafe_allow_html=True)
    h2.markdown('<div class="monitor-bar">PROJEÇÕES K97</div>', unsafe_allow_html=True)

    c_main, c_side = st.columns([3, 1])
    with c_main:
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #00f2ff;'>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        v2_var = ((res['vivo'] / e_dol) - 1) * 100
        v2_cor = "#00ff00" if v2_var >= 0 else "#ff0000"
        html_table += f"<tr><td class='asset-name'>SINTÉTICO 2.0 (VIVO)</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(e_dol/1000):.4f}</td><td>{(e_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{v2_cor};'>{v2_var:+.2f}%</td></tr>"
        
        ativos = {"SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "GOLD": "GC=F", "BRENT": "BZ=F"}
        ticker_items = [f"<span style='color:#fff;'>SINTÉTICO 2.0:</span> <span style='color:{v2_cor};'>{v2_var:+.2f}%</span>"]
        
        for label, sym in ativos.items():
            d = fetch(sym)
            if d:
                fmt = ".3f" if label == "GOLD" else (".4f" if "USD" in label or label == "SPOT" else ".2f")
                v = ((d['at']/d['cl'])-1)*100
                c = "#00ff00" if v >= 0 else "#ff0000"
                html_table += f"<tr><td class='asset-name'>{label}</td><td class='price-col'>{d['at']:{fmt}}</td><td>{d['cl']:{fmt}}</td><td>{d['cl']:{fmt}}</td><td>{d['mx']:{fmt}}</td><td>{d['mn']:{fmt}}</td><td style='color:{c};'>{v:+.2f}%</td></tr>"
                ticker_items.append(f"<span style='color:#fff;'>{label}:</span> <span style='color:{c};'>{v:+.2f}%</span>")
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ff7675;"><span>75% UP</span> <span>{res['p75_up']:.2f}</span></div><div class="calc-row" style="color:#fab1a0;"><span>50% UP</span> <span>{res['p50_up']:.2f}</span></div><div class="calc-row" style="color:#ffeaa7;"><span>25% UP</span> <span>{res['p25_up']:.2f}</span></div><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px;">EIXO: {e_dol:.2f}</div><div class="calc-row" style="color:#ffeaa7;"><span>25% DN</span> <span>{res['p25_down']:.2f}</span></div><div class="calc-row" style="color:#81ecec;"><span>50% DN</span> <span>{res['p50_down']:.2f}</span></div><div class="calc-row" style="color:#55efc4;"><span>75% DN</span> <span>{res['p75_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
        vm_cor = "#00ff00" if res['v_med'] >= 0 else "#ff0000"
        st.markdown(f"""<div class="calc-panel" style="border-color: #d4a017;"><div class="calc-row" style="color:#00f2ff;"><span>MÉDIO (50%)</span> <span>{res['medio']:.2f}</span></div><div class="calc-row" style="color:{vm_cor}; font-size:14px;"><span>VAR MÉDIA</span> <span>{res['v_med']:+.2f}%</span></div><div class="calc-row" style="color:#d4a017; border-bottom: none;"><span>3.6 (FRAJA)</span> <span>{res['fraja']:.2f}</span></div></div>""", unsafe_allow_html=True)

    ticker_html = " • ".join(ticker_items)
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{ticker_html} • {ticker_html}</div></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
