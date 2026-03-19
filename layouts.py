import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- CSS: ESTILIZAÇÃO ---
st.markdown("""
<style>
    [data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container { padding-top: 0.5rem !important; }

    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    
    /* Alinhamento do Título e Botão */
    .title-wrapper { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; }
    .bair-text { font-size: 42px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 42px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    
    .clock-container { display: flex; gap: 8px; color: #888; font-family: 'monospace'; justify-content: flex-end; padding-top: 10px; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 8px; border-radius: 4px; background: #0a141a; min-width: 90px; }
    .clock-label { font-size: 9px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; }
    .clock-time { color: #fff; font-size: 16px; font-weight: bold; display: block; }
    
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
    
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    
    /* Estilo do botão SET */
    div.stButton > button {
        background-color: #0a141a !important;
        color: #d4a017 !important;
        border: 1px solid #d4a017 !important;
        font-weight: bold !important;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- ESTADOS ---
if 'exibir_adm' not in st.session_state: st.session_state.exibir_adm = False
if 'a_ewz' not in st.session_state: st.session_state.a_ewz = 37.85
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00

def fetch(s):
    try:
        t = yf.Ticker(s)
        f = t.fast_info
        # Proteção contra dados vazios
        price = f['last_price'] if f['last_price'] is not None else 0.0
        close = f['previous_close'] if f['previous_close'] is not None else price
        return {
            "at": price, 
            "cl": close, 
            "op": f.get('open', price), 
            "mx": f.get('day_high', price), 
            "mn": f.get('day_low', price)
        }
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

placeholder = st.empty()

while True:
    tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
    ewz_d = fetch("EWZ")
    res = calcular_k97(st.session_state.a_ewz, ewz_d['at'], ewz_d['mx'], ewz_d['mn'], st.session_state.a_dol)

    if res:
        with placeholder.container():
            # Cabeçalho com Botão SET ao lado
            h_col1, h_col2, h_col3 = st.columns([3, 0.5, 3])
            
            with h_col1:
                st.markdown(f'<div class="title-wrapper"><span class="bair-text">BAIR</span><span style="color:white; font-size:42px;">-</span><span class="terminal-text">TERMINAL</span></div>', unsafe_allow_html=True)
            
            with h_col2:
                if st.button("SET ⚙️"):
                    st.session_state.exibir_adm = not st.session_state.exibir_adm

            with h_col3:
                st.markdown(f"""<div class="clock-container"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M:%S')}</span></div><div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M:%S')}</span></div><div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M:%S')}</span></div></div>""", unsafe_allow_html=True)

            st.markdown('<hr style="border: 1.2px solid white; margin-top: -10px; margin-bottom: 10px;">', unsafe_allow_html=True)

            if st.session_state.exibir_adm:
                with st.expander("AJUSTE DE VARIÁVEIS", expanded=True):
                    with st.form("adm_form"):
                        st.session_state.a_ewz = st.number_input("AXIS EWZ:", value=st.session_state.a_ewz, format="%.2f")
                        st.session_state.a_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol, format="%.2f")
                        if st.form_submit_button("APLICAR"):
                            st.session_state.exibir_adm = False
                            st.rerun()

            # --- CORPO DO TERMINAL ---
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
                    # Verifica se d['at'] é número para evitar o erro da imagem
                    p = d['at'] if isinstance(d['at'], (int, float)) else 0.0
                    cl = d['cl'] if isinstance(d['cl'], (int, float)) else p
                    var = ((p / cl) - 1) * 100 if cl > 0 else 0
                    color = "#00ff00" if var >= 0 else "#ff4d4d"
                    
                    table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{p:.4f}</td><td>{cl:.4f}</td><td>{d['op']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
                    ticker.append(f"<span style='color:#fff;'>{lbl}:</span> <span style='color:{color};'>{var:+.2f}%</span>")
                
                st.markdown(table + "</tbody></table></div>", unsafe_allow_html=True)

            with c_s:
                st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {st.session_state.a_dol:.2f}</div><div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="padding: 10px 8px;"><span style="color:#ffffff;">DOLFUT</span> <span style="color:#00f2ff; font-size: 16px; font-weight: 950;">{res['vivo']:.2f}</span></div><div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff; font-size: 16px;">{res['medio']:.2f}</span></div><div class="calc-row" style="border-bottom: none;"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#ffffff; font-size: 16px; font-weight: bold;">{res['fraja']:.2f}</span></div></div>""", unsafe_allow_html=True)

            st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker)} • {" • ".join(ticker)}</div></div>', unsafe_allow_html=True)

    time.sleep(1)
