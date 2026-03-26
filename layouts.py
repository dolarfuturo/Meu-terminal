import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- CSS: ESTILIZAÇÃO (PADRÃO CRYPTO APLICADO) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container { padding-top: 0rem !important; }
    .stApp { background-color: #0E1117 !important; }
    
    /* TOP BAR NEXUS STYLE */
    .top-bar-nexus { 
        display: flex; justify-content: space-between; align-items: center; 
        padding: 5px 20px; background: #050505; border-bottom: 1px solid #1a1a1a; 
    }
    .live-indicator { display: flex; align-items: center; gap: 8px; color: #FFF; font-size: 11px; font-weight: bold; font-family: monospace; }
    .dot { 
        height: 10px; width: 10px; background-color: #00FF00; border-radius: 50%; 
        display: inline-block; box-shadow: 0 0 8px #00FF00; animation: pulse-glow 1s infinite alternate;
    }
    @keyframes pulse-glow { from { opacity: 1; transform: scale(1); } to { opacity: 0.2; transform: scale(0.8); } }

    /* CABEÇALHO PADRÃO CRYPTO (35px) */
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #0E1117; margin-bottom: 15px; }
    .main-title { margin: 0px; line-height: 1.1; font-size: 35px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .sub-title { color: white; font-size: 12px; letter-spacing: 8px; margin: 0px; text-transform: uppercase; }
    
    /* RELÓGIOS (14px) */
    .clock-row { display: flex; justify-content: center; gap: 30px; padding: 10px 0; font-weight: bold; font-size: 14px; font-family: monospace; color: #AAA; }
    .br-green { color: #00ff00; }
    .white-time { color: #ffffff; }

    /* FAIXAS DE TÍTULO */
    .section-title { 
        border: 1px solid #ffffff; 
        color: #00f2ff; 
        text-align: center; 
        font-weight: bold; 
        font-family: monospace; 
        padding: 5px; 
        margin-bottom: 8px; 
        text-transform: uppercase;
        font-size: 14px;
    }

    /* GRADE PRINCIPAL (FONTES 11px e 13px) */
    .main-grid { border: 1px solid #444; overflow: hidden; font-family: monospace; background-color: #0E1117; }
    .terminal-table { width: 100%; border-collapse: separate; border-spacing: 0; color: #ffffff; }
    .terminal-table th { background-color: #1A1C23 !important; color: #FFD700; border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 11px; text-transform: uppercase; position: sticky; top: 0; }
    .terminal-table td { border: 1px solid #ffffff; padding: 8px; text-align: center; font-size: 13px; font-weight: bold; }
    
    .asset-name { text-align: center !important; }
    .price-col { font-weight: bold; }

    /* BLOCOS LATERAIS */
    .calc-panel { border: 1px solid #ffffff; padding: 6px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 6px 8px; border-bottom: 1px solid #333; font-size: 13px; font-weight: bold; align-items: center; color: white; }
    .axis-center-box { text-align:center; padding: 10px; color: #00f2ff; font-size: 14px; font-weight: bold; border-top:1px solid #444; border-bottom:1px solid #444; margin: 5px 0; }

    /* BARRA DE FORÇA */
    .bar-wrapper-dual { background: #050505; padding: 12px 10px 6px 10px; border: 1px solid #ffffff; border-radius: 0px; text-align: center; position: relative; }
    .force-scale { display: flex; justify-content: space-between; font-size: 11px; font-family: monospace; font-weight: bold; margin-bottom: 4px; }
    .scale-left { color: #00ff88; width: 50%; display: flex; justify-content: space-around; }
    .scale-right { color: #ff4d4d; width: 50%; display: flex; justify-content: space-around; }
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 0px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 16px; font-weight: 950; margin-top: 5px; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }

    /* FOOTER */
    .footer-trava { color: #555; font-family: monospace; font-size: 11px; padding: 8px 20px; background: #050505; border-top: 1px solid #1a1a1a; margin-top: 10px; }
    
    .ticker-wrapper { width: 100%; background: #000; border-top: 1px solid #ffffff; border-bottom: 1px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: monospace; font-size: 13px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        ref_close = t.info.get('previousClose')
        if s == "EWZ":
            d_hist = t.history(period="3d", interval="1m", prepost=True)
            if not d_hist.empty:
                d_hist.index = d_hist.index.tz_convert(tz_sp)
                unique_dates = sorted(list(set(d_hist.index.date)))
                data_anterior = unique_dates[-2] if len(unique_dates) > 1 else unique_dates[0]
                f_21h = d_hist.between_time('05:00', '21:00').loc[d_hist.index.date == data_anterior]
                if not f_21h.empty: ref_close = f_21h['Close'].iloc[-1]
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1] * m, "cl": (ref_close or d['Open'].iloc[0]) * m, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

@st.cache_data(ttl=600)
def calcular_sentinela():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d", prepost=False)
        if df.empty: return 37.85
        tz_sp = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(tz_sp)
        hoje = agora.date()
        ultima_data_yahoo = df.index[-1].date()
        idx = -2 if (ultima_data_yahoo == hoje and agora.hour < 18) else -1
        return (df['High'].iloc[idx] + df['Low'].iloc[idx]) / 2
    except: return 37.85

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol, spot_data):
    try:
        if p_ewz_atual == 0: return None
        v_spreed = (spot_data['mx'] - spot_data['mn']) / 8
        v_spot = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        v_ewz = ((p_ewz_atual / fetch("EWZ")['cl']) - 1) if fetch("EWZ")['cl'] > 0 else 0
        v_final = (v_spot * 0.6) - (v_ewz * 0.4)
        dolar_vivo = spot_data['at'] 
        dolar_fraja = eixo_dol * (1 + (v_final / 2))
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        max_fut = spot_data['mx'] + v_spreed
        p75_up, p25_up = max_fut - v_spreed, eixo_dol + v_spreed
        p25_down, p75_down = eixo_dol - v_spreed, (spot_data['mn'] + v_spreed) + v_spreed
        min_fut = spot_data['mn'] + v_spreed
        dist_base = abs(eixo_dol - dolar_medio)
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = 0, 0
        if dist_base > 0:
            if diff < 0: p_v = min(100, (abs(diff)/(dist_base*2))*100)
            else: p_r = min(100, (abs(diff)/(dist_base*2))*100)
        seta_txt, seta_cor = "", "#000000"
        if p_v >= 100: seta_txt, seta_cor = "▲ REGIÃO DE COMPRA", "#00ff88"
        elif p_r >= 100: seta_txt, seta_cor = "▼ REGIÃO DE VENDA", "#ff4d4d"
        var_axis = ((spot_data['at'] + v_spreed) / eixo_dol - 1) * 100
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, "ewz_med": (max_ewz + min_ewz) / 2,
            "max_fut": max_fut, "p75_up": p75_up, "p25_up": p25_up, "p25_down": p25_down, "p75_down": p75_down, 
            "min_fut": min_fut, "v_v": v_final * 100, "spreed": v_spreed, "var_axis": var_axis,
            "p_v": p_v, "p_r": p_r, "seta": seta_txt, "seta_cor": seta_cor
        }
    except: return None

# --- SIDEBAR ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
    st.button("SALVAR")

placeholder = st.empty()

while True:
    tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
    ewz_live = fetch("EWZ")
    spot_live = fetch("USDBRL=X")
    res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol, spot_live)
    now = datetime.now()

    with placeholder.container():
        # TOP BAR STYLE
        st.markdown(f"""
            <div class="top-bar-nexus">
                <div class="live-indicator"><span class="dot"></span> SISTEMA | ONLINE</div>
                <div style="color: #444; font-size: 10px; font-family: monospace;">BAIR SYSTEM V2.0</div>
            </div>
            <div class="header-container">
                <h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1>
                <p class="sub-title">VISÃO DE TUBARÃO</p>
                <div class="clock-row">
                    <span>🇧🇷 BRASÍLIA: <span class="br-green">{now.astimezone(tz_sp).strftime('%H:%M:%S')}</span></span>
                    <span>🇺🇸 NEW YORK: <span class="white-time">{now.astimezone(tz_ny).strftime('%H:%M:%S')}</span></span>
                    <span>🇬🇧 LONDON: <span class="white-time">{now.astimezone(tz_ld).strftime('%H:%M:%S')}</span></span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if res:
            dolfut_calc, dolfut_com_spread = a_dol * (1 + (res['v_v'] / 100)), res['vivo'] + res['spreed']
            c_main, c_side = st.columns([3, 1])
            
            with c_main:
                st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                v_v = res['v_v']
                
                # LINHA DOLFUT
                bg_dol = "background-color:rgba(0, 255, 0, 0.4);" if v_v >= 0 else "background-color:rgba(255, 0, 0, 0.4);"
                html_table += f"<tr><td>DOLFUT</td><td style='color:#00BFFF; {bg_dol}'>{(dolfut_calc/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max_fut']/1000):.4f}</td><td>{(res['min_fut']/1000):.4f}</td><td style='color:{("#00ff00" if v_v >= 0 else "#ff4d4d")};'>{v_v:+.2f}%</td></tr>"
                
                ticker_items = [f"DOLFUT: {v_v:+.2f}%"]
                outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "XAU/USD": "GC=F", "PETROLEO": "BZ=F"}
                
                for lbl, sym in outros.items():
                    d = spot_live if lbl == "DOLSPOT" else (ewz_live if lbl == "EWZ" else fetch(sym))
                    f, p_val = (".4f", d['at']/1000) if lbl == "DOLSPOT" else (".2f", d['at'])
                    var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                    bg_item = "background-color:rgba(0, 255, 0, 0.4);" if var >= 0 else "background-color:rgba(255, 0, 0, 0.4);"
                    
                    html_table += f"<tr><td>{lbl}</td><td style='color:#00BFFF; {bg_item}'>{p_val:{f}}</td><td>{(d['cl']/1000 if lbl=='DOLSPOT' else d['cl']):{f}}</td><td>{(d['op']/1000 if lbl=='DOLSPOT' else d['op']):{f}}</td><td>{(d['mx']/1000 if lbl=='DOLSPOT' else d['mx']):{f}}</td><td>{(d['mn']/1000 if lbl=='DOLSPOT' else d['mn']):{f}}</td><td style='color:{("#00ff00" if var >= 0 else "#ff4d4d")};'>{var:+.2f}%</td></tr>"
                    ticker_items.append(f"{lbl}: {var:+.2f}%")
                
                st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)
            
            with c_side:
                st.markdown('<div class="section-title">CÁLCULOS DE PROJEÇÕES</div>', unsafe_allow_html=True)
                st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MAX FUT</span> <span>{res['max_fut']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div><div class="axis-center-box">AXIS: {a_dol:.2f}</div><div class="calc-row" style="color:#ffa500;"><span>25%</span> <span>{res['p25_down']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>75%</span> <span>{res['p75_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MIN FUT</span> <span>{res['min_fut']:.2f}</span></div></div>""", unsafe_allow_html=True)
                
                st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span>DOLFUT</span> <span style="color:#00f2ff;">{dolfut_com_spread:.2f}</span></div><div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span>{res['medio']:.2f}</span></div><div class="calc-row"><span style="color:#d4a017;">P. JUSTO</span> <span>{res['fraja']:.2f}</span></div><div class="calc-row" style="border-bottom: none;"><span style="color:#ff4d4d;">SPREED</span> <span style="color:#00f2ff;">{res['spreed']:.2f}</span></div></div>""", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="bar-wrapper-dual">
                    <div class="force-scale">
                        <div class="scale-left"><span>100%</span><span>50%</span><span>30%</span></div>
                        <div class="scale-right"><span>30%</span><span>50%</span><span>100%</span></div>
                    </div>
                    <div class="force-container-dual"><div class="center-line"></div>
                        <div style="width: 50%; height: 100%;"><div class="fill-green" style="width: {res['p_v']}%;"></div></div>
                        <div style="width: 50%; height: 100%;"><div class="fill-red" style="width: {res['p_r']}%;"></div></div>
                    </div>
                    <div class="sinal-indicator blink" style="color:{res['seta_cor']};">{res['seta']}</div>
                </div>""", unsafe_allow_html=True)
            
            ticker_html = " • ".join(ticker_items)
            st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{ticker_html} • {ticker_html}</div></div>', unsafe_allow_html=True)
            st.markdown(f"<div class='footer-trava'>BAIR - TERMINAL | Status: Online | {datetime.now(tz_sp).strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

    time.sleep(2)
