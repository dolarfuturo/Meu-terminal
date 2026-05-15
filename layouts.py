import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- FUNÇÕES DE PERSISTÊNCIA ---
def salvar_eixos(frp, dol, axis_fut):
    with open("config_axis.txt", "w") as f:
        f.write(f"{frp},{dol},{axis_fut}")

def carregar_eixos():
    if os.path.exists("config_axis.txt"):
        try:
            with open("config_axis.txt", "r") as f:
                dados = f.read().split(",")
                d1 = float(dados[0])
                d2 = float(dados[1])
                d3 = float(dados[2]) if len(dados) > 2 else d2
                return d1, d2, d3
        except: pass
    return 8.0, 5246.0, 5246.0

frp_salvo, eixo_dol_salvo, axis_fut_salvo = carregar_eixos()

if 'market_data' not in st.session_state: st.session_state.market_data = {}
if 'last_p' not in st.session_state: st.session_state.last_p = {}
if 'frp_mem' not in st.session_state: st.session_state.frp_mem = frp_salvo
if 'a_dol_mem' not in st.session_state: st.session_state.a_dol_mem = eixo_dol_salvo
if 'a_fut_mem' not in st.session_state: st.session_state.a_fut_mem = axis_fut_salvo

# --- CSS ---
st.markdown("""
<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    [data-testid="column"] { display: flex; flex-direction: column; justify-content: flex-start; gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { gap: 12px !important; margin-bottom: 0px !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; position: relative; }
    .main-title { margin: 0px; line-height: 1.2; font-size: 28px; font-family: monospace; padding-bottom: 5px; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .clock-row { display: flex; justify-content: center; gap: 15px; padding: 2px 0; font-weight: bold; font-size: 11px; font-family: monospace; }
    .clock-item { color: #AAA; }
    .br-green { color: #00ff00; }
    .white-time { color: #ffffff; }
    .utc-gold { color: #FFD700; }
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
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; margin-top: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; align-items: center; }
    .bar-wrapper-full { background: #0a141a; padding: 6px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; margin-top: 5px; }
    .force-scale { display: flex; justify-content: space-between; font-size: 8px; font-family: monospace; color: #AAA; margin-bottom: 2px; padding: 0 5px; }
    .force-container-dual { background: #111; height: 10px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 11px; font-weight: 900; line-height: 1; margin-top: 4px; }
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .txt-green { color: #00ff88 !important; }
    .txt-yellow { color: #ffff00 !important; }
    .txt-red { color: #ff4d4d !important; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    fallback = {"at": 0.0, "cl": 1.0, "op": 0.0, "mx": 0.0, "mn": 0.0}
    try:
        t = yf.Ticker(s)
        if s == "^TNX":
            info = t.fast_info
            d = t.history(period="1d", interval="1m")
            if d.empty: return st.session_state.market_data.get(s, fallback)
            data = {"at": float(info.last_price), "cl": float(info.previous_close if info.previous_close else d['Open'].iloc[0]), "op": float(d['Open'].iloc[0]), "mx": float(d['High'].max()), "mn": float(d['Low'].min())}
        else:
            d = t.history(period="1d", interval="1m", prepost=True)
            if d.empty: return st.session_state.market_data.get(s, fallback)
            ref_close = t.info.get('previousClose')
            if not ref_close: ref_close = d['Open'].iloc[0]
            m = 1000 if s == "USDBRL=X" else 1
            data = {"at": float(d['Close'].iloc[-1] * m), "cl": float(ref_close * m), "op": float(d['Open'].iloc[0] * m), "mx": float(d['High'].max() * m), "mn": float(d['Low'].min() * m)}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s, fallback)

# --- CÁLCULOS K97 ---
def calcular_k97_total(frp_adm, p_ewz_atual, eixo_dol, spot_data):
    try:
        if not spot_data or p_ewz_atual == 0: return None
        
        # 1. MÉDIA REAL DO SPOT
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        
        # 2. PREÇO JUSTO (SPOT + FRP do ADM)
        preço_justo = spot_data['at'] + frp_adm
        
        # 3. DOLB3 (MÉDIA + VARIAÇÃO DXY/EWZ)
        dxy_data = fetch("DX-Y.NYB")
        v_dxy = ((dxy_data['at'] / dxy_data['cl']) - 1) if dxy_data['cl'] > 0 else 0
        ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
        v_ewz = ((p_ewz_atual / ewz_ref) - 1) if ewz_ref > 0 else 0
        calc_variacoes_pct = (v_dxy * 0.7) - (v_ewz * 0.3)
        vivo_val = dolar_medio * (1 + calc_variacoes_pct)

        # 4. SPREEDS (CONFORME SOLICITADO)
        amp_total = spot_data['mx'] - spot_data['mn']
        spreed_metade = amp_total / 2 # O SPREED É A METADE DO SPREED T
        
        # Resto da lógica de força
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = 0, 0
        seta_txt, seta_cor, piscando = "", "#000000", False
        if spreed_metade > 0:
            calculo_pct = (abs(diff) / (spreed_metade * 5.0)) * 100 
            if diff < 0: p_v = min(100, calculo_pct)
            else: p_r = min(100, calculo_pct)
            
        if p_v >= 100: seta_txt, seta_cor, piscando = "▲ REGIÃO DE COMPRA", "#00ff88", True
        elif p_r >= 100: seta_txt, seta_cor, piscando = "▼ REGIÃO DE VENDA", "#ff4d4d", True
        
        v_spot_pct = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        v_final = (v_spot_pct * 0.6) - (v_ewz * 0.4)
        elastico = abs(eixo_dol - dolar_medio) if abs(eixo_dol - dolar_medio) != 0 else 1.0
        
        return {
            "vivo": vivo_val, "vivo_pct": calc_variacoes_pct * 100, "dolfut_calc": eixo_dol * (1 + v_final), 
            "justo": preço_justo, "medio": dolar_medio, "frp": frp_adm,
            "spreed": spreed_metade, "spreed_t": amp_total,
            "max_fut_5": eixo_dol + (elastico * 10), "max_fut_1": eixo_dol + (elastico * 2),
            "min_fut_1": eixo_dol - (elastico * 2), "min_fut_5": eixo_dol - (elastico * 10),
            "v_v": v_final * 100, "p_v": p_v, "p_r": p_r, 
            "seta": seta_txt, "seta_cor": seta_cor, "piscando": piscando,
            "max_grade": eixo_dol + (amp_total * 0.75), "min_grade": eixo_dol - (amp_total * 0.25)
        }
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    i_frp = st.number_input("SPREED DO DIA (FRP):", value=st.session_state.frp_mem, format="%.2f")
    i_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol_mem, format="%.2f")
    i_fut = st.number_input("AXIS FUT:", value=st.session_state.a_fut_mem, format="%.2f")
    if st.button("SALVAR CONFIGURAÇÕES"):
        st.session_state.frp_mem, st.session_state.a_dol_mem, st.session_state.a_fut_mem = i_frp, i_dol, i_fut
        salvar_eixos(i_frp, i_dol, i_fut); st.success("Salvo!"); time.sleep(0.5); st.rerun()

frp_val, a_dol, a_fut = st.session_state.frp_mem, st.session_state.a_dol_mem, st.session_state.a_fut_mem
placeholder = st.empty()

# --- LOOP ---
while True:
    spot_live, ewz_live = fetch("USDBRL=X"), fetch("EWZ")
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    with placeholder.container():
        st.markdown(f'''<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1><div class="clock-row">📅 {now.strftime("%d/%m/%Y")} | 🇧🇷 {now.strftime("%H:%M:%S")}</div></div>''', unsafe_allow_html=True)
        res = calcular_k97_total(frp_val, ewz_live['at'] if ewz_live else 0, a_dol, spot_live)
        if res:
            c1, c2 = st.columns([2.8, 1.2])
            with c1:
                st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                html += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['dolfut_calc']/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max_grade']/1000):.4f}</td><td>{(res['min_grade']/1000):.4f}</td><td style='color:{("#00ff00" if res['v_v'] >= 0 else "#ff4d4d")};'>{res['v_v']:+.2f}%</td></tr>"
                for lbl, sym in {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ"}.items():
                    d = fetch(sym)
                    p = d['at']/1000 if lbl=="DOLSPOT" else d['at']
                    var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                    html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{p:.4f if lbl=='DOLSPOT' else p:.2f}</td><td>{(d['cl']/1000 if lbl=='DOLSPOT' else d['cl']):.2f}</td><td>{(d['mx']/1000 if lbl=='DOLSPOT' else d['mx']):.2f}</td><td>{(d['mn']/1000 if lbl=='DOLSPOT' else d['mn']):.2f}</td><td style='color:{("#00ff00" if var >= 0 else "#ff4d4d")};'>{var:+.2f}%</td></tr>"
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
                st.markdown(f'''<div class="bar-wrapper-full"><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width: {res["p_v"]}%;"></div></div><div class="bar-side"><div class="fill-red" style="width: {res["p_r"]}%;"></div></div></div><div class="sinal-indicator {"blink" if res["piscando"] else ""}" style="color:{res["seta_cor"]};">{res["seta"]}</div></div>''', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                st.markdown(f'''<div class="calc-panel">
                    <div class="calc-row"><span style="color:#ffffff;">DOLB3</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div>
                    <div style="text-align:right; font-size:9px; color:{("#00ff00" if res['vivo_pct'] >= 0 else "#ff4d4d")}; font-weight:bold; padding-right:6px;">{res['vivo_pct']:+.2f}%</div>
                    <div class="calc-row"><span style="color:#ffff00;">MÉDIA DOLAR</span> <span style="color:#00f2ff;">{res['medio']:.2f}</span></div>
                    <div class="calc-row"><span style="color:#d4a017;">PREÇO JUSTO</span> <span style="color:#ffffff;">{res['justo']:.2f}</span></div>
                    <div class="calc-row"><span style="color:#ff4d4d;">FRP (ADM)</span> <span style="color:#00f2ff;">{res['frp']:.2f}</span></div>
                    <div class="calc-row"><span style="color:#00BFFF;">SPREED</span> <span style="color:#00f2ff;">{res['spreed']:.2f}</span></div>
                    <div class="calc-row" style="border-bottom:none;"><span style="color:#ffffff;">SPREED T</span> <span style="color:#ffffff;">{res['spreed_t']:.2f}</span></div>
                </div>''', unsafe_allow_html=True)
    time.sleep(5)
