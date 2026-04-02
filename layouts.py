import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- FUNÇÕES DE PERSISTÊNCIA ---
def salvar_eixos(div_spreed, dol):
    with open("config_axis.txt", "w") as f:
        f.write(f"{div_spreed},{dol}")

def carregar_eixos():
    if os.path.exists("config_axis.txt"):
        try:
            with open("config_axis.txt", "r") as f:
                dados = f.read().split(",")
                return float(dados[0]), float(dados[1])
        except: pass
    return 0.0, 0.0

div_spreed_salvo, eixo_dol_salvo = carregar_eixos()

if 'market_data' not in st.session_state:
    st.session_state.market_data = {}
if 'last_p' not in st.session_state:
    st.session_state.last_p = {}
if 'div_spreed_mem' not in st.session_state:
    st.session_state.div_spreed_mem = div_spreed_salvo
if 'a_dol_mem' not in st.session_state:
    st.session_state.a_dol_mem = eixo_dol_salvo

# --- CSS: DESIGN TERMINAL REESTRUTURADO E FINO ---
st.markdown("""
<style>
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    
    [data-testid="column"] { display: flex; flex-direction: column; justify-content: flex-start; gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { gap: 12px !important; margin-bottom: 0px !important; }

    .header-container { text-align: center; padding: 2px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 5px; position: relative; }
    .main-title { margin: 0px; line-height: 1.0; font-size: 26px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    
    .clock-row { display: flex; justify-content: center; gap: 20px; padding: 2px 0; font-weight: bold; font-size: 11px; font-family: monospace; }
    .clock-item { color: #AAA; }
    .br-green { color: #00ff00; }
    .white-time { color: #ffffff; }
    .date-container { position: absolute; bottom: 5px; right: 10px; font-family: monospace; font-size: 11px; font-weight: bold; color: #ffffff; }
    
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 5px; text-transform: uppercase; font-size: 11px; }
    
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; margin-bottom: 0px; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 10px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 12px; }
    
    .asset-name { font-size: 12px; color: #fff; text-align: left; font-weight: bold; padding-left: 8px; }
    .price-col { font-weight: bold; color: #ffffff !important; }
    .f-up { background-color: #00ff00aa !important; }
    .f-dn { background-color: #ff0000aa !important; }
    
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; align-items: center; }
    
    .bar-wrapper-full { background: #0a141a; padding: 6px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; margin-top: 5px; }
    .force-scale { display: flex; justify-content: space-between; font-size: 8px; font-family: monospace; color: #AAA; margin-bottom: 2px; padding: 0 5px; }
    .force-container-dual { background: #111; height: 10px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 11px; font-weight: 900; line-height: 1; margin-top: 4px; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    
    .txt-green { color: #00ff88 !important; }
    .txt-yellow { color: #ffff00 !important; }
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
        data = {"at": d['Close'].iloc[-1] * m, "cl": (ref_close or d['Open'].iloc[0]) * m, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s)

def calcular_k97_total(div_spreed, p_ewz_atual, eixo_dol, spot_data):
    try:
        if not spot_data or p_ewz_atual == 0: return None
        amp = spot_data['mx'] - spot_data['mn']
        v_spreed = amp / 8
        folga = v_spreed / 2 
        max_original, min_original = eixo_dol + (amp * 0.75), eixo_dol - (amp * 0.25)
        dolar_medio = ((max_original + min_original) / 2) - v_spreed
        elastico_calculado = abs(eixo_dol - ((spot_data['mx'] + spot_data['mn']) / 2)) + folga
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = 0, 0
        seta_txt, seta_cor, piscando = "", "#000000", False
        if elastico_calculado > 0 and div_spreed > 0:
            calculo_pct = (abs(diff) / (elastico_calculado * div_spreed)) * 100
            if diff < 0: p_v = min(100, calculo_pct)
            else: p_r = min(100, calculo_pct)
        if p_v >= 100: seta_txt, seta_cor, piscando = "▲ REGIÃO DE COMPRA", "#00ff88", True
        elif p_r >= 100: seta_txt, seta_cor, piscando = "▼ REGIÃO DE VENDA", "#ff4d4d", True
        v_spot_pct = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
        v_ewz = ((p_ewz_atual / ewz_ref) - 1) if ewz_ref > 0 else 0
        v_final = (v_spot_pct * 0.6) - (v_ewz * 0.4)
        return {
            "vivo": eixo_dol * (1 + v_spot_pct), "dolfut_calc": eixo_dol * (1 + v_final), 
            "fraja": eixo_dol * (1 + (v_final / 2)), "medio": dolar_medio, 
            "max_fut_5": eixo_dol + (abs(eixo_dol - dolar_medio) * 10), "min_fut_5": eixo_dol - (abs(eixo_dol - dolar_medio) * 10),
            "v_v": v_final * 100, "v_spot": v_spot_pct * 100, "spreed": v_spreed, "p_v": p_v, "p_r": p_r, 
            "seta": seta_txt, "seta_cor": seta_cor, "piscando": piscando, "max_grade": max_original, "min_grade": min_original
        }
    except: return None

# --- UI E LOOP ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    input_div_val = st.number_input("DIVISOR SPREED:", value=st.session_state.div_spreed_mem, format="%.2f", key="div_spreed_input")
    input_dol_val = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol_mem, format="%.2f", key="axis_dol_input")
    if st.button("SALVAR CONFIGURAÇÕES"):
        st.session_state.div_spreed_mem, st.session_state.a_dol_mem = input_div_val, input_dol_val
        salvar_eixos(input_div_val, input_dol_val)
        st.success("Salvo!")
        time.sleep(0.5)
        st.rerun()

div_s, a_dol = st.session_state.div_spreed_mem, st.session_state.a_dol_mem
placeholder = st.empty()

while True:
    tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
    spot_raw, ewz_raw = fetch("USDBRL=X"), fetch("EWZ")
    
    # Persistência: se o fetch falhar, usa o último dado da memória
    spot_live = spot_raw if spot_raw else st.session_state.market_data.get("USDBRL=X")
    ewz_live = ewz_raw if ewz_raw else st.session_state.market_data.get("EWZ")
    
    now = datetime.now()
    dt_br = now.astimezone(tz_sp).strftime("%H:%M:%S")
    dt_ny = now.astimezone(tz_ny).strftime("%H:%M:%S")
    dt_ld = now.astimezone(tz_ld).strftime("%H:%M:%S")
    
    with placeholder.container():
        st.markdown(f'''<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1><div class="clock-row"><span class="clock-item">🇧🇷 BRASÍLIA: <span class="br-green">{dt_br}</span></span><span class="clock-item">🇺🇸 NEW YORK: <span class="white-time">{dt_ny}</span></span><span class="clock-item">🇬🇧 LONDON: <span class="white-time">{dt_ld}</span></span></div><div class="date-container">📅 {now.astimezone(tz_sp).strftime("%d/%m/%Y")}</div></div>''', unsafe_allow_html=True)

        if spot_live and ewz_live:
            res = calcular_k97_total(div_s, ewz_live['at'], a_dol, spot_live)
            if res:
                v_f, d_c = res['v_v'], res['dolfut_calc']
                c_main, c_side = st.columns([2.8, 1.2])
                
                with c_main:
                    st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                    html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                    l_df = st.session_state.last_p.get('DF', d_c/1000)
                    cl_df = "f-up" if (d_c/1000) > l_df else "f-dn" if (d_c/1000) < l_df else ""
                    st.session_state.last_p['DF'] = d_c/1000
                    bg_dol = f"background-color:rgba({('0,255,0' if v_f >= 0 else '255,0,0')}, 0.1);"
                    html += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col {cl_df}' style='{bg_dol}'>{(d_c/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max_grade']/1000):.4f}</td><td>{(res['min_grade']/1000):.4f}</td><td style='color:{("#00ff00" if v_f >= 0 else "#ff4d4d")}; font-weight:bold;'>{v_f:+.2f}%</td></tr>"
                    
                    ticker_items = [f"DOLFUT: <span style='color:{("#00ff00" if v_f >= 0 else "#ff4d4d")};'>{v_f:+.2f}%</span>"]
                    outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "XAU/USD": "GC=F"}
                    
                    for lbl, sym in outros.items():
                        d = fetch(sym)
                        if d:
                            f = ".4f" if lbl == "DOLSPOT" else ".2f"
                            p_v = d['at']/1000 if lbl == "DOLSPOT" else d['at']
                            l_a = st.session_state.last_p.get(lbl, p_v); cl_a = "f-up" if p_v > l_a else "f-dn" if p_v < l_a else ""; st.session_state.last_p[lbl] = p_v
                            var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                            html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col {cl_a}'>{p_v:{f}}</td><td>{(d['cl']/1000 if lbl=='DOLSPOT' else d['cl']):{f}}</td><td>{(d['op']/1000 if lbl=='DOLSPOT' else d['op']):{f}}</td><td>{(d['mx']/1000 if lbl=='DOLSPOT' else d['mx']):{f}}</td><td>{(d['mn']/1000 if lbl=='DOLSPOT' else d['mn']):{f}}</td><td style='color:{("#00ff00" if var >= 0 else "#ff4d4d")}; font-weight:bold;'>{var:+.2f}%</td></tr>"
                            ticker_items.append(f"{lbl}: <span style='color:{("#00ff00" if var >= 0 else "#ff4d4d")};'>{var:+.2f}%</span>")
                    st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
                    st.markdown(f'''<div class="bar-wrapper-full"><div class="force-scale"><span>100%</span><span>50%</span><span>0%</span><span>50%</span><span>100%</span></div><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width: {res["p_v"]}%;"></div></div><div class="bar-side"><div class="fill-red" style="width: {res["p_r"]}%;"></div></div></div><div class="sinal-indicator {"blink" if res["piscando"] else ""}" style="color:{res["seta_cor"]};">{res["seta"]}</div></div>''', unsafe_allow_html=True)

                with c_side:
                    st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                    st.markdown(f'''<div class="calc-panel">
                        <div class="calc-row txt-green"><span>MAX FUT 5</span> <span>{res['max_fut_5']:.2f}</span></div>
                        <div style="text-align:center; padding: 4px; color: #00f2ff; font-size: 10px; font-weight: bold; border-top:1px solid #444; border-bottom:1px solid #444;">AXIS: {a_dol:.2f}</div>
                        <div class="calc-row txt-green" style="border-bottom: none;"><span>MIN FUT 5</span> <span>{res['min_fut_5']:.2f}</span></div>
                    </div>''', unsafe_allow_html=True)
                    st.markdown(f'''<div class="calc-panel"><div class="calc-row" style="border-bottom:none; padding-bottom:0px;"><span style="color:#ffffff;">DOLB3</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div><div style="text-align:right; font-size:9px; padding-right:6px; color:{("#00ff00" if res['v_spot'] >= 0 else "#ff4d4d")}; font-weight:bold; margin-bottom:4px;">{res['v_spot']:+.2f}%</div><div class="calc-row"><span style="color:#ffff00;">MÉDIA DOLAR</span> <span style="color:#00f2ff;">{res['medio']:.2f}</span></div><div class="calc-row"><span style="color:#d4a017;">PREÇO JUSTO</span> <span style="color:#ffffff;">{res['fraja']:.2f}</span></div><div class="calc-row" style="border-bottom: none;"><span style="color:#ff4d4d;">SPREED</span> <span style="color:#00f2ff;">{res['spreed']:.2f}</span></div></div>''', unsafe_allow_html=True)
                st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)}</div></div>', unsafe_allow_html=True)
        else:
            # Caso não haja dados nem na memória (primeiro boot), apenas informa discretamente
            st.info("Conectando ao fluxo de dados...")
            
    time.sleep(2)
