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

# --- CSS (ESTILIZAÇÃO DO TERMINAL) ---
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
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        
        if s == "USDBRL=X":
            d_hist = t.history(period="5d", interval="1m", prepost=True)
            if d_hist.empty: return st.session_state.market_data.get(s)
            
            d_hist.index = d_hist.index.tz_convert(tz_sp)
            hoje = datetime.now(tz_sp).date()
            
            # 1. BUSCAR O CLOSE REAL (TRAVADO NAS 18:30 DE ONTEM)
            dias_anteriores = d_hist[d_hist.index.date < hoje]
            ref_close = t.info.get('previousClose')
            
            if not dias_anteriores.empty:
                ult_dia = dias_anteriores.index.date[-1]
                df_ontem = dias_anteriores.loc[dias_anteriores.index.date == ult_dia]
                # Pega a janela final do pregão e seleciona o último candle disponível até as 18:30:59
                f_janela = df_ontem.between_time('18:00', '18:30')
                if not f_janela.empty:
                    ref_close = f_janela['Close'].iloc[-1]
            
            # 2. DADOS DE HOJE
            d_hoje = d_hist[d_hist.index.date == hoje]
            if not d_hoje.empty:
                p_atual = d_hoje['Close'].iloc[-1]
                p_open = d_hoje['Open'].iloc[0]
                p_max = d_hoje['High'].max()
                p_min = d_hoje['Low'].min()
            else:
                p_atual = d_hist['Close'].iloc[-1]
                p_open, p_max, p_min = p_atual, p_atual, p_atual

            data = {"at": p_atual * 1000, "cl": ref_close * 1000, "op": p_open * 1000, "mx": p_max * 1000, "mn": p_min * 1000}
        
        else:
            d = t.history(period="1d", interval="1m", prepost=True)
            if d.empty: return st.session_state.market_data.get(s)
            ref_close = t.info.get('previousClose')
            if s == "EWZ":
                d_ewz = t.history(period="3d", interval="1m", prepost=True)
                if not d_ewz.empty:
                    d_ewz.index = d_ewz.index.tz_convert(tz_sp)
                    u_d = sorted(list(set(d_ewz.index.date)))
                    d_ant = u_d[-2] if len(u_d) > 1 else u_d[0]
                    f_21h = d_ewz.between_time('05:00', '21:00').loc[d_ewz.index.date == d_ant]
                    if not f_21h.empty: ref_close = f_21h['Close'].iloc[-1]
            
            data = {"at": d['Close'].iloc[-1], "cl": ref_close or d['Open'].iloc[0], "op": d['Open'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}

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
        elastico_calculado = abs(eixo_dol - dolar_medio) if abs(eixo_dol - dolar_medio) != 0 else 1.0
        media_pura_barra = (spot_data['mx'] + spot_data['mn']) / 2
        
        val_x = eixo_dol - (eixo_dol - media_pura_barra - folga)
        val_y = eixo_dol + (eixo_dol - media_pura_barra + folga)
        alvo_low = spot_data['mn'] + (eixo_dol - val_x)
        alvo_high = spot_data['mx'] + (val_y - eixo_dol)

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
        fraja_val = eixo_dol * (1 + (v_final / 2))
        vivo_val = (eixo_dol + fraja_val) / 2
        return {
            "vivo": vivo_val, "dolfut_calc": eixo_dol * (1 + v_final), "fraja": fraja_val, "medio": dolar_medio, 
            "max_fut_5": eixo_dol + (elastico_calculado * 10), "max_fut_4": eixo_dol + (elastico_calculado * 8),
            "max_fut_3": eixo_dol + (elastico_calculado * 6), "max_fut_2": eixo_dol + (elastico_calculado * 4),
            "max_fut_1": eixo_dol + (elastico_calculado * 2), "min_fut_1": eixo_dol - (elastico_calculado * 2),
            "min_fut_2": eixo_dol - (elastico_calculado * 4), "min_fut_3": eixo_dol - (elastico_calculado * 6),
            "min_fut_4": eixo_dol - (elastico_calculado * 8), "min_fut_5": eixo_dol - (elastico_calculado * 10),
            "v_v": v_final * 100, "v_spot": v_spot_pct * 100, "spreed": v_spreed, "p_v": p_v, "p_r": p_r, 
            "seta": seta_txt, "seta_cor": seta_cor, "piscando": piscando, "max_grade": max_original, "min_grade": min_original,
            "alvo_low": alvo_low, "alvo_high": alvo_high
        }
    except: return None

# --- SIDEBAR E LOOP ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    i_div = st.number_input("DIVISOR SPREED:", value=st.session_state.div_spreed_mem, format="%.2f")
    i_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol_mem, format="%.2f")
    if st.button("SALVAR CONFIGURAÇÕES"):
        st.session_state.div_spreed_mem, st.session_state.a_dol_mem = i_div, i_dol
        salvar_eixos(i_div, i_dol); st.rerun()

