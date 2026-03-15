import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: ESTILO REFINADO + VELOCIDADE MARQUEE AJUSTADA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2px solid #1c3d4d; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #1c3d4d; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #1c3d4d; padding: 12px; text-align: center; font-size: 15px; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; color: #00f2ff; font-size: 26px; font-weight: bold; }
    .clock-container { display: flex; gap: 20px; color: #888; font-family: 'monospace'; font-size: 12px; }
    .clock-box { text-align: center; border: 1px solid #1c3d4d; padding: 5px; border-radius: 4px; background: #0a141a; }
    .clock-time { color: #fff; font-size: 16px; display: block; }
    
    .calc-panel { border: 2px solid #1c3d4d; border-radius: 8px; padding: 10px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 6px 8px; border-bottom: 1px solid #1c3d4d; font-size: 14px; font-weight: bold; }
    
    /* Marquee mais lento: 45s */
    .ticker-wrapper { background: #000; border: 1px solid #1c3d4d; padding: 5px; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 45s linear infinite; font-family: 'monospace'; font-size: 13px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    .monitor-bar { background: #0a141a; border: 1px solid #1c3d4d; padding: 8px; text-align: center; color: #00f2ff; font-weight: bold; font-family: monospace; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
@st.cache_data(ttl=600)
def calcular_eixo_automatico():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d")
        if df.empty: return 37.85, 38.10, 37.60
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        idx = -2 if agora.hour < 18 else -1
        mx, mn = df['High'].iloc[idx], df['Low'].iloc[idx]
        return (mx + mn) / 2, mx, mn
    except: return 37.85, 38.10, 37.60

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
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
        "v_atual": var_atual, "ewz_med": ewz_medio_dia, "v_med": var_medio,
        "max": alvo_max, "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), 
        "p50_up": (eixo_dol + alvo_max) / 2, "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25),
        "min": alvo_min, "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), 
        "p50_down": (eixo_dol + alvo_min) / 2, "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
    }

def fetch(s):
    try:
        d = yf.Ticker(s).history(period="1d", interval="1m", prepost=True)
        return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return None

# --- UI PRINCIPAL ---
eixo_sug, mx_ref, mn_ref = calcular_eixo_automatico()
br_t = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M')
ny_t = datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M')
ld_t = datetime.now(pytz.timezone('Europe/London')).strftime('%H:%M')

with st.sidebar:
    st.header("⚙️ AJUSTE K97")
    e_ewz = st.number_input("EIXO EWZ:", value=float(eixo_sug), format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f")
    st.divider()

st.markdown(f"""<div class="header-bair"><div>BAIR - <span style="color: #d4a017;">TERMINAL DOLAR</span></div><div class="clock-container"><div class="clock-box">BRASÍLIA<span class="clock-time">{br_t}</span></div><div class="clock-box">NEW YORK<span class="clock-time">{ny_t}</span></div><div class="clock-box">LONDRES<span class="clock-time">{ld_t}</span></div></div></div>""", unsafe_allow_html=True)

ewz_live = fetch("EWZ")
if ewz_live:
    res = calcular_k97_total(e_ewz, ewz_live['at'], mx_ref, mn_ref, e_dol)
    
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.markdown('<div class="monitor-bar">MONITORAMENTO DE ATIVOS</div>', unsafe_allow_html=True)
    with head_col2:
        st.markdown('<div class="monitor-bar">PROJEÇÕES K97</div>', unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1])
    
    with col_main:
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        # Sintético 2.0 - Ex: 5.3510
        v2_var = ((res['vivo'] / e_dol) - 1) * 100
        v2_cor = "#00ff00" if v2_var >= 0 else "#ff0000"
        html_table += f"<tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>SINTÉTICO 2.0 (VIVO)</td><td style='color:#d4a017;'>{(res['vivo']/1000):.4f}</td><td>{(e_dol/1000):.4f}</td><td>{(e_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{v2_cor}; font-weight:bold;'>{v2_var:+.2f}%</td></tr>"
        
        # Dicionário de ativos com mapeamento de precisão
        ativos_config = {
            "SPOT": {"sym": "USDBRL=X", "fmt": ".4f"},
            "DXY": {"sym": "DX-Y.NYB", "fmt": ".2f"},
            "EWZ": {"sym": "EWZ", "fmt": ".2f"},
            "GBP/USD": {"sym": "GBPUSD=X", "fmt": ".4f"},
            "JPY/USD": {"sym": "JPYUSD=X", "fmt": ".4f"},
            "EUR/USD": {"sym": "EURUSD=X", "fmt": ".4f"},
            "GOLD": {"sym": "GC=F", "fmt": ".4f"},
            "BRENT": {"sym": "BZ=F", "fmt": ".2f"}
        }
        
        ticker_items = [f"<span style='color:#fff;'>SINTÉTICO 2.0:</span> <span style='color:{v2_cor};'>{v2_var:+.2f}%</span>"]
        
        for label, cfg in ativos_config.items():
            d = fetch(cfg['sym'])
            if d:
                v = ((d['at']/d['cl'])-1)*100
                c = "#00ff00" if v >= 0 else "#ff0000"
                f = cfg['fmt']
                html_table += f"<tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>{label}</td><td style='color:#d4a017;'>{d['at']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{c}; font-weight:bold;'>{v:+.2f}%</td></tr>"
                ticker_items.append(f"<span style='color:#fff;'>{label}:</span> <span style='color:{c};'>{v:+.2f}%</span>")

        html_table += "</tbody></table></div>"
        st.markdown(html_table, unsafe_allow_html=True)
        
        # Ticker Marquee Lento
        ticker_html = " • ".join(ticker_items)
        st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{ticker_html} • {ticker_html}</div></div>', unsafe_allow_html=True)

    with col_side:
        # Bloco de Projeções (Níveis)
        st.markdown(f"""
        <div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ff7675;"><span>75% UP</span> <span>{res['p75_up']:.2f}</span></div>
            <div class="calc-row" style="color:#fab1a0;"><span>50% UP</span> <span>{res['p50_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffeaa7;"><span>25% UP</span> <span>{res['p25_up']:.2f}</span></div>
            <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 16px;">EIXO: {e_dol:.2f}</div>
            <div class="calc-row" style="color:#ffeaa7;"><span>25% DN</span> <span>{res['p25_down']:.2f}</span></div>
            <div class="calc-row" style="color:#81ecec;"><span>50% DN</span> <span>{res['p50_down']:.2f}</span></div>
            <div class="calc-row" style="color:#55efc4;"><span>75% DN</span> <span>{res['p75_down']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bloco Externo
        vm_cor = "#00ff00" if res['v_med'] >= 0 else "#ff0000"
        st.markdown(f"""
        <div class="calc-panel" style="border-color: #d4a017;">
            <div style="color: #d4a017; text-align: center; font-size: 12px; margin-bottom: 5px;">SINTÉTICOS ADICIONAIS</div>
            <div class="calc-row" style="color:#00f2ff;"><span>MÉDIO (50%)</span> <span>{res['medio']:.2f}</span></div>
            <div class="calc-row" style="color:{vm_cor}; font-size:12px;"><span>VAR MÉDIA</span> <span>{res['v_med']:+.2f}%</span></div>
            <div class="calc-row" style="color:#d4a017; border-bottom: none;"><span>3.6 (FRAJA)</span> <span>{res['fraja']:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

time.sleep(2)
st.rerun()
