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
    return 8.0, 5246.0

div_spreed_salvo, eixo_dol_salvo = carregar_eixos()

if 'market_data' not in st.session_state: st.session_state.market_data = {}
if 'last_p' not in st.session_state: st.session_state.last_p = {}
if 'div_spreed_mem' not in st.session_state: st.session_state.div_spreed_mem = div_spreed_salvo
if 'a_dol_mem' not in st.session_state: st.session_state.a_dol_mem = eixo_dol_salvo

# --- CSS REFINADO ---
st.markdown("""
<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; }
    .main-title { margin: 0px; line-height: 1.2; font-size: 28px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 5px; font-size: 11px; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 10px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 12px; }
    .price-col { font-weight: bold; color: #ffffff !important; }
    .f-up { background-color: #00ff00aa !important; }
    .f-dn { background-color: #ff0000aa !important; }
    .txt-green { color: #00ff88 !important; }
    .txt-red { color: #ff4d4d !important; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR UNIFICADO (SISTEMA SPOT PARA TODOS) ---
def fetch(s):
    try:
        # Puxamos o dia atual com intervalo de 1m para garantir o dado mais novo (estilo Spot)
        d = yf.download(s, period="1d", interval="1m", prepost=True, progress=False)
        
        if d.empty: return st.session_state.market_data.get(s)
        
        m = 1000 if s == "USDBRL=X" else 1
        last_price = d['Close'].iloc[-1] * m
        open_price = d['Open'].iloc[0] * m # Usamos a abertura do dia como referência fixa
        
        data = {
            "at": last_price, 
            "cl": open_price, # Aqui forçamos o sistema do Spot: variação sobre a abertura
            "op": open_price, 
            "mx": d['High'].max() * m, 
            "mn": d['Low'].min() * m
        }
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s)

def calcular_k97_total(div_spreed, p_ewz_atual, eixo_dol, spot_data):
    try:
        if not spot_data or p_ewz_atual == 0: return None
        amp = spot_data['mx'] - spot_data['mn']
        v_spreed = amp / 8
        dolar_medio = ((eixo_dol + (amp * 0.75) + eixo_dol - (amp * 0.25)) / 2) - v_spreed
        
        v_spot_pct = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
        v_ewz = ((p_ewz_atual / ewz_ref) - 1) if ewz_ref > 0 else 0
        v_final = (v_spot_pct * 0.6) - (v_ewz * 0.4)
        
        return {
            "vivo": (eixo_dol + (eixo_dol * (1 + (v_final / 2)))) / 2,
            "dolfut_calc": eixo_dol * (1 + v_final),
            "v_v": v_final * 100,
            "max_grade": eixo_dol + (amp * 0.75),
            "min_grade": eixo_dol - (amp * 0.25)
        }
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    i_div = st.number_input("DIVISOR SPREED:", value=st.session_state.div_spreed_mem)
    i_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol_mem)
    if st.button("SALVAR"):
        st.session_state.div_spreed_mem, st.session_state.a_dol_mem = i_div, i_dol
        salvar_eixos(i_div, i_dol); st.rerun()

div_s, a_dol = st.session_state.div_spreed_mem, st.session_state.a_dol_mem
placeholder = st.empty()

# --- LOOP PRINCIPAL ---
while True:
    spot_live, ewz_live = fetch("USDBRL=X"), fetch("EWZ")
    res = calcular_k97_total(div_s, ewz_live['at'] if ewz_live else 0, a_dol, spot_live)
    
    with placeholder.container():
        st.markdown(f'<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - K97 TERMINAL</span></h1></div>', unsafe_allow_html=True)
        
        if res:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown('<div class="section-title">MONITORAMENTO EM TEMPO REAL</div>', unsafe_allow_html=True)
                html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Ref (Open)</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                
                # Lista de ativos para o grid
                ativos = {"DOLFUT": None, "DOLSPOT": "USDBRL=X", "US10Y": "^TNX", "DXY": "DX-Y.NYB", "EWZ": "EWZ"}
                
                for lbl, sym in ativos.items():
                    if lbl == "DOLFUT":
                        p, r, v = res['dolfut_calc']/1000, a_dol/1000, res['v_v']
                        mx, mn = res['max_grade']/1000, res['min_grade']/1000
                    else:
                        d = fetch(sym)
                        if not d: continue
                        p = d['at']/1000 if lbl=="DOLSPOT" else d['at']
                        r = d['cl']/1000 if lbl=="DOLSPOT" else d['cl']
                        mx, mn = (d['mx']/1000, d['mn']/1000) if lbl=="DOLSPOT" else (d['mx'], d['mn'])
                        v = ((d['at']/d['cl'])-1)*100
                    
                    f = ".4f" if lbl in ["DOLFUT", "DOLSPOT"] else ".3f" if lbl == "US10Y" else ".2f"
                    cor = "#00ff00" if v >= 0 else "#ff4d4d"
                    html += f"<tr><td>{lbl}</td><td class='price-col'>{p:{f}}</td><td>{r:{f}}</td><td>{mx:{f}}</td><td>{mn:{f}}</td><td style='color:{cor}; font-weight:bold;'>{v:+.2f}%</td></tr>"
                
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
    time.sleep(5)
