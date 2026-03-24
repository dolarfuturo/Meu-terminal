import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO ULTRA COMPACTA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 12px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 8px; text-align: center; font-size: 14px; }
    .asset-name { font-size: 15px; color: #fff; text-align: left; font-weight: bold; padding-left: 10px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 5px 10px; border-bottom: 2px solid #ffffff; margin-bottom: 8px; }
    .title-box { display: flex; align-items: center; gap: 8px; line-height: 1; }
    .bair-text { font-size: 40px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .sep-text { font-size: 40px; color: #ffffff; font-weight: 950; margin: 0 5px; }
    .terminal-text { font-size: 40px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    
    .clock-container { display: flex; gap: 8px; color: #888; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 2px 8px; border-radius: 4px; background: #0a141a; min-width: 80px; }
    .clock-label { font-size: 9px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; }
    .clock-time { color: #fff; font-size: 15px; font-weight: bold; display: block; }

    /* BLOCOS COLADOS */
    .calc-panel { border: 2px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 3px 6px; border-bottom: 1px solid #444; font-size: 12px; font-weight: bold; align-items: center; }
    
    /* BARRA K97 E SETA DISCRETA */
    .bar-wrapper-dual { background: #0a141a; padding: 12px 8px 4px 8px; border: 2px solid #ffffff; border-radius: 4px; margin-top: 0px; text-align: center; position: relative; }
    .marker-container { display: flex; justify-content: space-between; position: absolute; width: calc(100% - 16px); top: 1px; font-size: 8px; color: #666; font-weight: bold; }
    .force-container-dual { background: #111; height: 14px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1.5px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    
    .sinal-indicator { font-size: 20px; font-weight: 950; line-height: 1; margin-top: 2px; } /* TAMANHO 20PX */
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.4; } }

    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; padding: 6px 0; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 13px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ewz-mini-container { display: flex; justify-content: space-around; padding: 2px 0; border-top: 1px solid #444; margin-top: 2px; }
    .ewz-mini-val { font-size: 10px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        ref_close = t.info.get('previousClose')
        if s == "EWZ":
            d_hist = t.history(period="3d", interval="1m", prepost=True)
            if not d_hist.empty:
                d_hist.index = d_hist.index.tz_convert(tz_sp)
                unique_dates = sorted(list(set(d_hist.index.date)))
                data_anterior = unique_dates[-2] if len(unique_dates) > 1 else unique_dates[0]
                f_21h = d_hist.between_time('05:00', '21:00').loc[d_hist.index.date == data_anterior]
                if not f_21h.empty: ref_close = f_21h['Close'].iloc[-1]
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1] * m, "cl": (ref_close or d['Open'].iloc[0]) * m, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

@st.cache_data(ttl=600)
def calcular_sentinela():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d")
        if df.empty: return 37.85
        mx, mn = df['High'].iloc[-2], df['Low'].iloc[-2]
        return (mx + mn) / 2
    except: return 37.85

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol, spot_data):
    try:
        v_spreed = (spot_data['mx'] - spot_data['mn']) / 8
        v_spot = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        v_ewz = ((p_ewz_atual / fetch("EWZ")['cl']) - 1) if fetch("EWZ")['cl'] > 0 else 0
        v_final = (v_spot * 0.6) - (v_ewz * 0.4)
        
        dolar_vivo = spot_data['at'] 
        dolar_fraja = eixo_dol * (1 + (v_final / 2))
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        alvo_max = spot_data['mx'] + v_spreed
        p50_up = (alvo_max + eixo_dol) / 2
        p50_down = ((spot_data['mn'] + v_spreed) + eixo_dol) / 2

        # BARRA FORÇA
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = (min(100, (abs(diff)/20)*100), 0) if diff < 0 else (0, min(100, (abs(diff)/20)*100))

        # SETA SEMPRE VISÍVEL (BINÁRIA)
        if spot_data['at'] < p50_up:
            seta_txt, seta_cor = "▼ VENDA", "#ff4d4d"
        else:
            seta_txt, seta_cor = "▲ COMPRA", "#00ff88"
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, "ewz_med": (max_ewz + min_ewz) / 2,
            "max": alvo_max, "min": spot_data['mn'] + v_spreed, "v_v": v_final * 100, "spreed": v_spreed,
            "p50_up": p50_up, "p50_down": p50_down, "p_v": p_v, "p_r": p_r, "seta": seta_txt, "seta_cor": seta_cor
        }
    except: return None

# --- UI HEADER ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    with st.form("ajuste_vars"):
        a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        st.form_submit_button("SALVAR")

tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">K97</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">SP</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">NY</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">LD</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

ewz_live = fetch("EWZ")
spot_live = fetch("USDBRL=X")
res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol, spot_live)

if res:
    c_main, c_side = st.columns([3, 1])
    with c_main:
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        v_v = res['v_v']
        html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{("#00ff00" if v_v >= 0 else "#ff4d4d")}; font-weight:bold;'>{v_v:+.2f}%</td></tr>"
        ticker_items = [f"DOLFUT: <span style='color:{("#00ff00" if v_v >= 0 else "#ff4d4d")};'>{v_v:+.2f}%</span>"]
        
        outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
        for lbl, sym in outros.items():
            d = spot_live if lbl == "DOLSPOT" else (ewz_live if lbl == "EWZ" else fetch(sym))
            f = ".4f" if lbl in ["DOLSPOT", "DOLFUT"] or "USD" in lbl else ".2f"
            var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
            color = "#00ff00" if var >= 0 else "#ff4d4d"
            html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{(d['at']/1000 if lbl=='DOLSPOT' else d['at']):{f}}</td><td>{(d['cl']/1000 if lbl=='DOLSPOT' else d['cl']):{f}}</td><td>{(d['op']/1000 if lbl=='DOLSPOT' else d['op']):{f}}</td><td>{(d['mx']/1000 if lbl=='DOLSPOT' else d['mx']):{f}}</td><td>{(d['mn']/1000 if lbl=='DOLSPOT' else d['mn']):{f}}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
            ticker_items.append(f"{lbl}: <span style='color:{color};'>{var:+.2f}%</span>")
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>50% UP</span> <span>{res['p50_up']:.2f}</span></div><div style="text-align:center; padding: 6px; color: #00f2ff; font-size: 16px; font-weight: bold; border-top:1px solid #444; border-bottom:1px solid #444; margin: 3px 0;">AXIS: {a_dol:.2f}</div><div class="calc-row" style="color:#ffa500;"><span>50% DOWN</span> <span>{res['p50_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span style="color:#ffffff;">DOLFUT</span> <span style="color:#00f2ff; font-size: 14px;">{res['vivo']:.2f}</span></div><div class="calc-row"><span style="color:#d4a017;">JUSTO</span> <span style="color:#ffffff;">{res['fraja']:.2f}</span></div><div class="calc-row" style="border-bottom: none;"><span style="color:#ff4d4d;">SPREAD</span> <span style="color:#00f2ff;">{res['spreed']:.2f}</span></div><div class="ewz-mini-container"><span class="ewz-mini-val" style="color:#00ff88;">{ewz_live['mx']:.2f}</span><span class="ewz-mini-val" style="color:#00f2ff;">{res['ewz_med']:.2f}</span><span class="ewz-mini-val" style="color:#ff4d4d;">{ewz_live['mn']:.2f}</span></div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="bar-wrapper-dual"><div class="marker-container"><div>80%</div><div>|</div><div>80%</div></div><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width: {res['p_v']}%;"></div></div><div class="bar-side"><div class="fill-red" style="width: {res['p_r']}%;"></div></div></div><div class="sinal-indicator blink" style="color:{res['seta_cor']};">{res['seta']}</div></div>""", unsafe_allow_html=True)

    ticker_html = " • ".join(ticker_items)
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{ticker_html} • {ticker_html}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
