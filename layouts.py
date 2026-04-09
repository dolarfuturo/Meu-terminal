import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- PERSISTÊNCIA ---
def salvar_config(div, dol, spot_manual):
    with open("config_v2.txt", "w") as f:
        f.write(f"{div},{dol},{spot_manual}")

def carregar_config():
    if os.path.exists("config_v2.txt"):
        try:
            with open("config_v2.txt", "r") as f:
                d = f.read().split(",")
                return float(d[0]), float(d[1]), float(d[2])
        except: pass
    return 8.0, 5246.0, 0.0

c_div, c_dol, c_spot = carregar_config()

if 'market_data' not in st.session_state: st.session_state.market_data = {}
if 'div_mem' not in st.session_state: st.session_state.div_mem = c_div
if 'dol_mem' not in st.session_state: st.session_state.dol_mem = c_dol
if 'spot_mem' not in st.session_state: st.session_state.spot_mem = c_spot

# --- CSS (ESTILO TERMINAL) ---
st.markdown("""
<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    [data-testid="stHorizontalBlock"] { gap: 12px !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; position: relative; }
    .main-title { margin: 0px; line-height: 1.2; font-size: 28px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .clock-row { display: flex; justify-content: center; gap: 15px; font-weight: bold; font-size: 11px; font-family: monospace; color: #AAA; }
    .br-green { color: #00ff00; }
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 5px; font-size: 11px; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; font-size: 10px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 12px; }
    .asset-name { font-size: 12px; color: #fff; text-align: left; font-weight: bold; padding-left: 8px; }
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-top: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; }
    .bar-wrapper-full { background: #0a141a; padding: 6px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; margin-top: 5px; }
    .force-container-dual { background: #111; height: 10px; width: 100%; position: relative; display: flex; border: 1px solid #444; margin: 5px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .fill-green { background: #00ff88; float: right; height: 100%; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; }
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    .txt-green { color: #00ff88 !important; }
    .txt-red { color: #ff4d4d !important; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s, manual_close=0.0):
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        
        if s == "USDBRL=X":
            d_hist = t.history(period="5d", interval="1m", prepost=True)
            if d_hist.empty: return st.session_state.market_data.get(s)
            d_hist.index = d_hist.index.tz_convert(tz_sp)
            hoje = datetime.now(tz_sp).date()
            
            # Lógica do Close: Prioriza o Manual, se 0.0 usa a trava de 18:30
            if manual_close > 0:
                ref_close = manual_close / 1000
            else:
                dias_anteriores = d_hist[d_hist.index.date < hoje]
                ref_close = t.info.get('previousClose', 0)
                if not dias_anteriores.empty:
                    ult_dia = dias_anteriores.index.date[-1]
                    f_janela = dias_anteriores.loc[dias_anteriores.index.date == ult_dia].between_time('18:00', '18:30')
                    if not f_janela.empty: ref_close = f_janela['Close'].iloc[-1]
            
            d_hoje = d_hist[d_hist.index.date == hoje]
            if not d_hoje.empty:
                p_at, p_op = d_hoje['Close'].iloc[-1], d_hoje['Open'].iloc[0]
                p_mx, p_mn = d_hoje['High'].max(), d_hoje['Low'].min()
            else:
                p_at = d_hist['Close'].iloc[-1]
                p_op, p_mx, p_mn = p_at, p_at, p_at

            return {"at": p_at * 1000, "cl": ref_close * 1000, "op": p_op * 1000, "mx": p_mx * 1000, "mn": p_min * 1000}
        
        # Padrão para outros ativos
        d = t.history(period="1d", interval="1m", prepost=True)
        cl = t.info.get('previousClose', d['Open'].iloc[0] if not d.empty else 0)
        return {"at": d['Close'].iloc[-1], "cl": cl, "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()} if not d.empty else None
    except: return st.session_state.market_data.get(s)

def calcular_k97(div, ewz_at, eixo_dol, spot):
    if not spot or ewz_at == 0: return None
    amp = spot['mx'] - spot['mn']
    v_spreed = amp / 8
    media_barra = (spot['mx'] + spot['mn']) / 2
    diff = spot['at'] - eixo_dol
    p_v, p_r = 0, 0
    dist = (abs(eixo_dol - media_barra) + (v_spreed/2)) * div
    if dist > 0:
        pct = (abs(diff) / dist) * 100
        if diff < 0: p_v = min(100, pct)
        else: p_r = min(100, pct)
    
    v_spot = ((spot['at'] / spot['cl']) - 1) if spot['cl'] > 0 else 0
    v_ewz = ((ewz_at / st.session_state.market_data.get("EWZ", {"cl":1})['cl']) - 1)
    v_final = (v_spot * 0.6) - (v_ewz * 0.4)
    fraja = eixo_dol * (1 + (v_final / 2))
    
    return {
        "dolfut": eixo_dol * (1 + v_final), "fraja": fraja, "vivo": (eixo_dol + fraja) / 2,
        "p_v": p_v, "p_r": p_r, "v_v": v_final * 100, "spreed": v_spreed,
        "mx_g": eixo_dol + (amp * 0.75), "mn_g": eixo_dol - (amp * 0.25)
    }

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    i_div = st.number_input("DIVISOR SPREED:", value=st.session_state.div_mem)
    i_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.dol_mem)
    i_spot = st.number_input("AJUSTE MANUAL SPOT (0 = AUTO):", value=st.session_state.spot_mem, help="Digite o fechamento de ontem (ex: 5100.5)")
    if st.button("SALVAR E APLICAR"):
        st.session_state.div_mem, st.session_state.dol_mem, st.session_state.spot_mem = i_div, i_dol, i_spot
        salvar_config(i_div, i_dol, i_spot); st.rerun()

# --- INTERFACE ---
placeholder = st.empty()
while True:
    tz_sp = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz_sp)
    spot = fetch("USDBRL=X", st.session_state.spot_mem)
    ewz = fetch("EWZ")
    res = calcular_k97(st.session_state.div_mem, ewz['at'] if ewz else 0, st.session_state.dol_mem, spot)
    
    with placeholder.container():
        st.markdown(f'''<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - K97 TERMINAL</span></h1><div class="clock-row">🇧🇷 <span class="br-green">{now.strftime("%H:%M:%S")}</span> | SPOT REF: <span style="color:#FFF;">{spot["cl"] if spot else 0:.2f}</span> {"(MANUAL)" if st.session_state.spot_mem > 0 else "(AUTO)"}</div></div>''', unsafe_allow_html=True)
        
        if res:
            c1, c2 = st.columns([2.8, 1.2])
            with c1:
                st.markdown('<div class="section-title">MONITORAMENTO</div>', unsafe_allow_html=True)
                html = '<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>'
                # Linha DOLFUT
                html += f"<tr><td class='asset-name'>DOLFUT</td><td>{res['dolfut']/1000:.4f}</td><td>{st.session_state.dol_mem/1000:.4f}</td><td>{res['mx_g']/1000:.4f}</td><td>{res['mn_g']/1000:.4f}</td><td class='{("txt-green" if res["v_v"]>=0 else "txt-red")}'>{res['v_v']:+.2f}%</td></tr>"
                # Linha SPOT
                v_s = ((spot['at']/spot['cl'])-1)*100
                html += f"<tr><td class='asset-name'>DOLSPOT</td><td>{spot['at']/1000:.4f}</td><td>{spot['cl']/1000:.4f}</td><td>{spot['mx']/1000:.4f}</td><td>{spot['mn']/1000:.4f}</td><td class='{("txt-green" if v_s>=0 else "txt-red")}'>{v_s:+.2f}%</td></tr>"
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
                
                st.markdown(f'''<div class="bar-wrapper-full"><div class="force-container-dual"><div class="center-line"></div><div style="width:50%"><div class="fill-green" style="width:{res['p_v']}%"></div></div><div style="width:50%"><div class="fill-red" style="width:{res['p_r']}%"></div></div></div><div class="blink" style="color:{("#00ff88" if res["p_v"]>=100 else "#ff4d4d" if res["p_r"]>=100 else "#555")}; font-size:12px; font-weight:bold;">{("▲ COMPRA" if res["p_v"]>=100 else "▼ VENDA" if res["p_r"]>=100 else "AGUARDANDO")}</div></div>''', unsafe_allow_html=True)
            
            with c2:
                st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                st.markdown(f'''<div class="calc-panel"><div class="calc-row"><span>DOLB3</span><span style="color:#00f2ff;">{res['vivo']:.2f}</span></div><div class="calc-row"><span>PREÇO JUSTO</span><span>{res['fraja']:.2f}</span></div><div class="calc-row" style="border:none;"><span>SPREED</span><span>{res['spreed']:.2f}</span></div></div>''', unsafe_allow_html=True)
    
    time.sleep(5)
