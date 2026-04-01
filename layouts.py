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

# --- CSS: AJUSTE DE POSICIONAMENTO DO TÍTULO ---
st.markdown("""
<style>
    .block-container { padding-top: 0.2rem !important; padding-bottom: 0rem !important; max-width: 99% !important; }
    .stApp { background-color: #050a0e !important; overflow: hidden !important; }
    
    [data-testid="column"] { display: flex; flex-direction: column; gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { gap: 8px !important; }

    .header-container { 
        text-align: center; 
        padding-top: 35px; 
        padding-bottom: 5px; 
        border-bottom: 1px solid #FFD700; 
        margin-bottom: 4px; 
        position: relative; 
    }
    
    .main-title { 
        margin-bottom: -5px; 
        line-height: 1.0; 
        font-size: 24px; 
        font-family: monospace; 
    }
    
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    
    .clock-row { display: flex; justify-content: center; gap: 15px; font-size: 10px; font-family: monospace; color: #AAA; }
    .br-green { color: #00ff00; font-weight: bold; }
    
    .section-title { border: 1px solid #444; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 1px; margin-bottom: 3px; font-size: 9px; background: #0a141a; }
    
    .main-grid { border: 1px solid #ffffff; border-radius: 2px; overflow: hidden; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; font-family: 'monospace'; }
    .terminal-table th { background-color: #000; color: #d4a017; border: 0.5px solid #444; padding: 2px; font-size: 9px; }
    .terminal-table td { border: 0.5px solid #444; padding: 3px; text-align: center; font-size: 11px; color: #e0e0e0; }
    .asset-name { text-align: left !important; padding-left: 5px !important; font-weight: bold; color: #fff; }
    
    .calc-panel { border: 1px solid #ffffff; padding: 2px; background: #0a141a; font-family: monospace; margin-bottom: 3px; }
    .calc-row { display: flex; justify-content: space-between; padding: 1px 4px; border-bottom: 1px solid #333; font-size: 9px; font-weight: bold; }
    
    .bar-wrapper-full { background: #0a141a; padding: 4px; border: 1px solid #ffffff; margin-top: 3px; }
    .force-container-dual { background: #000; height: 8px; width: 100%; position: relative; display: flex; border: 1px solid #333; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .fill-green { background: #00ff88; float: right; height: 100%; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; }
    .sinal-indicator { font-size: 10px; font-weight: 900; margin-top: 2px; text-align: center; }

    .ticker-wrapper { position: fixed; bottom: 0; left: 0; width: 100%; background: #000; border-top: 1px solid #FFD700; padding: 2px 0; z-index: 999; }
    .ticker-text { display: inline-block; white-space: nowrap; animation: marquee 40s linear infinite; font-family: monospace; font-size: 10px; color: #fff; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }

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
        m = 1000 if s == "USDBRL=X" else 1
        data = {"at": d['Close'].iloc[-1]*m, "cl": (t.info.get('previousClose') or d['Open'].iloc[0])*m, "op": d['Open'].iloc[0]*m, "mx": d['High'].max()*m, "mn": d['Low'].min()*m}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s)

def calcular_k97(div_s, p_ewz, eixo_d, spot):
    if not spot: return None
    amp = spot['mx'] - spot['mn']
    v_spreed = amp / 8
    max_g, min_g = eixo_d + (amp * 0.75), eixo_d - (amp * 0.25)
    dolar_m = ((max_g + min_g) / 2) - v_spreed
    elast = abs(eixo_d - dolar_m) if abs(eixo_d - dolar_m) != 0 else 1.0
    diff = spot['at'] - eixo_d
    p_v, p_r = 0, 0
    dist = abs(eixo_d - ((spot['mx']+spot['mn'])/2)) + (v_spreed/2)
    if dist > 0 and div_s > 0:
        calc = (abs(diff)/(dist*div_s))*100
        if diff < 0: p_v = min(100, calc)
        else: p_r = min(100, calc)
    v_s_pct = (spot['at']/spot['cl'])-1
    ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
    v_e = (p_ewz/ewz_ref)-1
    v_f = (v_s_pct * 0.6) - (v_e * 0.4)
    return {
        "vivo": eixo_d*(1+v_s_pct), "dolfut": eixo_d*(1+v_f), "fraja": eixo_d*(1+(v_f/2)), "medio": dolar_m,
        "max5": eixo_d+(elast*10), "min5": eixo_d-(elast*10), "v_v": v_f*100, "v_s": v_s_pct*100,
        "p_v": p_v, "p_r": p_r, "spreed": v_spreed, "max_g": max_g, "min_g": min_g
    }

# --- LOOP PRINCIPAL ---
placeholder = st.empty()
while True:
    spot, ewz = fetch("USDBRL=X"), fetch("EWZ")
    with placeholder.container():
        now = datetime.now(pytz.timezone("America/Sao_Paulo"))
        st.markdown(f'<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1><div class="clock-row"><span>🇧🇷 BRASÍLIA: <span class="br-green">{now.strftime("%H:%M:%S")}</span></span><span>📅 {now.strftime("%d/%m/%Y")}</span></div></div>', unsafe_allow_html=True)
        
        if spot and ewz:
            res = calcular_k97(st.session_state.div_spreed_mem, ewz['at'], st.session_state.a_dol_mem, spot)
            if res:
                c1, c2 = st.columns([2.8, 1.2])
                with c1:
                    st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                    html = '<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>'
                    
                    # DOLFUT
                    html += f"<tr><td class='asset-name'>DOLFUT</td><td>{(res['dolfut']/1000):.4f}</td><td>{(st.session_state.a_dol_mem/1000):.4f}</td><td>{(res['max_g']/1000):.4f}</td><td>{(res['min_g']/1000):.4f}</td><td style='color:#00ff00;'>{res['v_v']:+.2f}%</td></tr>"
                    
                    tick_list = []
                    for lbl, sym in {"DOLSPOT":"USDBRL=X", "DXY":"DX-Y.NYB", "EWZ":"EWZ", "XAU":"GC=F"}.items():
                        d = fetch(sym)
                        if d:
                            v = ((d['at']/d['cl'])-1)*100
                            # Tratamento fixo de precisão para evitar o erro de formatação
                            if lbl == "DOLSPOT":
                                p_val, c_val = d['at']/1000, d['cl']/1000
                                html += f"<tr><td class='asset-name'>{lbl}</td><td>{p_val:.4f}</td><td>{c_val:.4f}</td><td>{(d['mx']/1000):.4f}</td><td>{(d['mn']/1000):.4f}</td><td style='color:{('#00ff00' if v>=0 else '#ff4d4d')};'>{v:+.2f}%</td></tr>"
                            else:
                                html += f"<tr><td class='asset-name'>{lbl}</td><td>{d['at']:.2f}</td><td>{d['cl']:.2f}</td><td>{d['mx']:.2f}</td><td>{d['mn']:.2f}</td><td style='color:{('#00ff00' if v>=0 else '#ff4d4d')};'>{v:+.2f}%</td></tr>"
                            tick_list.append(f"{lbl}: {v:+.2f}%")
                            
                    st.markdown(html + '</tbody></table></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="bar-wrapper-full"><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width:{res["p_v"]}%;"></div></div><div class="bar-side"><div class="fill-red" style="width:{res["p_r"]}%;"></div></div></div><div class="sinal-indicator" style="color:{"#00ff88" if res["p_v"]>=100 else "#ff4d4d" if res["p_r"]>=100 else "#aaa"};">{"▲ COMPRA" if res["p_v"]>=100 else "▼ VENDA" if res["p_r"]>=100 else "NEUTRO"}</div></div>', unsafe_allow_html=True)

                with c2:
                    st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="calc-panel"><div class="calc-row txt-green"><span>MAX 5</span><span>{res["max5"]:.2f}</span></div><div style="text-align:center; font-size:8px; color:#00f2ff; padding:2px;">AXIS: {st.session_state.a_dol_mem:.2f}</div><div class="calc-row txt-green"><span>MIN 5</span><span>{res["min5"]:.2f}</span></div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="calc-panel"><div class="calc-row"><span>DOLB3</span><span style="color:#00f2ff;">{res["vivo"]:.2f}</span></div><div class="calc-row"><span style="color:#ffff00;">MÉDIA</span><span style="color:#00f2ff;">{res["medio"]:.2f}</span></div><div class="calc-row"><span>JUSTO</span><span>{res["fraja"]:.2f}</span></div><div class="calc-row" style="border:none;"><span>SPREAD</span><span>{res["spreed"]:.2f}</span></div></div>', unsafe_allow_html=True)

                st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(tick_list)}</div></div>', unsafe_allow_html=True)
    time.sleep(5)