div_s, a_dol = st.session_state.div_spreed_mem, st.session_state.a_dol_mem
placeholder = st.empty()

while True:
    tz_sp, tz_ny, tz_ld, tz_utc = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London'), pytz.utc
    spot_live, ewz_live = fetch("USDBRL=X"), fetch("EWZ")
    now = datetime.now()
    
    with placeholder.container():
        st.markdown(f'''<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1><div class="clock-row">🇧🇷 BR: <span class="br-green">{now.astimezone(tz_sp).strftime("%H:%M:%S")}</span> | 🇺🇸 NY: <span class="white-time">{now.astimezone(tz_ny).strftime("%H:%M:%S")}</span> | 🌐 UTC: <span class="utc-gold">{now.astimezone(tz_utc).strftime("%H:%M:%S")}</span></div><div class="date-container">📅 {now.astimezone(tz_sp).strftime("%d/%m/%Y")}</div></div>''', unsafe_allow_html=True)
        res = calcular_k97_total(div_s, ewz_live['at'] if ewz_live else 0, a_dol, spot_live)
        if res:
            c1, c2 = st.columns([2.8, 1.2])
            with c1:
                st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                outros = {"DOLFUT": "CALC", "DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "XAU/USD": "GC=F"}
                ticker_items = []
                for lbl, sym in outros.items():
                    if lbl == "DOLFUT":
                        d = {"at": res['dolfut_calc'], "cl": a_dol, "op": a_dol, "mx": res['max_grade'], "mn": res['min_grade']}
                        p_v = d['at']/1000; var = res['v_v']
                    else:
                        d = fetch(sym)
                        if not d: continue
                        p_v = d['at']/1000 if lbl=="DOLSPOT" else d['at']
                        var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                    
                    f = ".4f" if lbl in ["DOLFUT", "DOLSPOT", "GBP/USD", "JPY/USD"] else ".2f"
                    html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{p_v:{f}}</td><td>{(d['cl']/1000 if lbl in ['DOLFUT','DOLSPOT'] else d['cl']):{f}}</td><td>{(d['op']/1000 if lbl in ['DOLFUT','DOLSPOT'] else d['op']):{f}}</td><td>{(d['mx']/1000 if lbl in ['DOLFUT','DOLSPOT'] else d['mx']):{f}}</td><td>{(d['mn']/1000 if lbl in ['DOLFUT','DOLSPOT'] else d['mn']):{f}}</td><td style='color:{("#00ff00" if var >= 0 else "#ff4d4d")};'>{var:+.2f}%</td></tr>"
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
                
                st.markdown(f'''<div class="bar-wrapper-full"><div class="force-scale"><span>100%</span><span>0%</span><span>100%</span></div><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width: {res["p_v"]}%;"></div></div><div class="bar-side"><div class="fill-red" style="width: {res["p_r"]}%;"></div></div></div><div class="sinal-indicator {"blink" if res["piscando"] else ""}" style="color:{res["seta_cor"]};">{res["seta"]}</div></div>''', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                st.markdown(f'''<div class="calc-panel">
                    <div class="calc-row txt-red"><span>MAX 5</span> <span>{res['max_fut_5']:.2f}</span></div>
                    <div class="calc-row txt-red"><span>MAX 1</span> <span>{res['max_fut_1']:.2f}</span></div>
                    <div style="text-align:center; padding: 4px; color: #00f2ff; font-size: 10px;">AXIS: {a_dol:.2f}</div>
                    <div class="calc-row txt-green"><span>MIN 1</span> <span>{res['min_fut_1']:.2f}</span></div>
                    <div class="calc-row txt-green"><span>MIN 5</span> <span>{res['min_fut_5']:.2f}</span></div>
                </div>''', unsafe_allow_html=True)
                st.markdown(f'''<div class="calc-panel"><div class="calc-row"><span>DOLB3</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div><div class="calc-row"><span>PREÇO JUSTO</span> <span>{res['fraja']:.2f}</span></div></div>''', unsafe_allow_html=True)
    time.sleep(5)
