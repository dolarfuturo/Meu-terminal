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
    
    /* ESTILO DA BARRA DE FORÇA BIDIRECIONAL */
    .bar-wrapper { background: #0a141a; padding: 10px; border: 2.5px solid #ffffff; border-radius: 8px; margin-top: 5px; text-align: center; }
    .force-container-dual { background: #111; height: 20px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 5px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .label-row { display: flex; justify-content: space-between; font-size: 9px; color: #888; font-weight: bold; text-transform: uppercase; }

    .sinal-indicator { font-size: 36px; font-weight: 900; line-height: 1; margin-top: 5px; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }

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
        return {"at": d['Close'].iloc[-1]*m, "cl": (ref_close or d['Open'].iloc[0])*m, "op": d['Open'].iloc[0]*m, "mx": d['High'].max()*m, "mn": d['Low'].min()*m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

@st.cache_data(ttl=600)
def calcular_sentinela():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d", prepost=False)
        if df.empty: return 37.85
        tz_sp = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(tz_sp)
        hoje = agora.date()
        ultima_data_yahoo = df.index[-1].date()
        idx = -2 if (ultima_data_yahoo == hoje and agora.hour < 18) else -1
        return (df['High'].iloc[idx] + df['Low'].iloc[idx]) / 2
    except: return 37.85

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol, spot_data):
    try:
        if p_ewz_atual == 0: return None
        v_spreed = (spot_data['mx'] - spot_data['mn']) / 8
        v_spot = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        v_ewz = ((p_ewz_atual / fetch("EWZ")['cl']) - 1) if fetch("EWZ")['cl'] > 0 else 0
        v_final = (v_spot * 0.6) - (v_ewz * 0.4)
        
        dolar_vivo = spot_data['at'] 
        dolar_fraja = eixo_dol * (1 + (v_final / 2))
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        alvo_max = spot_data['mx'] + v_spreed
        alvo_min = spot_data['mn'] + v_spreed
        p50_up = (alvo_max + eixo_dol) / 2
        p50_down = (alvo_min + eixo_dol) / 2

        # BARRA BIDIRECIONAL: Distância X = AXIS -> P50
        dist_x = abs(eixo_dol - p50_down)
        diff_atual = spot_data['at'] - eixo_dol
        pct_v, pct_r = 0, 0
        if diff_atual < 0: pct_v = min(100, (abs(diff_atual) / (dist_x * 2)) * 100)
        else: pct_r = min(100, (abs(diff_atual) / (dist_x * 2)) * 100)

        # SETA DE FLUXO INDEPENDENTE
        seta_txt, seta_cor = "•", "#888"
        if spot_data['at'] > spot_data['mn'] + 2: seta_txt, seta_cor = "▲ COMPRA", "#00ff00"
        if spot_data['at'] < p50_up and spot_data['at'] > eixo_dol: seta_txt, seta_cor = "▼ VENDA", "#ff4d4d"
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, "ewz_med": (max_ewz + min_ewz) / 2,
            "max": alvo_max, "min": alvo_min, "v_v": v_final * 100, "spreed": v_spreed,
            "p50_up": p50_up, "p50_down": p50_down, "pct_v": pct_v, "pct_r": pct_r, "seta": seta_txt, "seta_cor": seta_cor
        }
    except: return None

# --- UI HEADER ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug))
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00)

tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

ewz_live = fetch("EWZ")
spot_live = fetch("USDBRL=X")
res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol, spot_live)

if res:
    c_main, c_side = st.columns([3, 1])
    with c_main:
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        ticker = []
        outros = {"DOLFUT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "PETROLEO": "BZ=F"}
        for lbl, sym in outros.items():
            d = spot_live if lbl == "DOLFUT" else fetch(sym)
            var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
            p_val = d['at']/1000 if lbl == "DOLFUT" else d['at']
            html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{p_val:.4f}</td><td>{(d['cl']/1000 if lbl=='DOLFUT' else d['cl']):.4f}</td><td>{(d['mx']/1000 if lbl=='DOLFUT' else d['mx']):.4f}</td><td>{(d['mn']/1000 if lbl=='DOLFUT' else d['mn']):.4f}</td><td style='color:{("#00ff00" if var >= 0 else "#ff4d4d")};'>{var:+.2f}%</td></tr>"
            ticker.append(f"{lbl}: {var:+.2f}%")
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        # PAINEL DE ALVOS
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>50% Alta</span> <span>{res['p50_up']:.2f}</span></div><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {a_dol:.2f}</div><div class="calc-row" style="color:#ffa500;"><span>50% Baixa</span> <span>{res['p50_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
        
        # PAINEL DE DADOS
        st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff;">{res['medio']:.2f}</span></div><div class="calc-row"><span style="color:#ff4d4d;">SPREED</span> <span style="color:#00f2ff;">{res['spreed']:.2f}</span></div><div class="ewz-mini-container"><span class="ewz-mini-val" style="color:#00ff88;">{ewz_live['mx']:.2f}</span><span class="ewz-mini-val" style="color:#00f2ff;">{res['ewz_med']:.2f}</span><span class="ewz-mini-val" style="color:#ff4d4d;">{ewz_live['mn']:.2f}</span></div></div>""", unsafe_allow_html=True)

        # BARRA E SETA FORA DOS BLOCOS (ABAIXO)
        st.markdown(f"""
        <div class="bar-wrapper">
            <div class="label-row"><span style="color:#00ff88;">EXAUST</span><span style="color:#fff;">AXIS</span><span style="color:#ff4d4d;">EXAUST</span></div>
            <div class="force-container-dual">
                <div class="center-line"></div>
                <div class="bar-side"><div class="fill-green" style="width: {res['pct_v']}%;"></div></div>
                <div class="bar-side"><div class="fill-red" style="width: {res['pct_r']}%;"></div></div>
            </div>
            <div class="sinal-indicator blink" style="color:{res['seta_cor']};">{res['seta']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker)}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
