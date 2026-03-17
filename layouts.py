import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR", initial_sidebar_state="collapsed")

# --- CSS: LIMPEZA TOTAL, STATUS OCULTO E BOTÃO ADM VISÍVEL ---
st.markdown("""
<style>
    /* 1. ESCONDE O STATUS "RUNNING" E A BARRA DE PROGRESSO */
    div[data-testid="stStatusWidget"] { display: none !important; }
    
    /* 2. ESCONDE ICONES DE FORK, ESTRELA E BONEQUINHO (TOOLBAR) */
    .stAppToolbar { visibility: hidden !important; }
    footer { visibility: hidden !important; }

    /* 3. FORÇA O BOTÃO DO MENU (SIDEBAR) A APARECER E FICAR POR CIMA */
    [data-testid="stHeader"] {
        background: transparent !important;
        height: 3rem;
    }
    
    /* Estiliza o botão do menu para ser visível no fundo escuro */
    button[data-testid="sidebar-button"] {
        visibility: visible !important;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        margin-left: 10px;
        z-index: 999999;
    }

    /* 4. ESTILO DO TERMINAL */
    .stApp { background-color: #050a0e !important; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }

    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; margin-top: -10px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; }
    
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    .monitor-bar { background: #0a141a; border: 2.2px solid #ffffff; padding: 6px; text-align: center; color: #00f2ff; font-weight: bold; font-size: 14px; border-radius: 4px; margin-bottom: 8px; }

    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (MANTIDAS) ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        ref_close = t.info.get('previousClose')
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        return {"at": d['Close'].iloc[-1], "cl": ref_close or d['Open'].iloc[0], "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97_total(eixo_ewz, p_ewz, mx_e, mn_e, eixo_dol):
    if p_ewz <= 0: return None
    v_at = ((eixo_ewz / p_ewz) - 1) * 100 / 1.5
    v_fr = ((eixo_ewz / p_ewz) - 1) * 100 / 4.5
    v_pos = ((eixo_ewz / mn_e) - 1) * 100 / 1.5 if mn_e > 0 else 0
    v_neg = ((eixo_ewz / mx_e) - 1) * 100 / 1.5 if mx_e > 0 else 0
    mx_d, mn_d = eixo_dol * (1 + (v_pos / 100)), eixo_dol * (1 + (v_neg / 100))
    return {
        "vivo": eixo_dol * (1 + (v_at / 100)), "fraja": eixo_dol * (1 + (v_fr / 100)),
        "max": mx_d, "min": mn_d, "ewz_med": (mx_e + mn_e) / 2,
        "p50_up": (eixo_dol + mx_d) / 2, "p50_down": (eixo_dol + mn_d) / 2
    }

# --- SIDEBAR (PAINEL ADM) ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    with st.form("ajuste"):
        a_ewz = st.number_input("AXIS EWZ:", value=36.42, format="%.2f")
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        st.form_submit_button("SALVAR")

# --- HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""
<div class="header-bair">
    <div class="title-box"><span class="bair-text">BAIR</span><span style="color:#fff; font-size:46px;">-</span><span class="terminal-text">TERMINAL DOLAR</span></div>
    <div style="display: flex; gap: 10px;">
        <div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

placeholder = st.empty()

while True:
    with placeholder.container():
        ewz_live = fetch("EWZ")
        res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol)
        
        c_main, c_side = st.columns([3, 1])
        with c_main:
            st.markdown('<div class="monitor-bar">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
            html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
            ticker_items = []
            ativos = {"DOLFUT": "BZ=F", "SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "XAU/USD": "GC=F"}
            for lbl, sym in ativos.items():
                d = fetch(sym)
                price = res['vivo'] if lbl == "DOLFUT" and res else d['at']
                close = a_dol if lbl == "DOLFUT" else d['cl']
                var = ((price / close) - 1) * 100 if close > 0 else 0
                color = "#00ff00" if var >= 0 else "#ff4d4d"
                fmt = ".4f" if "USD" in lbl or lbl == "SPOT" else ".2f"
                html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{price:{fmt}}</td><td>{close:{fmt}}</td><td>{d['op']:{fmt}}</td><td>{d['mx']:{fmt}}</td><td>{d['mn']:{fmt}}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
                ticker_items.append(f"<span style='color:#fff;'>{lbl}:</span> <span style='color:{color};'>{var:+.2f}%</span>")
            st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

        with c_side:
            st.markdown('<div class="monitor-bar">PROJEÇÕES</div>', unsafe_allow_html=True)
            if res:
                st.markdown(f"""
                <div class="calc-panel">
                    <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
                    <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
                    <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {a_dol:.2f}</div>
                    <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
                    <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
                </div>
                <div class="calc-panel">
                    <div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
                    <div class="calc-row" style="border-bottom:none;"><span>P. JUSTO</span> <span style="color:#ffffff; font-weight:bold;">{res['fraja']:.2f}</span></div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)} • {" • ".join(ticker_items)}</div></div>', unsafe_allow_html=True)

    time.sleep(5)
    st.rerun()
