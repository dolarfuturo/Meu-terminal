import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet/Site
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: ESTILIZAÇÃO COM SUPER ZOOM ---
st.markdown("""
<style>
    /* ZOOM GLOBAL MAIS AGRESSIVO */
    .stApp { 
        background-color: #050a0e !important; 
        zoom: 0.70; /* 70% do tamanho original */
        -moz-transform: scale(0.70);
        -moz-transform-origin: 0 0;
    }
    
    /* Zera margens externas do Streamlit para o site */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* Ajuste de tabelas para ocupar menos espaço vertical */
    .terminal-table th { 
        padding: 6px !important; 
        font-size: 12px !important; 
    }
    .terminal-table td { 
        padding: 8px !important; 
        font-size: 14px !important; 
    }
    
    .main-grid { border: 2px solid #ffffff; border-radius: 8px; background-color: #0d1b22; }
    .header-bair { padding: 5px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 8px; }
    .bair-text, .terminal-text { font-size: 40px !important; }
    
    .calc-panel { border: 2px solid #ffffff; padding: 6px; margin-bottom: 6px; }
    .calc-row { padding: 4px 6px; font-size: 12px; }
    
    /* Ajuste para o Ticker não criar barra de rolagem */
    .ticker-wrapper { width: 100%; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        ref_close = t.info.get('previousClose')
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: 
            return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        if not ref_close:
            hist_ref = t.history(period="2d")
            ref_close = hist_ref['Close'].iloc[-2] if len(hist_ref) > 1 else d['Open'].iloc[0]
        return {
            "at": d['Close'].iloc[-1], "cl": ref_close, "op": d['Open'].iloc[0],
            "mx": d['High'].max(), "mn": d['Low'].min()
        }
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

@st.cache_data(ttl=600)
def calcular_sentinela():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d")
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        idx = -2 if agora.hour < 18 else -1
        mx, mn = df['High'].iloc[idx], df['Low'].iloc[idx]
        return (mx + mn) / 2
    except: return 37.85

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        if p_ewz_atual == 0: return None
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 1.5
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 4.5
        dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
        ewz_medio_dia = (max_ewz + min_ewz) / 2
        var_medio = ((eixo_ewz / ewz_medio_dia) - 1) * 100 if ewz_medio_dia > 0 else 0
        dolar_medio = eixo_dol * (1 + (var_medio / 100)) 
        v_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 1.5 if max_ewz > 0 else 0
        v_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 1.5 if min_ewz > 0 else 0
        alvo_max, alvo_min = eixo_dol * (1 + (v_pos / 100)), eixo_dol * (1 + (v_neg / 100))
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, "ewz_med": ewz_medio_dia,
            "max": alvo_max, "min": alvo_min,
            "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), "p50_up": (eixo_dol + alvo_max) / 2, 
            "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25), "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), 
            "p50_down": (eixo_dol + alvo_min) / 2, "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
        }
    except: return None

# --- PAINEL ADM ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    with st.form("ajuste_vars"):
        a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        st.form_submit_button("SALVAR")

# --- UI HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text" style="color:#fff; font-size:40px;">-</span><span class="terminal-text">TERMINAL</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">BSB</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">NY</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">LDN</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

ewz_live = fetch("EWZ")
res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol)

if res:
    c_main, c_side = st.columns([2.8, 1.2]) # Ajuste leve na proporção das colunas
    with c_main:
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        v_v = ((res['vivo']/a_dol)-1)*100 if a_dol > 0 else 0
        html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{("#00ff00" if v_v >= 0 else "#ff4d4d")}; font-weight:bold;'>{v_v:+.2f}%</td></tr>"
        
        outros = {"SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "XAU/USD": "GC=F", "BRENT": "BZ=F"}
        for lbl, sym in outros.items():
            d = fetch(sym)
            f = ".4f" if "USD" in lbl or lbl == "SPOT" else ".2f"
            var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
            color = "#00ff00" if var >= 0 else "#ff4d4d"
            html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['op']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
        
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div><div style="text-align:center; padding: 8px; color: #00f2ff; font-size: 16px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 4px 0;">AXIS: {a_dol:.2f}</div><div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="padding: 8px 8px;"><span style="color:#ffffff;">DOLFUT</span> <span style="color:#00f2ff; font-size: 15px; font-weight: 950;">{res['vivo']:.2f}</span></div><div class="calc-row" style="border-bottom: none;"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#ffffff; font-size: 15px; font-weight: bold;">{res['fraja']:.2f}</span></div><div class="ewz-mini-container"><span class="ewz-mini-val" style="color:#00ff88;">{ewz_live['mx']:.2f}</span><span class="ewz-mini-val" style="color:#00f2ff;">{res['ewz_med']:.2f}</span><span class="ewz-mini-val" style="color:#ff4d4d;">{ewz_live['mn']:.2f}</span></div></div>""", unsafe_allow_html=True)

time.sleep(5)
st.rerun()
