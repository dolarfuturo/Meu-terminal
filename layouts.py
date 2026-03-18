import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="expanded")

# --- CSS: ESTILIZAÇÃO E REMOÇÃO TOTAL DE STATUS (BONEQUINHO) ---
st.markdown("""
<style>
    /* OCULTA O BONEQUINHO E A BARRA DE STATUS */
    [data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container { padding-top: 1rem !important; }

    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .sep-text { font-size: 46px; color: #ffffff; font-weight: 950; margin: 0 5px; }
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    .clock-container { display: flex; gap: 10px; color: #888; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; margin-bottom: 2px; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'exibir_adm' not in st.session_state: st.session_state.exibir_adm = False
if 'a_ewz' not in st.session_state: st.session_state.a_ewz = 37.85
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        f = t.fast_info
        return {"at": f['last_price'], "cl": f['previous_close'], "op": f['open'], "mx": f['day_high'], "mn": f['day_low']}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97(e_ewz, p_ewz, mx_e, mn_e, e_dol):
    try:
        if p_ewz <= 0: return None
        v_at = ((e_ewz / p_ewz) - 1) * 100 / 1.5
        v_fr = ((e_ewz / p_ewz) - 1) * 100 
        e_med = (mx_e + mn_e) / 2
        v_me = ((p_ewz / e_med) - 1) * 100 if e_med > 0 else 0
        v_ng = ((e_ewz / mx_e) - 1) * 100 / 1.5 if mx_e > 0 else 0
        v_ps = ((e_ewz / mn_e) - 1) * 100 / 1.5 if mn_e > 0 else 0
        al_mx, al_mn = e_dol * (1 + (v_ps / 100)), e_dol * (1 + (v_ng / 100))
        return {
            "vivo": e_dol * (1 + (v_at / 100)), "fraja": e_dol * (1 + (v_fr / 100)), "medio": e_dol * (1 + (v_me / 100)), 
            "ewz_med": e_med, "max": al_mx, "min": al_mn,
            "p75_up": (e_dol + (al_mx - e_dol)*0.75), "p50_up": (e_dol + al_mx) / 2, "p25_up": (e_dol + (al_mx - e_dol)*0.25),
            "p75_down": (e_dol + (al_mn - e_dol)*0.75), "p50_down": (e_dol + al_mn) / 2, "p25_down": (e_dol + (al_mn - e_dol)*0.25)
        }
    except: return None

# --- SIDEBAR: BOTÃO SET ADM ---
with st.sidebar:
    st.markdown("### ⚙️ SETTINGS")
    if st.button("🔓 ACESSAR PAINEL ADM"):
        st.session_state.exibir_adm = not st.session_state.exibir_adm
    
    if st.session_state.exibir_adm:
        st.markdown("---")
        with st.form("form_adm"):
            st.session_state.a_ewz = st.number_input("AXIS EWZ:", value=st.session_state.a_ewz, format="%.2f")
            st.session_state.a_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol, format="%.2f")
            if st.form_submit_button("SALVAR E FECHAR"):
                st.session_state.exibir_adm = False
                st.rerun()

# --- TERMINAL LOOP ---
placeholder = st.empty()

while True:
    tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
    ewz_d = fetch("EWZ")
    res = calcular_k97(st.session_state.a_ewz, ewz_d['at'], ewz_d['mx'], ewz_d['mn'], st.session_state.a_dol)

    if res:
        with placeholder.container():
            st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M:%S')}</span></div><div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M:%S')}</span></div><div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M:%S')}</span></div></div></div>""", unsafe_allow_html=True)

            c_m, c_s = st.columns([3, 1])
            with c_m:
                v_v = ((res['vivo']/st.session_state.a_dol)-1)*100
                cor_v = "#00ff00" if v_v >= 0 else "#ff4d4d"
                table = f"""<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>
                <tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(st.session_state.a_dol/1000):.4f}</td><td>{(st.session_state.a_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{cor_v}; font-weight:bold;'>{v_v:+.2f}%</td></tr>"""
                
                ticker = [f"<span style='color:#fff;'>DOLFUT:</span> <span style='color:{cor_v};'>{v_v:+.2f}%</span>"]
                outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "BRENT": "BZ=F"}
                
                for lbl, sym in outros.items():
                    d = fetch(sym)
                    var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                    color = "#00ff00" if var >= 0 else "#ff4d4d"
                    table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['op']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
                    ticker.append(f"<span style='color:#fff;'>{lbl}:</span> <span style='color:{color};'>{var:+.2f}%</span>")
                st.markdown(table + "</tbody></table></div>", unsafe_allow_html=True)

            with c_s:
                st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {st.session_state.a_dol:.2f}</div><div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="padding: 10px 8px;"><span style="color:#ffffff;">DOLFUT</span> <span style="color:#00f2ff; font-size: 16px; font-weight: 950;">{res['vivo']:.2f}</span></div><div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff; font-size: 16px;">{res['medio']:.2f}</span></div><div class="calc-row" style="border-bottom: none;"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#ffffff; font-size: 16px; font-weight: bold;">{res['fraja']:.2f}</span></div><div style="display: flex; justify-content: space-around; padding: 4px 0; border-top: 1px solid #444; margin-top: 4px;"><span style="font-size: 11px; font-weight: bold; color:#00ff88;">{ewz_d['mx']:.2f}</span><span style="font-size: 11px; font-weight: bold; color:#00f2ff;">{res['ewz_med']:.2f}</span><span style="font-size: 11px; font-weight: bold; color:#ff4d4d;">{ewz_d['mn']:.2f}</span></div></div>""", unsafe_allow_html=True)

            st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker)} • {" • ".join(ticker)}</div></div>', unsafe_allow_html=True)

    time.sleep(1)
