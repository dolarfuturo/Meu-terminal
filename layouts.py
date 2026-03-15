import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL K97")

# --- CSS: ESTILO LARANJA + RELÓGIOS + MARQUEE ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2px solid #1c3d4d; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #1c3d4d; padding: 10px; text-align: center; font-size: 13px; }
    .terminal-table td { border: 1px solid #1c3d4d; padding: 12px; text-align: center; font-size: 15px; }
    
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; color: #00f2ff; font-size: 26px; font-weight: bold; }
    
    .clock-container { display: flex; gap: 20px; color: #888; font-family: 'monospace'; font-size: 12px; }
    .clock-box { text-align: center; }
    .clock-time { color: #fff; font-size: 16px; display: block; }

    /* Painel Lateral Estilizado */
    .calc-panel { border: 2px solid #1c3d4d; border-radius: 8px; padding: 10px; background: #0a141a; font-family: monospace; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #1c3d4d; font-size: 14px; font-weight: bold; }

    .ticker-wrapper { background: #000; border: 1px solid #1c3d4d; color: #d4a017; padding: 5px; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 25s linear infinite; font-family: 'monospace'; font-size: 12px; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE CÁLCULO K97 (SUA LÓGICA ORIGINAL) ---
@st.cache_data(ttl=600)
def calcular_eixo_automatico():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d")
        if df.empty: return 37.85, 0, 0
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        idx = -2 if agora.hour < 18 else -1
        mx, mn = df['High'].iloc[idx], df['Low'].iloc[idx]
        return (mx + mn) / 2, mx, mn
    except: return 37.85, 0, 0

def calcular_k97_total(e_ewz, p_ewz_at, mx_ewz, mn_ewz, e_dol):
    try:
        var_at = ((e_ewz / p_ewz_at) - 1) * 100 / 1.5
        dolar_vivo = e_dol * (1 + (var_at / 100))
        var_fraja = ((e_ewz / p_ewz_at) - 1) * 100 / 4.5
        dolar_fraja = e_dol * (1 + (var_fraja / 100))
        
        ewz_med = (mx_ewz + mn_ewz) / 2
        v_neg = ((e_ewz / mx_ewz) - 1) * 100 / 1.5
        v_pos = ((e_ewz / mn_ewz) - 1) * 100 / 1.5
        
        mx_proj = e_dol * (1 + (v_pos / 100))
        mn_proj = e_dol * (1 + (v_neg / 100))
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "v_at": var_at,
            "max": mx_proj, "p75_up": (e_dol + (mx_proj - e_dol)*0.75), 
            "p50_up": (e_dol + mx_proj) / 2, "p25_up": (e_dol + (mx_proj - e_dol)*0.25),
            "min": mn_proj, "p75_dn": (e_dol + (mn_proj - e_dol)*0.75), 
            "p50_dn": (e_dol + mn_proj) / 2, "p25_dn": (e_dol + (mn_proj - e_dol)*0.25)
        }
    except: return None

# --- CAPTURA DE DADOS VIVOS ---
eixo_sug, mx_ref, mn_ref = calcular_eixo_automatico()
br_t = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M')
ny_t = datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M')
ld_t = datetime.now(pytz.timezone('Europe/London')).strftime('%H:%M')

with st.sidebar:
    st.header("⚙️ AJUSTE K97")
    e_ewz_input = st.number_input("EIXO EWZ:", value=float(eixo_sug), format="%.2f")
    e_dol_input = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f")

# --- HEADER ---
st.markdown(f"""
<div class="header-bair">
    <div style="color: #00f2ff;">BAIR - <span style="color: #d4a017;">TERMINAL DOLAR</span></div>
    <div class="clock-container">
        <div class="clock-box">BRASÍLIA<span class="clock-time">{br_t}</span></div>
        <div class="clock-box">NEW YORK<span class="clock-time">{ny_t}</span></div>
        <div class="clock-box">LONDRES<span class="clock-time">{ld_t}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Coleta final para a tabela
def fetch(s):
    try:
        d = yf.Ticker(s).history(period="1d", interval="1m", prepost=True)
        return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return None

ewz = fetch("EWZ")
dxy = fetch("DX-Y.NYB")
spot = fetch("USDBRL=X")

if ewz and spot:
    res = calcular_k97_total(e_ewz_input, ewz['at'], ewz['mx'], ewz['mn'], e_dol_input)
    
    # --- GRADE PRINCIPAL ---
    html_table = f"""
    <div class="main-grid">
        <table class="terminal-table">
            <thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead>
            <tbody>
                <tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>SINTÉTICO 2.0</td><td style='color:#d4a017;'>{res['vivo']:.2f}</td><td>{e_dol_input:.2f}</td><td>{e_dol_input:.2f}</td><td>{res['max']:.2f}</td><td>{res['min']:.2f}</td><td style='color:#00f2ff; font-weight:bold;'>{res['v_at']:+.2f}%</td></tr>
                <tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>SINTÉTICO 3.6</td><td style='color:#d4a017;'>{res['fraja']:.2f}</td><td>{e_dol_input:.2f}</td><td>{e_dol_input:.2f}</td><td>---</td><td>---</td><td style='color:#00f2ff;'>FRAJA</td></tr>
                <tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>SPOT</td><td style='color:#d4a017;'>{spot['at']:.4f}</td><td>{spot['cl']:.4f}</td><td>{spot['cl']:.4f}</td><td>{spot['mx']:.4f}</td><td>{spot['mn']:.4f}</td><td style='color:#ff4d4d;'>--</td></tr>
                <tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>EWZ</td><td style='color:#d4a017;'>{ewz['at']:.2f}</td><td>{e_ewz_input:.2f}</td><td>{e_ewz_input:.2f}</td><td>{ewz['mx']:.2f}</td><td>{ewz['mn']:.2f}</td><td style='color:#ff4d4d;'>{((ewz['at']/e_ewz_input)-1)*100:+.2f}%</td></tr>
            </tbody>
        </table>
    </div>"""

    col_main, col_side = st.columns([3, 1])
    with col_main:
        st.markdown(html_table, unsafe_allow_html=True)
        # Rodapé Marquee
        ticker_txt = f" • SINTÉTICO 2.0: {res['vivo']:.2f} • EWZ: {ewz['at']:.2f} • DXY: {dxy['at']:.3f} • SPOT: {spot['at']:.4f} "
        st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{ticker_txt * 4}</div></div>', unsafe_allow_html=True)

    with col_side:
        # --- PAINEL DE CÁLCULOS (SUAS VARIÁVEIS) ---
        st.markdown(f"""
        <div class="calc-panel">
            <div style="color: #d4a017; text-align: center; font-size: 14px; font-weight: bold; margin-bottom: 10px;">VARIAÇÕES MAX/MIN</div>
            <div class="calc-row" style="color:#ff4d4d; border-top: 2px solid #ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ff7675;"><span>75% UP</span> <span>{res['p75_up']:.2f}</span></div>
            <div class="calc-row" style="color:#fab1a0;"><span>50% UP</span> <span>{res['p50_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffeaa7;"><span>25% UP</span> <span>{res['p25_up']:.2f}</span></div>
            <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 16px;">EIXO: {e_dol_input:.2f}</div>
            <div class="calc-row" style="color:#ffeaa7;"><span>25% DN</span> <span>{res['p25_dn']:.2f}</span></div>
            <div class="calc-row" style="color:#81ecec;"><span>50% DN</span> <span>{res['p50_dn']:.2f}</span></div>
            <div class="calc-row" style="color:#55efc4;"><span>75% DN</span> <span>{res['p75_dn']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom: 2px solid #00ff88;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

time.sleep(2)
st.rerun()
