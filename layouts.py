import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime
import pytz

# Configuração para Tablet - Terminal K97
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- FUNÇÕES DE PERSISTÊNCIA ---
def salvar_eixos(div_spreed, dol, axis_fut):
    with open("config_axis.txt", "w") as f:
        f.write(f"{div_spreed},{dol},{axis_fut}")

def carregar_eixos():
    if os.path.exists("config_axis.txt"):
        try:
            with open("config_axis.txt", "r") as f:
                dados = f.read().split(",")
                return float(dados[0]), float(dados[1]), float(dados[2])
        except: pass
    return 8.0, 5246.0, 5246.0

div_sp_salvo, eixo_dol_salvo, axis_fut_salvo = carregar_eixos()

# Gerenciamento de Estado
for key, val in [('market_data', {}), ('last_p', {}), ('div_spreed_mem', div_sp_salvo), ('a_dol_mem', eixo_dol_salvo), ('a_fut_mem', axis_fut_salvo)]:
    if key not in st.session_state: st.session_state[key] = val

# --- CSS INTERFACE K97 ---
st.markdown("""
<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; position: relative; }
    .main-title { margin: 0px; line-height: 1.2; font-size: 28px; font-family: monospace; }
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 5px; text-transform: uppercase; font-size: 11px; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 10px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 12px; }
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-top: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; }
    .txt-green { color: #00ff88 !important; } .txt-yellow { color: #ffff00 !important; } .txt-red { color: #ff4d4d !important; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return st.session_state.market_data.get(s, {"at":0.0,"cl":1.0,"op":0.0,"mx":0.0,"mn":0.0})
        m = 1000 if s == "USDBRL=X" else 1
        data = {"at": float(d['Close'].iloc[-1]*m), "cl": float(t.info.get('previousClose', d['Open'].iloc[0])*m), "op": float(d['Open'].iloc[0]*m), "mx": float(d['High'].max()*m), "mn": float(d['Low'].min()*m)}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s, {"at":0.0,"cl":1.0,"op":0.0,"mx":0.0,"mn":0.0})

# --- HIERARQUIA DE CÁLCULOS K97 ---
def calcular_k97(frp, eixo_dol, spot, dxy, ewz):
    try:
        # 1. MÉDIA DOLAR: (Max + Min) / 2
        medio = (spot['mx'] + spot['mn']) / 2
        
        # 2. SPREED T: Range total e SPREED: 50% do range
        spreed_t = spot['mx'] - spot['mn']
        spreed_50 = spreed_t / 2
        
        # 3. PREÇO JUSTO: Spot + FRP (Valor fixo ADM)
        justo = spot['at'] + frp
        
        # 4. DOLB3: Média + % (DXY 70% / EWZ 30%)
        v_dxy = (dxy['at'] / dxy['cl'] - 1) if dxy['cl'] > 0 else 0
        v_ewz = (ewz['at'] / ewz['cl'] - 1) if ewz['cl'] > 0 else 0
        pct_ajuste = (v_dxy * 0.7) - (v_ewz * 0.3)
        vivo_val = medio * (1 + pct_ajuste)
        
        # Grade de Elástico
        el = abs(eixo_dol - medio) if abs(eixo_dol - medio) != 0 else 1.0
        
        return {
            "vivo": vivo_val, "pct": pct_ajuste * 100, "medio": medio, 
            "justo": justo, "spreed_t": spreed_t, "spreed_50": spreed_50,
            "max5": eixo_dol + (el * 10), "max1": eixo_dol + (el * 2),
            "min1": eixo_dol - (el * 2), "min5": eixo_dol - (el * 10)
        }
    except: return None

# --- UI & LOOP ---
with st.sidebar:
    st.markdown("### ⚙️ ADM K97")
    i_frp = st.number_input("FRP (JUSTO):", value=st.session_state.div_spreed_mem)
    i_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol_mem)
    if st.button("ATUALIZAR"):
        st.session_state.div_spreed_mem, st.session_state.a_dol_mem = i_frp, i_dol
        salvar_eixos(i_frp, i_dol, 0); st.rerun()

placeholder = st.empty()
while True:
    spot, dxy, ewz = fetch("USDBRL=X"), fetch("DX-Y.NYB"), fetch("EWZ")
    res = calcular_k97(st.session_state.div_spreed_mem, st.session_state.a_dol_mem, spot, dxy, ewz)
    
    with placeholder.container():
        st.markdown(f'<div class="header-container"><h1 class="main-title"><span style="color:#00BFFF;">BAIR</span><span style="color:#FFD700;"> - TERMINAL K97</span></h1></div>', unsafe_allow_html=True)
        
        if res:
            c1, c2 = st.columns([2.8, 1.2])
            with c1:
                st.markdown('<div class="section-title">GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                html = '<div class="main-grid"><table class="terminal-table"><thead><tr><th>ATIVO</th><th>PREÇO</th><th>MÁXIMA</th><th>MÍNIMA</th><th>VAR%</th></tr></thead><tbody>'
                for lbl, d in [("DOLSPOT", spot), ("DXY", dxy), ("EWZ", ewz)]:
                    p_v = d['at']/1000 if lbl == "DOLSPOT" else d['at']
                    var = (d['at']/d['cl'] - 1) * 100
                    cor = "#00ff88" if var >= 0 else "#ff4d4d"
                    html += f"<tr><td>{lbl}</td><td style='font-weight:bold;'>{p_v:.4f if lbl=='DOLSPOT' else p_v:.2f}</td><td>{d['mx']/(1000 if lbl=='DOLSPOT' else 1):.2f}</td><td>{d['mn']/(1000 if lbl=='DOLSPOT' else 1):.2f}</td><td style='color:{cor};'>{var:+.2f}%</td></tr>"
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="section-title">HIERARQUIA DE CÁLCULO</div>', unsafe_allow_html=True)
                st.markdown(f'''<div class="calc-panel">
                    <div class="calc-row"><span style="color:#ffffff;">DOLB3 (VIVO)</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
                    <div class="calc-row"><span style="color:#ffff00;">MÉDIA DOLAR</span> <span>{res['medio']:.2f}</span></div>
                    <div class="calc-row"><span style="color:#d4a017;">PREÇO JUSTO</span> <span>{res['justo']:.2f}</span></div>
                    <div class="calc-row"><span style="color:#ff4d4d;">SPREED T (RANGE)</span> <span>{res['spreed_t']:.2f}</span></div>
                    <div class="calc-row" style="border:none;"><span style="color:#00BFFF;">SPREED (50%)</span> <span>{res['spreed_50']:.2f}</span></div>
                </div>''', unsafe_allow_html=True)
                
    time.sleep(5)
