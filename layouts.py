import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- CSS: ESTILIZAÇÃO COMPACTA (MANTIDA INTEGRALMENTE) ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 8px; }
    .title-box { display: flex; align-items: center; gap: 8px; line-height: 1; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .sep-text { font-size: 46px; color: #ffffff; font-weight: 950; margin: 0 5px; }
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; margin-bottom: 2px; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 6px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
    .bar-wrapper-dual { background: #0a141a; padding: 12px 10px 6px 10px; border: 2.5px solid #ffffff; border-radius: 8px; text-align: center; position: relative; }
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 16px; font-weight: 950; line-height: 1; margin-top: 5px; min-height: 16px; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADO ---
if 'a_ewz' not in st.session_state: st.session_state.a_ewz = 37.85
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00

# --- MOTOR DE DADOS ---
def fetch_fast(s):
    try:
        t = yf.Ticker(s)
        # Usando fast_info para o preço live (estilo Nexus)
        price = t.fast_info['last_price']
        # History apenas para o dia atual (mx/mn)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": price, "cl": 0.0, "mx": price, "mn": price, "op": price}
        m = 1000 if s == "USDBRL=X" else 1
        return {
            "at": price * m, 
            "cl": t.info.get('previousClose', d['Open'].iloc[0]) * m, 
            "op": d['Open'].iloc[0] * m, 
            "mx": d['High'].max() * m, 
            "mn": d['Low'].min() * m
        }
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- PAINEL ADM NA SIDEBAR (SEM PISCAR) ---
with st.sidebar:
    st.markdown("### ⚙️ CONFIGURAÇÕES K97")
    with st.expander("AJUSTAR EIXOS", expanded=True):
        st.session_state.a_ewz = st.number_input("AXIS EWZ:", value=st.session_state.a_ewz, format="%.2f")
        st.session_state.a_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol, format="%.2f")
        if st.button("ATUALIZAR TERMINAL"):
            st.rerun()

# --- ESPAÇO RESERVADO (O SEGREDO DO NEXUS) ---
main_placeholder = st.empty()

# --- LOOP INFINITO (SEM RERUN) ---
while True:
    # Coleta de dados rápida
    ewz_live = fetch_fast("EWZ")
    spot_live = fetch_fast("USDBRL=X")
    
    # Lógica K97 (Intocada)
    v_spreed = (spot_live['mx'] - spot_live['mn']) / 8
    v_spot = ((spot_live['at'] / spot_live['cl']) - 1) if spot_live['cl'] > 0 else 0
    # Busca o fechamento do EWZ para variação
    ewz_cl = ewz_live['cl'] if ewz_live['cl'] > 0 else 1
    v_ewz = ((ewz_live['at'] / ewz_cl) - 1)
    v_final = (v_spot * 0.6) - (v_ewz * 0.4)
    
    # Cálculos de Exaustão
    dolar_vivo = spot_live['at']
    dolar_fraja = st.session_state.a_dol * (1 + (v_final / 2))
    dolar_medio = (spot_live['mx'] + spot_live['mn']) / 2
    max_fut = spot_live['mx'] + v_spreed
    min_fut = spot_live['mn'] + v_spreed
    
    dist_base = abs(st.session_state.a_dol - dolar_medio)
    diff = spot_live['at'] - st.session_state.a_dol
    p_v, p_r = 0, 0
    if dist_base > 0:
        if diff < 0: p_v = min(100, (abs(diff)/(dist_base*2))*100)
        else: p_r = min(100, (abs(diff)/(dist_base*2))*100)

    seta_txt, seta_cor = ("", "#000000")
    if p_v >= 100: seta_txt, seta_cor = "▲ COMPRA", "#00ff88"
    elif p_r >= 100: seta_txt, seta_cor = "▼ VENDA", "#ff4d4d"

    # Início da Renderização no Placeholder
    with main_placeholder.container():
        tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
        
        st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M:%S')}</span></div><div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M:%S')}</span></div><div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M:%S')}</span></div></div></div>""", unsafe_allow_html=True)

        c_main, c_side = st.columns([3, 1])
        with c_main:
            html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
            
            # Linha DOLFUT
            dolfut_calc = st.session_state.a_dol * (1 + v_final)
            html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(dolfut_calc/1000):.4f}</td><td>{(st.session_state.a_dol/1000):.4f}</td><td>{(st.session_state.a_dol/1000):.4f}</td><td>{(max_fut/1000):.4f}</td><td>{(min_fut/1000):.4f}</td><td style='color:{("#00ff00" if v_final >= 0 else "#ff4d4d")}; font-weight:bold;'>{v_final*100:+.2f}%</td></tr>"
            
            outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "SPX": "^GSPC", "PETROLEO": "BZ=F"}
            for lbl, sym in outros.items():
                d = spot_live if lbl == "DOLSPOT" else (ewz_live if lbl == "EWZ" else fetch_fast(sym))
                var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                p_val = d['at']/1000 if "DOL" in lbl else d['at']
                html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{p_val:.4f}</td><td>{(d['cl']/1000 if 'DOL' in lbl else d['cl']):.4f}</td><td>{(d['op']/1000 if 'DOL' in lbl else d['op']):.4f}</td><td>{(d['mx']/1000 if 'DOL' in lbl else d['mx']):.4f}</td><td>{(d['mn']/1000 if 'DOL' in lbl else d['mn']):.4f}</td><td style='color:{("#00ff00" if var>=0 else "#ff4d4d")};'>{var:+.2f}%</td></tr>"
            st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

        with c_side:
            st.markdown(f"""<div class="calc-panel">
                <div class="calc-row" style="color:#ff4d4d;"><span>MAX FUT</span> <span>{max_fut:.2f}</span></div>
                <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {st.session_state.a_dol:.2f}</div>
                <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MIN FUT</span> <span>{min_fut:.2f}</span></div>
            </div>""", unsafe_allow_html=True)
            
            st.markdown(f"""<div class="calc-panel">
                <div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff; font-size:18px;">{dolar_vivo+v_spreed:.2f}</span></div>
                <div class="calc-row"><span>P. JUSTO</span> <span style="color:#ffffff;">{dolar_fraja:.2f}</span></div>
                <div class="calc-row" style="border-bottom:none;"><span>SPREAD</span> <span style="color:#d4a017;">{v_spreed:.2f}</span></div>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"""<div class="bar-wrapper-dual">
                <div class="force-container-dual">
                    <div class="center-line"></div>
                    <div class="bar-side"><div class="fill-green" style="width: {p_v}%;"></div></div>
                    <div class="bar-side"><div class="fill-red" style="width: {p_r}%;"></div></div>
                </div>
                <div class="sinal-indicator blink" style="color:{seta_cor};">{seta_txt}</div>
            </div>""", unsafe_allow_html=True)

    time.sleep(1) # Refresh de 1 segundo (Liso)
