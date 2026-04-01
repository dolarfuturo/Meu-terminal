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

# --- CSS: DESIGN TERMINAL AJUSTADO ---
st.markdown("""
<style>
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    
    [data-testid="column"] { display: flex; flex-direction: column; justify-content: flex-start; gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { gap: 10px !important; margin-bottom: 0px !important; }

    .header-container { text-align: center; padding: 2px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 5px; position: relative; }
    .main-title { margin: 0px; line-height: 1.0; font-size: 24px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    
    .clock-row { display: flex; justify-content: center; gap: 15px; padding: 2px 0; font-weight: bold; font-size: 10px; font-family: monospace; }
    .clock-item { color: #AAA; }
    .br-green { color: #00ff00; }
    .date-container { position: absolute; bottom: 2px; right: 10px; font-family: monospace; font-size: 10px; color: #ffffff; }
    
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 4px; font-size: 10px; }
    
    .main-grid { border: 1px solid #ffffff; border-radius: 2px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 10px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 11px; }
    
    .price-col { font-weight: bold; color: #ffffff !important; }
    .f-up { background-color: #00ff0066 !important; }
    .f-dn { background-color: #ff000066 !important; }
    
    .calc-panel { border: 1px solid #ffffff; border-radius: 2px; padding: 3px; background: #0a141a; font-family: monospace; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 5px; border-bottom: 1px solid #333; font-size: 10px; font-weight: bold; }
    
    /* BARRA DE FORÇA MAIS FINA */
    .bar-wrapper-thin { background: #0a141a; padding: 5px; border: 1px solid #ffffff; border-radius: 2px; text-align: center; margin-top: 4px; }
    .force-scale { display: flex; justify-content: space-between; font-size: 8px; font-family: monospace; color: #888; margin-bottom: 2px; }
    .force-container-thin { background: #111; height: 8px; width: 100%; position: relative; overflow: hidden; display: flex; border: 1px solid #444; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; }
    .sinal-indicator { font-size: 11px; font-weight: bold; margin-top: 3px; }
    
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 50s linear infinite; font-family: 'monospace'; font-size: 11px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    
    .txt-green { color: #00ff88 !important; }
    .txt-yellow { color: #ffff00 !important; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return st.session_state.market_data.get(s)
        ref_close = t.info.get('previousClose') or d['Open'].iloc[0]
        m = 1000 if s == "USDBRL=X" else 1
        data = {"at": d['Close'].iloc[-1] * m, "cl": ref_close * m, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s)

def calcular_k97(div_spreed, p_ewz_atual, eixo_dol, spot_data):
    if not spot_data: return None
    amp = spot_data['mx'] - spot_data['mn']
    v_spreed = amp / 8
    folga = v_spreed / 2
    max_original, min_original = eixo_dol + (amp * 0.75), eixo_dol - (amp * 0.25)
    dolar_medio = ((max_original + min_original) / 2) - v_spreed
    elastico = abs(eixo_dol - dolar_medio) if abs(eixo_dol - dolar_medio) != 0 else 1.0
    dist_base = abs(eixo_dol - ((spot_data['mx'] + spot_data['mn']) / 2)) + folga
    diff = spot_data['at'] - eixo_dol
    p_v, p_r = 0, 0
    if dist_base > 0 and div_spreed > 0:
        calc = (abs(diff) / (dist_base * div_spreed)) * 100
        if diff < 0: p_v = min(100, calc)
        else: p_r = min(100, calc)
    seta = "▲ COMPRA" if p_v >= 100 else "▼ VENDA" if p_r >= 100 else ""
    cor = "#00ff88" if p_v >= 100 else "#ff4d4d" if p_r >= 100 else "#444"
    v_spot_pct = ((spot_data['at'] / spot_data['cl']) - 1)
    ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
    v_ewz = ((p_ewz_atual / ewz_ref) - 1)
    v_final = (v_spot_pct * 0.6) - (v_ewz * 0.4)
    return {
        "vivo": eixo_dol * (1 + v_spot_pct), "dolfut": eixo_dol * (1 + v_final), 
        "fraja": eixo_dol * (1 + (v_final / 2)), "medio": dolar_medio, 
        "max5": eixo_dol + (elastico * 10), "max1": eixo_dol + (elastico * 2),
        "min1": eixo_dol - (elastico * 2), "min5": eixo_dol - (elastico * 10),
        "v_v": v_final * 100, "v_spot": v_spot_pct * 100, "spreed": v_spreed, 
        "p_v": p_v, "p_r": p_r, "seta": seta, "seta_cor": cor, "mx_g": max_original, "mn_g": min_original
    }

# --- LOOP ---
placeholder = st.empty()
while True:
    spot, ewz = fetch("USDBRL=X"), fetch("EWZ")
    with placeholder.container():
        st.markdown(f'<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1><div class="clock-row"><span class="br-green">🇧🇷 {datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%H:%M:%S")}</span></div><div class="date-container">📅 {datetime.now().strftime("%d/%m/%Y")}</div></div>', unsafe_allow_html=True)
        
        if spot and ewz:
            res = calcular_k97(st.session_state.div_spreed_mem, ewz['at'], st.session_state.a_dol_mem, spot)
            if res:
                col_left, col_right = st.columns([2.8, 1.2])
                
                with col_left:
                    st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                    html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                    # Dados do DOLFUT Calculado
                    html += f"<tr><td style='text-align:left; padding-left:10px;'>DOLFUT</td><td class='price-col'>{(res['dolfut']/1000):.4f}</td><td>{(st.session_state.a_dol_mem/1000):.4f}</td><td>{(st.session_state.a_dol_mem/1000):.4f}</td><td>{(res['mx_g']/1000):.4f}</td><td>{(res['mn_g']/1000):.4f}</td><td style='color:#00ff00;'>{res['v_v']:+.2f}%</td></tr>"
                    # Outros ativos
                    outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ"}
                    ticker_txt = [f"DOLFUT: {res['v_v']:+.2f}%"]
                    for lbl, sym in outros.items():
                        d = fetch(sym)
                        if d:
                            v = ((d['at']/d['cl'])-1)*100
                            p_disp = d['at']/1000 if lbl=="DOLSPOT" else d['at']
                            html += f"<tr><td style='text-align:left; padding-left:10px;'>{lbl}</td><td class='price-col'>{p_disp:.4f}</td><td>{(d['cl']/1000 if lbl=='DOLSPOT' else d['cl']):.4f}</td><td>{(d['op']/1000 if lbl=='DOLSPOT' else d['op']):.4f}</td><td>{(d['mx']/1000 if lbl=='DOLSPOT' else d['mx']):.4f}</td><td>{(d['mn']/1000 if lbl=='DOLSPOT' else d['mn']):.4f}</td><td style='color:{("#00ff00" if v>=0 else "#ff4d4d")};'>{v:+.2f}%</td></tr>"
                            ticker_txt.append(f"{lbl}: {v:+.2f}%")
                    st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
                    
                    # BARRA DE FORÇA FINA LOGO ABAIXO DA GRADE
                    st.markdown(f'''<div class="bar-wrapper-thin"><div class="force-scale"><span>100%</span><span>0%</span><span>100%</span></div><div class="force-container-thin"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width: {res["p_v"]}%;"></div></div><div class="bar-side"><div class="fill-red" style="width: {res["p_r"]}%;"></div></div></div><div class="sinal-indicator" style="color:{res["seta_cor"]};">{res["seta"]}</div></div>''', unsafe_allow_html=True)

                with col_right:
                    st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                    st.markdown(f'''<div class="calc-panel">
                        <div class="calc-row txt-green"><span>MAX 5</span><span>{res['max5']:.2f}</span></div>
                        <div class="calc-row txt-green"><span>MAX 1</span><span>{res['max1']:.2f}</span></div>
                        <div style="text-align:center; font-size:9px; color:#00f2ff; padding:2px;">AXIS: {st.session_state.a_dol_mem:.2f}</div>
                        <div class="calc-row txt-green"><span>MIN 1</span><span>{res['min1']:.2f}</span></div>
                        <div class="calc-row txt-green" style="border:none;"><span>MIN 5</span><span>{res['min5']:.2f}</span></div>
                        <hr style="margin:4px 0; border:0; border-top:1px solid #444;">
                        <div class="calc-row"><span>DOLB3</span><span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
                        <div class="calc-row"><span>MÉDIA</span><span style="color:#ffff00;">{res['medio']:.2f}</span></div>
                        <div class="calc-row" style="border:none;"><span>JUSTO</span><span>{res['fraja']:.2f}</span></div>
                    </div>''', unsafe_allow_html=True)

                # RODAPÉ ABAIXO DE TUDO
                st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_txt)}</div></div>', unsafe_allow_html=True)

    time.sleep(5)
