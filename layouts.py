import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: ALINHAMENTO SUPERIOR TOTAL E RODAPÉ DUPLO ---
st.markdown("""
<style>
    header[data-testid="stHeader"] { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .stApp { background-color: #050a0e !important; }
    
    /* Remove espaços que o Streamlit cria entre colunas e no topo */
    .block-container { padding: 0.5rem 1rem !important; }
    [data-testid="stVerticalBlock"] > div:first-child { margin-top: 0 !important; padding-top: 0 !important; }
    
    /* Grade Principal */
    .main-grid { border: 2.5px solid #ffffff; border-radius: 6px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 8px; text-align: center; font-size: 12px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12.5px; text-align: center; font-size: 14px; }
    .asset-name { font-size: 16px; color: #fff; text-align: left; font-weight: bold; padding-left: 12px; }

    /* Ajuste dos Blocos da Direita (Puxar para cima) */
    .right-column-align {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 0px !important; /* Garante que comece no topo */
    }
    .calc-panel { 
        border: 2.5px solid #ffffff; border-radius: 6px; background: #0a141a; 
        font-family: monospace; padding: 8px 5px;
    }
    .calc-row { display: flex; justify-content: space-between; padding: 6px 10px; border-bottom: 1px solid #333; font-size: 14px; font-weight: bold; }

    /* Relógios */
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 85px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 16px; font-weight: bold; }

    /* RODAPÉ DUPLO FIXO */
    .footer-fixed {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000; border-top: 2.5px solid #ffffff;
        z-index: 999; padding: 4px 0;
    }
    .ticker-line { overflow: hidden; white-space: nowrap; width: 100%; height: 22px; display: flex; align-items: center; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 50s linear infinite; font-family: 'monospace'; font-size: 13px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    .up { color: #00ff00 !important; }
    .down { color: #ff4d4d !important; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def get_data(s):
    try:
        t = yf.Ticker(s)
        h = t.history(period="1d", interval="1m", prepost=True)
        pc = t.info.get('previousClose', 0)
        if h.empty: return {"at": pc, "cl": pc, "mx": pc, "mn": pc, "op": pc}
        return {"at": h['Close'].iloc[-1], "cl": pc, "op": h['Open'].iloc[0], "mx": h['High'].max(), "mn": h['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calc_res(e_ewz, p_ewz, mx_e, mn_e, e_dol):
    try:
        v_at = ((e_ewz / p_ewz) - 1) * 100 / 1.5
        v_fr = ((e_ewz / p_ewz) - 1) * 100 / 4.5
        ewz_m = (mx_e + mn_e) / 2
        v_m = ((e_ewz / ewz_m) - 1) * 100
        v_neg = ((e_ewz / mx_e) - 1) * 100 / 1.5
        v_pos = ((e_ewz / mn_e) - 1) * 100 / 1.5
        mx_a, mn_a = e_dol * (1 + (v_pos / 100)), e_dol * (1 + (v_neg / 100))
        return {
            "vivo": e_dol * (1 + (v_at / 100)), "fraja": e_dol * (1 + (v_fr / 100)), "medio": e_dol * (1 + (v_m / 100)),
            "ewz_med": ewz_m, "max": mx_a, "min": mn_a,
            "p75_up": (e_dol + (mx_a - e_dol)*0.75), "p50_up": (e_dol + mx_a) / 2, 
            "p25_up": (e_dol + (mx_a - e_dol)*0.25), "p75_down": (e_dol + (mn_a - e_dol)*0.75), 
            "p50_down": (e_dol + mn_a) / 2, "p25_down": (e_dol + (mn_a - e_dol)*0.25)
        }
    except: return None

# --- SIDEBAR ADM ---
with st.sidebar:
    st.title("⚙️ CONFIGURAÇÃO")
    ax_ewz = st.number_input("AXIS EWZ", value=36.42, format="%.2f")
    ax_dol = st.number_input("AXIS DOLFUT", value=5274.0, format="%.2f")
    if st.button("RECARREGAR"): st.rerun()

# --- HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:2.5px solid #fff; margin-bottom:12px;">
    <div style="font-size:38px; font-weight:950; font-family:monospace;"><span style="color:#00f2ff;">BAIR</span><span style="color:#fff;"> - </span><span style="color:#d4a017;">TERMINAL DOLAR</span></div>
    <div style="display:flex; gap:10px;">
        <div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div>
    </div>
</div>""", unsafe_allow_html=True)

ewz_l = get_data("EWZ")
res = calc_res(ax_ewz, ewz_l['at'], ewz_l['mx'], ewz_l['mn'], ax_dol)

if res:
    c1, c2 = st.columns([3, 1])
    
    with c1:
        st.markdown('<div style="background:#0a141a; border:2px solid #fff; padding:4px; text-align:center; color:#00f2ff; font-weight:bold; margin-bottom:8px; font-size:11px;">GRADE PRINCIPAL</div>', unsafe_allow_html=True)
        h_tbl = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        ativos = {"DOLFUT": "BRL=X", "SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
        tick_list = []

        for label, sym in ativos.items():
            d = get_data(sym)
            var = ((d['at']/d['cl'])-1)*100 if d['cl'] > 0 else 0
            cor = "up" if var >= 0 else "down"
            h_tbl += f"<tr><td class='asset-name'>{label}</td><td style='color:#00f2ff; font-weight:bold;'>{d['at']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['op']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td class='{cor}'>{var:+.2f}%</td></tr>"
            tick_list.append(f"{label}: <span class='{cor}'>{var:+.2f}%</span>")
        
        st.markdown(h_tbl + "</tbody></table></div>", unsafe_allow_html=True)

    with c2:
        # Título alinhado com o da esquerda
        st.markdown('<div style="background:#0a141a; border:2px solid #fff; padding:4px; text-align:center; color:#00f2ff; font-weight:bold; margin-bottom:8px; font-size:11px;">PROJEÇÕES</div>', unsafe_allow_html=True)
        
        # Container que puxa tudo para cima
        st.markdown(f"""<div class="right-column-align">
            <div class="calc-panel">
                <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
                <div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div>
                <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
                <div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div>
                <div style="text-align:center; padding: 12px; color: #00f2ff; font-size: 19px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444;">AXIS: {ax_dol:.2f}</div>
                <div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div>
                <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
                <div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div>
                <div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
            </div>
            <div class="calc-panel">
                <div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
                <div class="calc-row"><span>MÉDIA DOL</span> <span style="color:#ffff00;">{res['medio']:.2f}</span></div>
                <div class="calc-row" style="border-bottom:none;"><span>P. JUSTO</span> <span style="color:#fff;">{res['fraja']:.2f}</span></div>
                <div style="display:flex; justify-content:space-around; padding-top:8px; border-top:1px solid #444; margin-top:5px;">
                    <span class="up" style="font-size:11px;">{ewz_l['mx']:.2f}</span>
                    <span style="color:#00f2ff; font-size:11px;">{res['ewz_med']:.2f}</span>
                    <span class="down" style="font-size:11px;">{ewz_l['mn']:.2f}</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # RODAPÉ DUPLO
    txt_f = " • ".join(tick_list)
    st.markdown(f"""
    <div class="footer-fixed">
        <div class="ticker-line"><div class="ticker-text">{txt_f} • {txt_f}</div></div>
        <div class="ticker-line" style="border-top: 1px solid #333;"><div class="ticker-text" style="animation-direction: reverse;">{txt_f} • {txt_f}</div></div>
    </div>""", unsafe_allow_html=True)

time.sleep(10)
st.rerun()
