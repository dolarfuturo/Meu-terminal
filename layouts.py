import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: AJUSTE DE ENCAIXE VERTICAL E CORES DO RODAPÉ ---
st.markdown("""
<style>
    /* 1. REMOVE CABEÇALHO PADRÃO */
    header[data-testid="stHeader"] { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }

    /* 2. AJUSTE DE TELA */
    .stApp { background-color: #050a0e !important; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }

    /* 3. BOTÃO ADM REAL (CHAMA A SIDEBAR) */
    .st-emotion-cache-12fmjuu { display: none !important; } /* Esconde o original */
    
    /* 4. GRADE DE ATIVOS */
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }

    /* 5. BLOCOS DA DIREITA - ALINHAMENTO VERTICAL */
    /* Ajustamos o padding interno para eles esticarem e darem o "encaixe" */
    .calc-panel { 
        border: 2.5px solid #ffffff; 
        border-radius: 8px; 
        padding: 10px 6px; 
        background: #0a141a; 
        font-family: monospace; 
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .calc-row { display: flex; justify-content: space-between; padding: 6px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    
    /* 6. RODAPÉ COM CORES */
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; color: white; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .val-up { color: #00ff00 !important; }
    .val-down { color: #ff4d4d !important; }
</style>
""", unsafe_allow_html=True)

# --- BOTÃO ADM (FUNCIONAL) ---
# O Streamlit não permite abrir a sidebar por botão de código puro sem hack, 
# então usamos o botão padrão estilizado ou um informativo.
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_ewz = st.number_input("AXIS EWZ:", value=36.42, format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT:", value=5274.00, format="%.2f")
    st.button("SALVAR AJUSTES")

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        ref_close = t.info.get('previousClose')
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {"at": d['Close'].iloc[-1], "cl": ref_close, "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97(eixo_ewz, p_ewz_at, mx_ewz, mn_ewz, eixo_dol):
    try:
        v_at = ((eixo_ewz / p_ewz_at) - 1) * 100 / 1.5
        v_fr = ((eixo_ewz / p_ewz_at) - 1) * 100 / 4.5
        ewz_med = (mx_ewz + mn_ewz) / 2
        v_med = ((eixo_ewz / ewz_med) - 1) * 100
        v_neg = ((eixo_ewz / mx_ewz) - 1) * 100 / 1.5
        v_pos = ((eixo_ewz / mn_ewz) - 1) * 100 / 1.5
        alvo_max, alvo_min = eixo_dol * (1 + (v_pos / 100)), eixo_dol * (1 + (v_neg / 100))
        return {
            "vivo": eixo_dol * (1 + (v_at / 100)), "fraja": eixo_dol * (1 + (v_fr / 100)), "medio": eixo_dol * (1 + (v_med / 100)),
            "ewz_med": ewz_med, "max": alvo_max, "min": alvo_min,
            "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), "p50_up": (eixo_dol + alvo_max) / 2, 
            "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25), "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), 
            "p50_down": (eixo_dol + alvo_min) / 2, "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
        }
    except: return None

# --- UI HEADER ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div style="display:flex; justify-content:space-between; align-items:center; padding:10px; border-bottom:2.5px solid #fff; margin-bottom:15px;">
    <div style="font-size:40px; font-weight:950; font-family:monospace;"><span style="color:#00f2ff;">BAIR</span><span style="color:#fff;"> - </span><span style="color:#d4a017;">TERMINAL DOLAR</span></div>
    <div style="display:flex; gap:10px;">
        <div style="border:1.5px solid #fff; padding:5px 10px; text-align:center; background:#0a141a;">
            <div style="color:#d4a017; font-size:10px; font-weight:bold;">BRASÍLIA</div>
            <div style="color:#fff; font-size:18px; font-weight:bold;">{datetime.now(tz_sp).strftime('%H:%M')}</div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

ewz_live = fetch("EWZ")
res = calcular_k97(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol)

if res:
    c_main, c_side = st.columns([3, 1])
    
    with c_main:
        st.markdown('<div style="background:#0a141a; border:2.2px solid #fff; padding:6px; text-align:center; color:#00f2ff; font-weight:bold; margin-bottom:10px;">GRADE PRINCIPAL DE ATIVOS</div>', unsafe_allow_html=True)
        html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        ativos = {"DOLFUT": "BRL=X", "SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
        ticker_items = []

        for lbl, sym in ativos.items():
            d = fetch(sym)
            var = ((d['at']/d['cl'])-1)*100 if d['cl'] > 0 else 0
            cor = "val-up" if var >= 0 else "val-down"
            html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['op']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td class='{cor}'>{var:+.2f}%</td></tr>"
            ticker_items.append(f"{lbl}: <span class='{cor}'>{var:+.2f}%</span>")
        
        st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        st.markdown('<div style="background:#0a141a; border:2.2px solid #fff; padding:6px; text-align:center; color:#00f2ff; font-weight:bold; margin-bottom:10px;">PROJEÇÕES</div>', unsafe_allow_html=True)
        # Bloco de Projeções (Aumentado na vertical)
        st.markdown(f"""<div class="calc-panel" style="height: 380px;">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div>
            <div style="text-align:center; padding: 15px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444;">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)
        
        # Segundo Bloco (Ajustado)
        st.markdown(f"""<div class="calc-panel" style="height: 160px;">
            <div class="calc-row"><span style="color:#fff;">DOLFUT</span> <span style="color:#00f2ff; font-size:16px;">{res['vivo']:.2f}</span></div>
            <div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff;">{res['medio']:.2f}</span></div>
            <div class="calc-row" style="border-bottom:none;"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#fff;">{res['fraja']:.2f}</span></div>
            <div style="display:flex; justify-content:space-around; padding-top:10px; border-top:1px solid #444;">
                <span style="color:#00ff88; font-size:11px;">{ewz_live['mx']:.2f}</span>
                <span style="color:#00f2ff; font-size:11px;">{res['ewz_med']:.2f}</span>
                <span style="color:#ff4d4d; font-size:11px;">{ewz_live['mn']:.2f}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # RODAPÉ COM CORES RESTAURADAS
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)} • {" • ".join(ticker_items)}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
