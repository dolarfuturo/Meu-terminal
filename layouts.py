import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(page_title="BAIR - K97 TERMINAL", layout="wide")

# --- CSS: ESTILO LARANJA + BLOCOS PROFISSIONAIS ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2px solid #1c3d4d; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #1c3d4d; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #1c3d4d; padding: 12px; text-align: center; font-size: 15px; }
    .var-pos { color: #00f2ff !important; font-weight: bold; }
    .var-neg { color: #ff4d4d !important; font-weight: bold; }
    
    /* Header e Relógios */
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; color: #00f2ff; font-size: 24px; font-weight: bold; }
    .clock-container { display: flex; gap: 15px; color: #888; font-family: 'monospace'; font-size: 11px; }
    .clock-box { text-align: center; border: 1px solid #1c3d4d; padding: 4px 8px; border-radius: 4px; background: #0a141a; }
    .clock-time { color: #fff; font-size: 14px; display: block; }

    /* Painel Lateral de Cálculos */
    .calc-row { display: flex; justify-content: space-between; padding: 6px 10px; border-bottom: 1px solid #1c3d4d; font-family: 'monospace'; font-size: 14px; }
    
    /* Ticker Tape Animation */
    .ticker-wrapper { background: #000; border: 1px solid #1c3d4d; color: #d4a017; padding: 5px; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 25s linear infinite; font-family: 'monospace'; font-size: 12px; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CÁLCULO (SUA LÓGICA ORIGINAL) ---
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

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 1.5
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 4.5
        dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
        
        ewz_medio_dia = (max_ewz + min_ewz) / 2
        var_medio = ((eixo_ewz / ewz_medio_dia) - 1) * 100 
        dolar_medio = eixo_dol * (1 + (var_medio / 100)) 
        
        v_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 1.5
        v_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 1.5
        alvo_max = eixo_dol * (1 + (v_pos / 100))
        alvo_min = eixo_dol * (1 + (v_neg / 100))
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, 
            "v_atual": var_atual, "ewz_med": ewz_medio_dia,
            "max": alvo_max, "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), 
            "p50_up": (eixo_dol + alvo_max) / 2, 
            "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25),
            "min": alvo_min, "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), 
            "p50_down": (eixo_dol + alvo_min) / 2, 
            "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
        }
    except: return None

# --- CAPTURA DE DADOS ---
eixo_sug, mx_ref, mn_ref = calcular_eixo_automatico()
fmt = '%H:%M'
br_t = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime(fmt)
ny_t = datetime.now(pytz.timezone('America/New_York')).strftime(fmt)
ld_t = datetime.now(pytz.timezone('Europe/London')).strftime(fmt)

# --- SIDEBAR (CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("⚙️ AJUSTE K97")
    e_ewz = st.number_input("EIXO EWZ:", value=float(eixo_sug), format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f")
    st.write(f"Ref. EWZ: {eixo_sug:.2f}")

# --- HEADER ---
st.markdown(f"""
<div class="header-bair">
    <div>BAIR - <span style="color: #d4a017;">TERMINAL DOLAR</span></div>
    <div class="clock-container">
        <div class="clock-box">BRASÍLIA<span class="clock-time">{br_t}</span></div>
        <div class="clock-box">NEW YORK<span class="clock-time">{ny_t}</span></div>
        <div class="clock-box">LONDRES<span class="clock-time">{ld_t}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- BUSCA REAL DOS ATIVOS ---
def get_data(ticker):
    try:
        d = yf.Ticker(ticker).history(period="1d", interval="1m", prepost=True)
        return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return None

ewz_data = get_data("EWZ")
dxy_data = get_data("DX-Y.NYB")
spot_data = get_data("USDBRL=X")

if ewz_data:
    res = calcular_k97_total(e_ewz, ewz_data["at"], ewz_data["mx"], ewz_data["mn"], e_dol)
    
    # Montagem da Tabela (Grade Principal)
    html_grid = f"""
    <div class="main-grid">
        <div style="background: #0a141a; color: #5ba6b5; text-align: center; padding: 8px; border-bottom: 1px solid #1c3d4d; font-size: 12px; letter-spacing: 2px;">
            MONITORAMENTO DA GRADE PRINCIPAL
        </div>
        <table class="terminal-table">
            <thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead>
            <tbody>
                <tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>SINTÉTICO 2.0</td><td style='color:#d4a017;'>{res['vivo']:.2f}</td><td>{e_dol:.2f}</td><td>{e_dol:.2f}</td><td>{res['max']:.2f}</td><td>{res['min']:.2f}</td><td class='var-pos'>{res['v_atual']:+.2f}%</td></tr>
                <tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>SINTÉTICO 3.6</td><td style='color:#d4a017;'>{res['fraja']:.2f}</td><td>{e_dol:.2f}</td><td>{e_dol:.2f}</td><td>---</td><td>---</td><td class='var-pos'>FRAJA</td></tr>
                <tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>SPOT</td><td style='color:#d4a017;'>{spot_data['at']:.4f}</td><td>{spot_data['cl']:.4f}</td><td>{spot_data['cl']:.4f}</td><td>{spot_data['mx']:.4f}</td><td>{spot_data['mn']:.4f}</td><td class='var-neg'>--</td></tr>
                <tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>EWZ</td><td style='color:#d4a017;'>{ewz_data['at']:.2f}</td><td>{e_ewz:.2f}</td><td>{e_ewz:.2f}</td><td>{ewz_data['mx']:.2f}</td><td>{ewz_data['mn']:.2f}</td><td class='var-neg'>{((ewz_data['at']/e_ewz)-1)*100:+.2f}%</td></tr>
                <tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>DXY</td><td style='color:#d4a017;'>{dxy_data['at']:.3f}</td><td>{dxy_data['cl']:.3f}</td><td>{dxy_data['cl']:.3f}</td><td>{dxy_data['mx']:.3f}</td><td>{dxy_data['mn']:.3f}</td><td class='var-pos'>--</td></tr>
            </tbody>
        </table>
    </div>
    """

    col_main, col_side = st.columns([3, 1.2])
    
    with col_main:
        st.markdown(html_grid, unsafe_allow_html=True)
        # Rodapé Animado
        ticker_txt = f" • SINTÉTICO 2.0: {res['vivo']:.2f} • EWZ: {ewz_data['at']:.2f} • DXY: {dxy_data['at']:.3f} • SPOT: {spot_data['at']:.4f}"
        st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{ticker_txt * 4}</div></div>', unsafe_allow_html=True)

    with col_side:
        # Painel Lateral com as SUAS variáveis
        st.markdown(f"""
        <div style="border: 2px solid #1c3d4d; border-radius: 8px; padding: 10px; background: #0a141a; font-family: monospace;">
            <div style="color: #d4a017; text-align: center; font-size: 13px; font-weight: bold; margin-bottom: 10px;">PROJEÇÕES K97</div>
            <div class="calc-row" style="color:#ff4d4d; font-weight:bold;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ff7675;"><span>75% UP</span> <span>{res['p75_up']:.2f}</span></div>
            <div class="calc-row" style="color:#fab1a0;"><span>50% UP</span> <span>{res['p50_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffeaa7;"><span>25% UP</span> <span>{res['p25_up']:.2f}</span></div>
            <div style="text-align:center; padding: 8px; color: #00f2ff; font-size: 16px; border-bottom: 1px solid #1c3d4d;">EIXO: {e_dol:.2f}</div>
            <div class="calc-row" style="color:#ffeaa7;"><span>25% DN</span> <span>{res['p25_down']:.2f}</span></div>
            <div class="calc-row" style="color:#81ecec;"><span>50% DN</span> <span>{res['p50_down']:.2f}</span></div>
            <div class="calc-row" style="color:#55efc4;"><span>75% DN</span> <span>{res['p75_down']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; font-weight:bold; border-bottom:none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

# Auto-refresh
time.sleep(2)
st.rerun()
