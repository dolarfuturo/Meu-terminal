import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS MANTIDO INTEGRALMENTE ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; }
    .clock-container { display: flex; gap: 10px; color: #888; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .monitor-bar { background: #0a141a; border: 2.2px solid #ffffff; padding: 6px; text-align: center; color: #00f2ff; font-weight: bold; border-radius: 4px; margin-bottom: 8px; }
    .ewz-mini-container { display: flex; justify-content: space-around; padding: 4px 0; border-top: 1px solid #444; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE CÁLCULO (EXCLUSIVO EWZ 10:30-17:00) ---
@st.cache_data(ttl=600)
def calcular_referencias_axis():
    try:
        t = yf.Ticker("EWZ")
        # Pega 5 dias para garantir o último pregão completo
        df = t.history(period="5d", interval="1m", prepost=False)
        if df.empty: return 37.85, 38.10, 37.60
        
        # Converte para SP para filtrar o horário exato de Brasília
        df.index = df.index.tz_convert('America/Sao_Paulo')
        
        # Pega o último dia útil disponível antes de hoje (ou hoje se já passou das 18h)
        hoje = datetime.now(pytz.timezone('America/Sao_Paulo')).date()
        datas_disponiveis = sorted(list(set(df.index.date)))
        
        # Lógica da Sentinela: Se hoje ainda não fechou, usa o dia anterior
        target_date = datas_disponiveis[-1]
        if target_date == hoje and datetime.now(pytz.timezone('America/Sao_Paulo')).hour < 18:
            target_date = datas_disponiveis[-2] if len(datas_disponiveis) > 1 else target_date

        df_dia = df[df.index.date == target_date]
        # FILTRO EXCLUSIVO 10:30 ÀS 17:00 PARA O EIXO
        df_regular = df_dia.between_time(dt_time(10, 30), dt_time(17, 0))
        
        if not df_regular.empty:
            mx = df_regular['High'].max()
            mn = df_regular['Low'].min()
            return (mx + mn) / 2, mx, mn
    except: pass
    return 37.85, 38.10, 37.60

def calcular_k97_total(axis_ewz, p_ewz_atual, max_ewz, min_ewz, axis_dol):
    # Motor K97 com sensibilidade 1.5 e 4.5
    v_atual = ((axis_ewz / p_ewz_atual) - 1) * 100 / 1.5
    dolar_vivo = axis_dol * (1 + (v_atual / 100))
    v_neg = ((axis_ewz / max_ewz) - 1) * 100 / 1.5
    v_pos = ((axis_ewz / min_ewz) - 1) * 100 / 1.5
    alvo_max, alvo_min = axis_dol * (1 + (v_pos / 100)), axis_dol * (1 + (v_neg / 100))
    return {
        "vivo": dolar_vivo, 
        "fraja": axis_dol * (1 + (((axis_ewz / p_ewz_atual) - 1) * 100 / 4.5 / 100)),
        "medio": axis_dol * (1 + (((axis_ewz / ((max_ewz + min_ewz) / 2)) - 1) * 100 / 100)),
        "max": alvo_max, "min": alvo_min,
        "p75_up": (axis_dol + (alvo_max - axis_dol)*0.75), "p50_up": (axis_dol + alvo_max) / 2, "p25_up": (axis_dol + (alvo_max - axis_dol)*0.25),
        "p75_down": (axis_dol + (alvo_min - axis_dol)*0.75), "p50_down": (axis_dol + alvo_min) / 2, "p25_down": (axis_dol + (alvo_min - axis_dol)*0.25)
    }

def fetch_real_time(s):
    try:
        # AQUI BUSCA HORÁRIO NORMAL (SEM FILTRO)
        d = yf.Ticker(s).history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0}
        return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0}

# --- UI EXECUTION ---
axis_auto, mx_ref, mn_ref = calcular_referencias_axis()
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_ewz = st.number_input("AXIS EWZ:", value=float(axis_auto), format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
    st.write(f"Eixo (10:30-17:00): {axis_auto:.2f}")

tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

ewz_live = fetch_real_time("EWZ")
if ewz_live:
    res = calcular_k97_total(a_ewz, ewz_live['at'], mx_ref, mn_ref, a_dol)
    c_main, c_side = st.columns([3, 1])
    
    with c_main:
        st.markdown('<div class="monitor-bar">GRADE DE ATIVOS (REAL-TIME)</div>', unsafe_allow_html=True)
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        # DOLFUT CALCULADO
        v_var = ((res['vivo']/a_dol)-1)*100
        c_v = "#00ff00" if v_var >= 0 else "#ff0000"
        html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{c_v}; font-weight:bold;'>{v_var:+.2f}%</td></tr>"
        
        ticker_items = [f"DOLFUT: {v_var:+.2f}%"]
        # OUTROS ATIVOS - HORÁRIO NORMAL
        outros = {"SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EURUSD": "EURUSD=X", "JPYUSD": "JPYUSD=X", "GBPUSD": "GBPUSD=X", "BRENT": "BZ=F", "GOLD": "GC=F"}
        for lbl, sym in outros.items():
            d = fetch_real_time(sym)
            v = ((d['at']/d['cl'])-1)*100 if d['cl'] > 0 else 0
            c = "#00ff00" if v >= 0 else "#ff0000"
            f = ".4f" if "USD" in lbl or lbl == "SPOT" else ".2f"
            html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{c}; font-weight:bold;'>{v:+.2f}%</td></tr>"
            ticker_items.append(f"{lbl}: {v:+.2f}%")
        
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        st.markdown('<div class="monitor-bar">PROJEÇÕES K97</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div><div style="text-align:center; padding:10px; color:#00f2ff; font-weight:bold; border-top:1px solid #444; border-bottom:1px solid #444;">AXIS: {a_dol:.2f}</div><div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
        
        st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div><div class="calc-row" style="border-bottom:none;"><span>JUSTO</span> <span style="color:#ffffff;">{res['fraja']:.2f}</span></div><div class="ewz-mini-container"><span style="color:#00ff88;">{mx_ref:.2f}</span><span style="color:#00f2ff;">{axis_auto:.2f}</span><span style="color:#ff4d4d;">{mn_ref:.2f}</span></div></div>""", unsafe_allow_html=True)

    t_str = " • ".join(ticker_items)
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{t_str} • {t_str}</div></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
