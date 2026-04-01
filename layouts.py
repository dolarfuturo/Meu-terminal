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

# --- CSS: DESIGN TERMINAL COMPACTO ---
st.markdown("""
<style>
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    
    [data-testid="column"] { display: flex; flex-direction: column; justify-content: flex-start; gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { gap: 10px !important; margin-bottom: 0px !important; }

    .header-container { text-align: center; padding: 5px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 5px; position: relative; }
    .main-title { margin: 0px; line-height: 1.0; font-size: 26px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    
    .clock-row { display: flex; justify-content: center; gap: 20px; padding: 2px 0; font-weight: bold; font-size: 10px; font-family: monospace; }
    .clock-item { color: #AAA; }
    .br-green { color: #00ff00; }
    .white-time { color: #ffffff; }
    .date-container { position: absolute; bottom: 5px; right: 10px; font-family: monospace; font-size: 10px; font-weight: bold; color: #ffffff; }
    
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 4px; text-transform: uppercase; font-size: 10px; }
    
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; margin-bottom: 5px; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 9px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 11px; }
    
    .asset-name { font-size: 11px; color: #fff; text-align: left; font-weight: bold; padding-left: 8px; }
    .price-col { font-weight: bold; color: #ffffff !important; }
    .f-up { background-color: #00ff00aa !important; }
    .f-dn { background-color: #ff0000aa !important; }
    
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 1px 6px; border-bottom: 1px solid #333; font-size: 9px; font-weight: bold; }
    
    /* Barra de Força Horizontal (Abaixo da Grade) */
    .bar-wrapper-horizontal { background: #0a141a; padding: 8px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; margin-top: 5px; width: 100%; }
    .force-scale { display: flex; justify-content: space-between; font-size: 9px; font-family: monospace; color: #AAA; margin-bottom: 3px; }
    .force-container-dual { background: #111; height: 12px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 12px; font-weight: 900; margin-top: 5px; }
    
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 5px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 11px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    
    .txt-green { color: #00ff88 !important; }
    .txt-yellow { color: #ffff00 !important; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS --- (Mesma lógica anterior)
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return st.session_state.market_data.get(s)
        ref_close = t.info.get('previousClose')
        m = 1000 if s == "USDBRL=X" else 1
        data = {"at": d['Close'].iloc[-1] * m, "cl": (ref_close or d['Open'].iloc[0]) * m, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s)

def calcular_k97_total(div_spreed, p_ewz_atual, eixo_dol, spot_data):
    try:
        if not spot_data: return None
        amp = spot_data['mx'] - spot_data['mn']
        v_spreed = amp / 8
        folga = v_spreed / 2 
        max_original, min_original = eixo_dol + (amp * 0.75), eixo_dol - (amp * 0.25)
        dolar_medio = ((max_original + min_original) / 2) - v_spreed
        elastico_calculado = abs(eixo_dol - dolar_medio) if abs(eixo_dol - dolar_medio) != 0 else 1.0
        media_pura_barra = (spot_data['mx'] + spot_data['mn']) / 2
        dist_base_barra = abs(eixo_dol - media_pura_barra) + folga
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = 0, 0
        seta_txt, seta_cor, piscando = "", "#000000", False
        if dist_base_barra > 0 and div_spreed > 0:
            calculo_pct = (abs(diff) / (dist_base_barra * div_spreed)) * 100
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
            "max_fut_5": eixo_dol + (elastico_calculado * 10), "max_fut_1": eixo_dol + (elastico_calculado * 2),
            "min_fut_1": eixo_dol - (elastico_calculado * 2), "min_fut_5": eixo_dol - (elastico_calculado * 10),
            "v_v": v_final * 100, "v_spot": v_spot_pct * 100, "spreed": v_spreed, "p_v": p_v, "p_r": p_r, 
            "seta": seta_txt, "seta_cor": seta_cor, "piscando": piscando, "max_grade": max_original, "min_grade": min_original
        }
    except: return None

# --- UI E LOOP ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    input_div_val = st.number_input("DIVISOR SPREED:", value=st.session_state.div_spreed_mem, format="%.2f")
    input_dol_val = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol_mem, format="%.2f")
    if st.button("SALVAR"):
        st.session_state.div_spreed_mem, st.session_state.a_dol_mem = input_div_val, input_dol_val
        salvar_eixos(input_div_val, input_dol_val)
        st.rerun()

placeholder = st.empty()

while True:
    tz_sp = pytz.timezone('America/Sao_Paulo')
    spot_live, ewz_live = fetch("USDBRL=X"), fetch("EWZ")
    now = datetime.now(tz_sp)
    
    with placeholder.container():
        st.markdown(f'''<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1><div class="clock-row"><span class="clock-item">🇧🇷 BRASÍLIA: <span class="br-green">{now.strftime("%H:%M:%S")}</span></span></div><div class="date-container">📅 {now.strftime("%d/%m/%Y")}</div></div>''', unsafe_allow_html=True)

        if spot_live and ewz_live:
            res = calcular_k97_total(div_spreed_salvo, ewz_live['at'], eixo_dol_salvo, spot_live)
            if res:
                c_main, c_side = st.columns([2.5, 1.5])
                
                with c_main:
                    st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                    html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                    outros = {"DOLFUT": "FUT", "DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ"}
                    ticker_items = []
                    for lbl, sym in outros.items():
                        d = fetch(sym) if sym != "FUT" else {"at": res['dolfut_calc'], "cl": eixo_dol_salvo, "op": eixo_dol_salvo, "mx": res['max_grade'], "mn": res['min_grade']}
                        if d:
                            p_v = d['at']/1000 if lbl in ["DOLSPOT", "DOLFUT"] else d['at']
                            var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                            html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{p_v:.4f}</td><td>{d['cl']/1000 if lbl in ['DOLSPOT', 'DOLFUT'] else d['cl']:.4f}</td><td>{d['op']/1000 if lbl in ['DOLSPOT', 'DOLFUT'] else d['op']:.4f}</td><td>{d['mx']/1000 if lbl in ['DOLSPOT', 'DOLFUT'] else d['mx']:.4f}</td><td>{d['mn']/1000 if lbl in ['DOLSPOT', 'DOLFUT'] else d['mn']:.4f}</td><td style='color:{("#00ff00" if var >= 0 else "#ff4d4d")}; font-weight:bold;'>{var:+.2f}%</td></tr>"
                            ticker_items.append(f"{lbl}: {var:+.2f}%")
                    st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
                    
                    # BARRA DE FORÇA AGORA ABAIXO DA GRADE
                    st.markdown(f'''<div class="bar-wrapper-horizontal"><div class="force-scale"><span>100%</span><span>50%</span><span>0%</span><span>50%</span><span>100%</span></div><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width: {res["p_v"]}%;"></div></div><div class="bar-side"><div class="fill-red" style="width: {res["p_r"]}%;"></div></div></div><div class="sinal-indicator {"blink" if res["piscando"] else ""}" style="color:{res["seta_cor"]};">{res["seta"]}</div></div>''', unsafe_allow_html=True)

                with c_side:
                    st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                    st.markdown(f'''<div class="calc-panel">
                        <div class="calc-row txt-green"><span>MAX FUT 5</span> <span>{res['max_fut_5']:.2f}</span></div>
                        <div class="calc-row txt-green"><span>MAX FUT 1</span> <span>{res['max_fut_1']:.2f}</span></div>
                        <div style="text-align:center; padding: 2px; color: #00f2ff; font-size: 10px; font-weight: bold; border-top:1px solid #444; border-bottom:1px solid #444;">AXIS: {eixo_dol_salvo:.2f}</div>
                        <div class="calc-row txt-green"><span>MIN FUT 1</span> <span>{res['min_fut_1']:.2f}</span></div>
                        <div class="calc-row txt-green"><span>MIN FUT 5</span> <span>{res['min_fut_5']:.2f}</span></div>
                    </div>''', unsafe_allow_html=True)
                    st.markdown(f'''<div class="calc-panel"><div class="calc-row"><span>DOLB3</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div><div class="calc-row"><span>MÉDIA</span> <span style="color:#ffff00;">{res['medio']:.2f}</span></div><div class="calc-row"><span>JUSTO</span> <span style="color:#ffffff;">{res['fraja']:.2f}</span></div></div>''', unsafe_allow_html=True)

                st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)}</div></div>', unsafe_allow_html=True)
        else: st.warning("AGUARDANDO DADOS...")
    time.sleep(5)
