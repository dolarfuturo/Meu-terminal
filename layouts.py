import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS DEFINITIVO: ALINHAMENTO E CORES ---
st.markdown("""
<style>
    header[data-testid="stHeader"] { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .stApp { background-color: #050a0e !important; }
    .block-container { padding-top: 0rem !important; }

    /* Estilo da Grade Principal */
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 11px; text-align: center; font-size: 14px; }
    .asset-name { font-size: 16px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }

    /* Ajuste dos Blocos da Direita para alinhar com a esquerda */
    .right-container { display: flex; flex-direction: column; height: 100%; gap: 10px; }
    .calc-panel { 
        border: 2.5px solid #ffffff; border-radius: 8px; background: #0a141a; 
        font-family: monospace; display: flex; flex-direction: column; justify-content: space-between;
        padding: 10px 5px;
    }
    .proj-height { min-height: 400px; } /* Ajuste fino da altura das projeções */
    .info-height { min-height: 165px; } /* Ajuste fino do bloco de baixo */
    
    .calc-row { display: flex; justify-content: space-between; padding: 5px 10px; border-bottom: 1px solid #333; font-size: 13px; font-weight: bold; }

    /* Rodapé com Cores */
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; color: white; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .up { color: #00ff00 !important; }
    .down { color: #ff4d4d !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (CORRIGIDAS) ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        h = t.history(period="1d", interval="1m", prepost=True)
        ref = t.info.get('previousClose', 0)
        if h.empty: return {"at": ref, "cl": ref, "mx": ref, "mn": ref, "op": ref}
        return {"at": h['Close'].iloc[-1], "cl": ref, "op": h['Open'].iloc[0], "mx": h['High'].max(), "mn": h['Low'].min()}
    except:
        return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97(e_ewz, p_ewz, mx_e, mn_e, e_dol):
    try:
        v_at = ((e_ewz / p_ewz) - 1) * 100 / 1.5
        v_fr = ((e_ewz / p_ewz) - 1) * 100 / 4.5
        ewz_m = (mx_e + mn_e) / 2
        v_m = ((e_ewz / ewz_m) - 1) * 100
        v_neg = ((e_ewz / mx_e) - 1) * 100 / 1.5
        v_pos = ((e_ewz / mn_e) - 1) * 100 / 1.5
        a_max, a_min = e_dol * (1 + (v_pos / 100)), e_dol * (1 + (v_neg / 100))
        return {
            "vivo": e_dol * (1 + (v_at / 100)), "fraja": e_dol * (1 + (v_fr / 100)), "medio": e_dol * (1 + (v_m / 100)),
            "ewz_med": ewz_m, "max": a_max, "min": a_min,
            "p75_up": (e_dol + (a_max - e_dol)*0.75), "p50_up": (e_dol + a_max) / 2, 
            "p25_up": (e_dol + (a_max - e_dol)*0.25), "p75_down": (e_dol + (a_min - e_dol)*0.75), 
            "p50_down": (e_dol + a_min) / 2, "p25_down": (e_dol + (a_min - e_dol)*0.25)
        }
    except: return None

# --- SIDEBAR ADM ---
with st.sidebar:
    st.header("⚙️ CONFIGURAÇÃO AXIS")
    a_ewz = st.number_input("AXIS EWZ", value=36.42, step=0.01)
    a_dol = st.number_input("AXIS DOLFUT", value=5274.00, step=1.0)
    if st.button("RECARREGAR"): st.rerun()

# --- HEADER ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div style="display:flex; justify-content:space-between; align-items:center; padding:10px; border-bottom:2.5px solid #fff; margin-bottom:10px;">
    <div style="font-size:38px; font-weight:950; font-family:monospace;"><span style="color:#00f2ff;">BAIR</span><span style="color:#fff;"> - </span><span style="color:#d4a017;">TERMINAL DOLAR</span></div>
    <div style="border:1.5px solid #fff; padding:5px 15px; background:#0a141a; text-align:center;">
        <div style="color:#d4a017; font-size:10px; font-weight:bold;">BRASÍLIA</div>
        <div style="color:#fff; font-size:18px; font-weight:bold;">{datetime.now(tz_sp).strftime('%H:%M')}</div>
    </div>
</div>""", unsafe_allow_html=True)

ewz_d = fetch("EWZ")
res = calcular_k97(a_ewz, ewz_d['at'], ewz_d['mx'], ewz_d['mn'], a_dol)

if res:
    col1, col2 = st.columns([3.2, 1])
    
    with col1:
        st.markdown('<div style="background:#0a141a; border:2px solid #fff; padding:5px; text-align:center; color:#00f2ff; font-weight:bold; margin-bottom:8px; font-size:12px;">GRADE PRINCIPAL DE ATIVOS</div>', unsafe_allow_html=True)
        html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        ativos = {"DOLFUT": "BRL=X", "SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
        ticker_list = []

        for lbl, sym in ativos.items():
            d = fetch(sym)
            var = ((d['at']/d['cl'])-1)*100 if d['cl'] > 0 else 0
            cls = "up" if var >= 0 else "down"
            html += f"<tr><td class='asset-name'>{lbl}</td><td style='color:#00f2ff; font-weight:bold;'>{d['at']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['op']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td class='{cls}'>{var:+.2f}%</td></tr>"
            ticker_list.append(f"{lbl}: <span class='{cls}'>{var:+.2f}%</span>")
        
        st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="background:#0a141a; border:2px solid #fff; padding:5px; text-align:center; color:#00f2ff; font-weight:bold; margin-bottom:8px; font-size:12px;">PROJEÇÕES</div>', unsafe_allow_html=True)
        # Painel Superior
        st.markdown(f"""<div class="calc-panel proj-height">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div>
            <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1px solid #444; border-bottom:1px solid #444;">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)
        
        # Painel Inferior
        st.markdown(f"""<div class="calc-panel info-height">
            <div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
            <div class="calc-row"><span>MÉDIA DOL</span> <span style="color:#ffff00;">{res['medio']:.2f}</span></div>
            <div class="calc-row" style="border-bottom:none;"><span>P. JUSTO</span> <span style="color:#fff;">{res['fraja']:.2f}</span></div>
            <div style="display:flex; justify-content:space-around; padding-top:8px; border-top:1px solid #444;">
                <span class="up" style="font-size:11px;">{ewz_d['mx']:.2f}</span>
                <span style="color:#00f2ff; font-size:11px;">{res['ewz_med']:.2f}</span>
                <span class="down" style="font-size:11px;">{ewz_d['mn']:.2f}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # RODAPÉ COLORIDO
    ticker_html = " • ".join(ticker_list)
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{ticker_html} • {ticker_html}</div></div>', unsafe_allow_html=True)

time.sleep(10)
st.rerun()
