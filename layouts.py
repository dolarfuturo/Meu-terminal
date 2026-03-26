import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- CSS: VOLTANDO PARA O TAMANHO QUE ESTAVA CERTO (COMPACTO) ---
st.markdown("""
<style>
    /* Layout solto no topo para não cortar o nome */
    .block-container { padding-top: 2rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; }
    .stApp { background-color: #050a0e !important; }
    
    /* CABEÇALHO COMPACTO */
    .header-container { text-align: center; padding: 5px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 10px; }
    .main-title { margin: 0px; line-height: 1.0; font-size: 28px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    
    /* RELÓGIOS 11px */
    .clock-row { display: flex; justify-content: center; gap: 20px; padding: 5px 0; font-weight: bold; font-size: 11px; font-family: monospace; }
    .br-green { color: #00ff00; }
    .white-time { color: #ffffff; }

    /* FAIXAS DE TÍTULO 11px */
    .section-title { 
        border: 1px solid #ffffff; 
        color: #00f2ff; 
        text-align: center; 
        font-weight: bold; 
        font-family: monospace; 
        padding: 4px; 
        margin-bottom: 6px; 
        text-transform: uppercase;
        font-size: 11px;
    }

    /* GRADE PRINCIPAL (VOLTANDO PARA 11px e 13px) */
    .main-grid { border: 1.5px solid #ffffff; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 11px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 13px; }
    .asset-name { font-size: 13px; color: #fff; text-align: left; font-weight: bold; padding-left: 10px !important; }

    /* PAINÉIS LATERAIS COMPACTOS COM TODOS OS DADOS */
    .calc-panel { border: 1.5px solid #ffffff; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 3px 6px; border-bottom: 1px solid #444; font-size: 11px; font-weight: bold; }
    
    /* BARRA DE FORÇA COMPACTA */
    .bar-wrapper-dual { background: #0a141a; padding: 8px 6px 4px 6px; border: 1.5px solid #ffffff; text-align: center; }
    .force-container-dual { background: #111; height: 12px; width: 100%; position: relative; display: flex; border: 1px solid #444; margin: 2px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; }
    .fill-green { background: #00ff88; float: right; height: 100%; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; }
    .sinal-indicator { font-size: 13px; font-weight: 900; margin-top: 4px; }

    .ticker-wrapper { background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 4px 0; margin-top: 8px; overflow: hidden; }
    .ticker-text { font-size: 11px; font-family: monospace; color: #fff; white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (PRESERVADAS) ---
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
        max_fut = spot_data['mx'] + v_spreed
        p75_up, p25_up = max_fut - v_spreed, eixo_dol + v_spreed
        p25_down, p75_down = eixo_dol - v_spreed, (spot_data['mn'] + v_spreed) + v_spreed
        min_fut = spot_data['mn'] + v_spreed
        dist_base = abs(eixo_dol - dolar_medio)
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = 0, 0
        if dist_base > 0:
            if diff < 0: p_v = min(100, (abs(diff)/(dist_base*2))*100)
            else: p_r = min(100, (abs(diff)/(dist_base*2))*100)
        seta = "▲ COMPRA" if p_v > 80 else "▼ VENDA" if p_r > 80 else "AGUARDAR"
        seta_cor = "#00ff88" if p_v > 80 else "#ff4d4d" if p_r > 80 else "#ffffff"
        return {"vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, "max_fut": max_fut, "min_fut": min_fut, 
                "p75_up": p75_up, "p25_up": p25_up, "p25_down": p25_down, "p75_down": p75_down,
                "v_v": v_final * 100, "spreed": v_spreed, "p_v": p_v, "p_r": p_r, "seta": seta, "seta_cor": seta_cor}
    except: return None

# --- SIDEBAR ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")

placeholder = st.empty()

while True:
    tz_sp, tz_ny = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York')
    ewz_live = fetch("EWZ")
    spot_live = fetch("USDBRL=X")
    res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol, spot_live)
    now = datetime.now()

    with placeholder.container():
        st.markdown(f'<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span> <span class="terminal-gold">- TERMINAL DOLLAR</span></h1><div class="clock-row"><span>🇧🇷 BRASÍLIA: <span class="br-green">{now.astimezone(tz_sp).strftime("%H:%M:%S")}</span></span><span>🇺🇸 NY: <span class="white-time">{now.astimezone(tz_ny).strftime("%H:%M:%S")}</span></span></div></div>', unsafe_allow_html=True)

        if res:
            c_main, c_side = st.columns([3.2, 0.8])
            with c_main:
                st.markdown('<div class="section-title">GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                outros = {"DOLFUT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "EUR/USD": "EURUSD=X", "PETROLEO": "BZ=F"}
                for lbl, sym in outros.items():
                    d = spot_live if lbl == "DOLFUT" else fetch(sym)
                    var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                    p_val = d['at']/1000 if lbl == "DOLFUT" else d['at']
                    bg = "rgba(0,255,0,0.3)" if var >= 0 else "rgba(255,0,0,0.3)"
                    html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col' style='background:{bg}'>{p_val:.4f if lbl=='DOLFUT' else p_val:.2f}</td><td>{d['cl']/1000 if lbl=='DOLFUT' else d['cl']:.2f}</td><td>{d['op']/1000 if lbl=='DOLFUT' else d['op']:.2f}</td><td>{d['mx']/1000 if lbl=='DOLFUT' else d['mx']:.2f}</td><td>{d['mn']/1000 if lbl=='DOLFUT' else d['mn']:.2f}</td><td style='color:{("#00ff00" if var>=0 else "#ff4d4d")}'>{var:+.2f}%</td></tr>"
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
            
            with c_side:
                st.markdown('<div class="section-title">PROJEÇÕES</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MAX</span> <span>{res["max_fut"]:.2f}</span></div><div class="calc-row"><span>75% UP</span> <span>{res["p75_up"]:.2f}</span></div><div class="calc-row"><span>25% UP</span> <span>{res["p25_up"]:.2f}</span></div><div style="text-align:center; padding:4px; color:#00f2ff; font-weight:bold; font-size:12px; border-top:1px solid #444;">AXIS: {a_dol:.2f}</div><div class="calc-row"><span>25% DN</span> <span>{res["p25_down"]:.2f}</span></div><div class="calc-row"><span>75% DN</span> <span>{res["p75_down"]:.2f}</span></div><div class="calc-row" style="color:#00ff88; border:none;"><span>MIN</span> <span>{res["min_fut"]:.2f}</span></div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="calc-panel"><div class="calc-row"><span>MÉDIA</span> <span>{res["medio"]:.2f}</span></div><div class="calc-row"><span>FRAJA</span> <span>{res["fraja"]:.2f}</span></div><div class="calc-row" style="border:none;"><span>SPREED</span> <span>{res["spreed"]:.2f}</span></div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bar-wrapper-dual"><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width:{res["p_v"]}%"></div></div><div class="bar-side"><div class="fill-red" style="width:{res["p_r"]}%"></div></div></div><div class="sinal-indicator" style="color:{res["seta_cor"]}">{res["seta"]}</div></div>', unsafe_allow_html=True)

    time.sleep(5)
