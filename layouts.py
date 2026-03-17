import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: AJUSTES DE POSICIONAMENTO E COMPRESSÃO ---
st.markdown("""
<style>
    /* 1. ESCONDE ELEMENTOS PADRÃO */
    header[data-testid="stHeader"] { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }
    
    /* 2. BOTÃO ADM CUSTOMIZADO (SUBSTITUI O ORIGINAL QUE SOME) */
    .st-emotion-cache-hp888a { display: none !important; } /* Esconde o botão original quebrado */
    
    /* 3. ESTILOS GERAIS E COMPRESSÃO */
    .stApp { background-color: #050a0e !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; }
    
    /* BLOCO DE PROJEÇÕES COMPACTADO */
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 6px; background: #0a141a; font-family: monospace; margin-bottom: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 3px 8px; border-bottom: 1px solid #444; font-size: 12px; font-weight: bold; }
    
    /* RODAPÉ COLADO */
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 6px 0; overflow: hidden; white-space: nowrap; margin-top: 5px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    
    .monitor-bar { background: #0a141a; border: 2.2px solid #ffffff; padding: 4px; text-align: center; color: #00f2ff; font-weight: bold; font-size: 13px; border-radius: 4px; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# --- BOTÃO ADM MANUAL ---
if st.button("⚙️ PAINEL ADM"):
    st.info("Ajuste os valores na barra lateral à esquerda.")

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        ref_close = t.info.get('previousClose')
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        if not ref_close:
            hist_ref = t.history(period="2d")
            ref_close = hist_ref['Close'].iloc[-2] if len(hist_ref) > 1 else d['Open'].iloc[0]
        return {"at": d['Close'].iloc[-1], "cl": ref_close, "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

@st.cache_data(ttl=600)
def calcular_sentinela():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d")
        idx = -2 if datetime.now(pytz.timezone('America/Sao_Paulo')).hour < 18 else -1
        return (df['High'].iloc[idx] + df['Low'].iloc[idx]) / 2
    except: return 37.85

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        if p_ewz_atual == 0: return None
        v_at = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 1.5
        v_fr = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 4.5
        ewz_med = (max_ewz + min_ewz) / 2
        v_med = ((eixo_ewz / ewz_med) - 1) * 100 if ewz_med > 0 else 0
        v_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 1.5 if max_ewz > 0 else 0
        v_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 1.5 if min_ewz > 0 else 0
        alvo_max, alvo_min = eixo_dol * (1 + (v_pos / 100)), eixo_dol * (1 + (v_neg / 100))
        return {
            "vivo": eixo_dol * (1 + (v_at / 100)), "fraja": eixo_dol * (1 + (v_fr / 100)),
            "medio": eixo_dol * (1 + (v_med / 100)), "ewz_med": ewz_med, "max": alvo_max, "min": alvo_min,
            "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), "p50_up": (eixo_dol + alvo_max) / 2, 
            "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25), "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), 
            "p50_down": (eixo_dol + alvo_min) / 2, "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
        }
    except: return None

# --- SIDEBAR ADM ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    st.header("⚙️ CONFIGURAÇÕES")
    a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")

# --- HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span style="color:#fff; font-size:46px;"> - </span><span class="terminal-text">TERMINAL DOLAR</span></div><div style="display:flex; gap:10px;"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

ewz_live = fetch("EWZ")
res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol)

if res:
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown('<div class="monitor-bar">GRADE PRINCIPAL DE ATIVOS</div>', unsafe_allow_html=True)
        html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        # DOLFUT
        v_v = ((res['vivo']/a_dol)-1)*100
        html += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{("#00ff00" if v_v >= 0 else "#ff4d4d")}; font-weight:bold;'>{v_v:+.2f}%</td></tr>"
        
        ticker = [f"DOLFUT: {v_v:+.2f}%"]
        outros = {"SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "XAU/USD": "GC=F"}
        for lbl, sym in outros.items():
            d = fetch(sym); var = ((d['at']/d['cl'])-1)*100; color = "#00ff00" if var >= 0 else "#ff4d4d"
            f = ".4f" if "USD" in lbl or lbl == "SPOT" else ".2f"
            html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['op']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
            ticker.append(f"{lbl}: {var:+.2f}%")
        st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="monitor-bar">PROJEÇÕES</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
            <div style="text-align:center; padding: 5px; color: #00f2ff; font-size: 16px; font-weight: bold; border-top:1px solid #444; border-bottom:1.5px solid #444; margin: 4px 0;">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)
        
        # BLOCO COMPRIMIDO (ALINHADO COM A GRADE)
        st.markdown(f"""<div class="calc-panel" style="margin-top: -2px;">
            <div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
            <div class="calc-row"><span>MÉDIA DOL</span> <span style="color:#ffff00;">{res['medio']:.2f}</span></div>
            <div class="calc-row" style="border-bottom:none;"><span>P. JUSTO</span> <span style="color:#fff;">{res['fraja']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)

    # RODAPÉ COLADO
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker)} • {" • ".join(ticker)}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
