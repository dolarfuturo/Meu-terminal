import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- SISTEMA DE CACHE ---
if 'market_data' not in st.session_state:
    st.session_state.market_data = {}
if 'last_p' not in st.session_state:
    st.session_state.last_p = {}

# --- CSS: MANTIDO ORIGINAL + CLASSES DE FLASH ---
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    .stApp { background-color: #050a0e !important; }
    .header-container { text-align: center; padding: 5px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; }
    .main-title { margin: 0px; line-height: 1.0; font-size: 28px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .clock-row { display: flex; justify-content: center; gap: 20px; padding: 5px 0; font-weight: bold; font-size: 11px; font-family: monospace; }
    .clock-item { color: #AAA; }
    .br-green { color: #00ff00; }
    .white-time { color: #ffffff; }
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 3px; margin-bottom: 5px; text-transform: uppercase; font-size: 11px; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 11px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 6px; text-align: center; font-size: 13px; transition: background-color 0.3s; }
    .asset-name { font-size: 13px; color: #fff; text-align: left; font-weight: bold; padding-left: 10px; }
    .price-col { font-weight: bold; color: #ffffff !important; }
    
    /* Classes para o Flash de Tique */
    .f-up { background-color: #00ff00aa !important; }
    .f-dn { background-color: #ff0000aa !important; }

    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 3px 6px; border-bottom: 1px solid #444; font-size: 11px; font-weight: bold; align-items: center; }
    .bar-wrapper-dual { background: #0a141a; padding: 8px 8px 4px 8px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; position: relative; }
    .force-scale { display: flex; justify-content: space-between; font-size: 9px; font-family: monospace; color: #AAA; margin-bottom: 2px; padding: 0 2px; }
    .force-container-dual { background: #111; height: 12px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 2px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 13px; font-weight: 900; line-height: 1; margin-top: 4px; min-height: 14px; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 5px 0; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return st.session_state.market_data.get(s)
        ref_close = t.info.get('previousClose')
        if s == "EWZ":
            d_hist = t.history(period="3d", interval="1m", prepost=True)
            if not d_hist.empty:
                d_hist.index = d_hist.index.tz_convert(tz_sp)
                unique_dates = sorted(list(set(d_hist.index.date)))
                data_anterior = unique_dates[-2] if len(unique_dates) > 1 else unique_dates[0]
                f_21h = d_hist.between_time('05:00', '21:00').loc[d_hist.index.date == data_anterior]
                if not f_21h.empty: ref_close = f_21h['Close'].iloc[-1]
        m = 1000 if s == "USDBRL=X" else 1
        data = {
            "at": d['Close'].iloc[-1] * m, 
            "cl": (ref_close or d['Open'].iloc[0]) * m, 
            "op": d['Open'].iloc[0] * m, 
            "mx": d['High'].max() * m, 
            "mn": d['Low'].min() * m
        }
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s)

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol, spot_data):
    try:
        if not spot_data or p_ewz_atual == 0: return None
        amp = spot_data['mx'] - spot_data['mn']
        v_spreed = amp / 8
        x1, x2 = amp * 0.77, amp * 0.23
        max_f, min_f = eixo_dol + x1, eixo_dol - x2
        med_d = ((max_f + min_f) / 2) - v_spreed
        v_spot_pct = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        dolb3 = eixo_dol + (eixo_dol * v_spot_pct)
        ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
        v_ewz = ((p_ewz_atual / ewz_ref) - 1) if ewz_ref > 0 else 0
        v_final = (v_spot_pct * 0.6) - (v_ewz * 0.4)
        dist_base = abs(eixo_dol - med_d)
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = 0, 0
        if dist_base > 0:
            if diff < 0: p_v = min(100, (abs(diff)/(dist_base*2))*100)
            else: p_r = min(100, (abs(diff)/(dist_base*2))*100)
        seta_txt, seta_cor = "", "#000000"
        if p_v >= 100: seta_txt, seta_cor = "▲ REGIÃO DE COMPRA", "#00ff88"
        elif p_r >= 100: seta_txt, seta_cor = "▼ REGIÃO DE VENDA", "#ff4d4d"
        return {
            "vivo": dolb3, "fraja": eixo_dol * (1 + (v_final / 2)), "medio": med_d,
            "max_fut": max_f, "min_fut": min_f, "p75_up": max_f - v_spreed,
            "p25_up": eixo_dol + v_spreed, "p25_down": eixo_dol - v_spreed,
            "p75_down": min_f + v_spreed, "v_v": v_spot_pct * 100, 
            "spreed": v_spreed, "p_v": p_v, "p_r": p_r, "seta": seta_txt, "seta_cor": seta_cor
        }
    except: return None

with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_ewz = st.number_input("AXIS EWZ:", value=37.85, format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT:", value=5264.50, format="%.2f")
    st.button("SALVAR")

placeholder = st.empty()

while True:
    tz_sp = pytz.timezone('America/Sao_Paulo'); tz_ny = pytz.timezone('America/New_York'); tz_ld = pytz.timezone('Europe/London')
    spot_live = fetch("USDBRL=X")
    ewz_live = fetch("EWZ")
    
    if spot_live and ewz_live:
        res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol, spot_live)
        now = datetime.now()

        with placeholder.container():
            st.markdown(f'<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1><div class="clock-row"><span class="clock-item">🇧🇷 BRASÍLIA: <span class="br-green">{now.astimezone(tz_sp).strftime("%H:%M:%S")}</span></span><span class="clock-item">🇺🇸 NEW YORK: <span class="white-time">{now.astimezone(tz_ny).strftime("%H:%M:%S")}</span></span><span class="clock-item">🇬🇧 LONDON: <span class="white-time">{now.astimezone(tz_ld).strftime("%H:%M:%S")}</span></span></div></div>', unsafe_allow_html=True)

            if res:
                v_v = res['v_v']
                dolfut_calc = a_dol * (1 + (v_v / 100))
                c_main, c_side = st.columns([3.2, 0.8])
                
                with c_main:
                    st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                    html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                    
                    # Logica DOLFUT com Flash
                    l_df = st.session_state.last_p.get('DF', dolfut_calc/1000)
                    cl_df = "f-up" if (dolfut_calc/1000) > l_df else "f-dn" if (dolfut_calc/1000) < l_df else ""
                    st.session_state.last_p['DF'] = dolfut_calc/1000
                    
                    bg_dol = "background-color:rgba(0, 255, 0, 0.2);" if v_v >= 0 else "background-color:rgba(255, 0, 0, 0.2);"
                    html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col {cl_df}' style='{bg_dol}'>{(dolfut_calc/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max_fut']/1000):.4f}</td><td>{(res['min_fut']/1000):.4f}</td><td style='color:{("#00ff00" if v_v >= 0 else "#ff4d4d")}; font-weight:bold;'>{v_v:+.2f}%</td></tr>"
                    
                    ticker_items = [f"DOLFUT: <span style='color:{("#00ff00" if v_v >= 0 else "#ff4d4d")};'>{v_v:+.2f}%</span>"]
                    outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
                    
                    for lbl, sym in outros.items():
                        d = fetch(sym)
                        if d:
                            # Precisão de 4 casas para Moedas
                            f = ".4f" if lbl in ["DOLSPOT", "GBP/USD", "JPY/USD", "EUR/USD"] else ".2f"
                            p_val = d['at']/1000 if lbl == "DOLSPOT" else d['at']
                            
                            # Logica Flash Ativos
                            l_at = st.session_state.last_p.get(lbl, p_val)
                            cl_at = "f-up" if p_val > l_at else "f-dn" if p_val < l_at else ""
                            st.session_state.last_p[lbl] = p_val
                            
                            var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                            color = "#00ff00" if var >= 0 else "#ff4d4d"
                            bg_item = "background-color:rgba(0, 255, 0, 0.2);" if var >= 0 else "background-color:rgba(255, 0, 0, 0.2);"
                            html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col {cl_at}' style='{bg_item}'>{p_val:{f}}</td><td>{(d['cl']/1000 if lbl=='DOLSPOT' else d['cl']):{f}}</td><td>{(d['op']/1000 if lbl=='DOLSPOT' else d['op']):{f}}</td><td>{(d['mx']/1000 if lbl=='DOLSPOT' else d['mx']):{f}}</td><td>{(d['mn']/1000 if lbl=='DOLSPOT' else d['mn']):{f}}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
                            ticker_items.append(f"{lbl}: <span style='color:{color};'>{var:+.2f}%</span>")
                    st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

                with c_side:
                    st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                    st.markdown(f"""<div class="calc-panel">
                        <div class="calc-row" style="color:#ff4d4d;"><span>MAX</span> <span>{res['max_fut']:.2f}</span></div>
                        <div class="calc-row"><span>75% UP</span> <span>{res['p75_up']:.2f}</span></div>
                        <div class="calc-row"><span>25% UP</span> <span>{res['p25_up']:.2f}</span></div>
                        <div style="text-align:center; padding: 4px; color: #00f2ff; font-size: 11px; font-weight: bold; border-top:1px solid #444; border-bottom:1px solid #444; margin: 3px 0;">AXIS: {a_dol:.2f}</div>
                        <div class="calc-row"><span>25% DN</span> <span>{res['p25_down']:.2f}</span></div>
                        <div class="calc-row"><span>75% DN</span> <span>{res['p75_down']:.2f}</span></div>
                        <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MIN</span> <span>{res['min_fut']:.2f}</span></div>
                    </div>""", unsafe_allow_html=True)
                    
                    st.markdown(f"""<div class="calc-panel">
                        <div class="calc-row" style="border-bottom:none; padding-bottom:0px;"><span style="color:#ffffff;">DOLB3</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
                        <div style="text-align:right; font-size:10px; padding-right:6px; color:{("#00ff00" if v_v >= 0 else "#ff4d4d")}; font-weight:bold; margin-bottom:4px;">{v_v:+.2f}%</div>
                        <div class="calc-row"><span style="color:#ffff00;">MÉDIA DOLAR</span> <span style="color:#00f2ff;">{res['medio']:.2f}</span></div>
                        <div class="calc-row"><span style="color:#d4a017;">PREÇO JUSTO</span> <span style="color:#ffffff;">{res['fraja']:.2f}</span></div>
                        <div class="calc-row" style="border-bottom: none;"><span style="color:#ff4d4d;">SPREED</span> <span style="color:#00f2ff;">{res['spreed']:.2f}</span></div>
                    </div>""", unsafe_allow_html=True)
                    st.markdown(f'<div class="bar-wrapper-dual"><div class="force-scale"><span>100%</span><span>50%</span><span>0%</span><span>50%</span><span>100%</span></div><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width: {res["p_v"]}%;"></div></div><div class="bar-side"><div class="fill-red" style="width: {res["p_r"]}%;"></div></div></div><div class="sinal-indicator blink" style="color:{res["seta_cor"]};">{res["seta"]}</div></div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)}</div></div>', unsafe_allow_html=True)
    
    time.sleep(5)
