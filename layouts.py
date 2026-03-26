import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração Otimizada para Mobile (Layout Centered é melhor para celular)
st.set_page_config(layout="centered", page_title="BAIR - MOBILE", initial_sidebar_state="collapsed")

# --- CSS: ADAPTAÇÃO VERTICAL ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    
    /* CABEÇALHO MOBILE */
    .header-container { text-align: center; padding: 10px 5px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 10px; }
    .main-title { margin: 0px; line-height: 1.1; font-size: 24px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    
    .clock-row { display: flex; justify-content: center; gap: 10px; padding: 5px 0; font-size: 11px; font-family: monospace; flex-wrap: wrap; }
    .clock-item { color: #AAA; }
    .br-green { color: #00ff00; }

    .section-title { 
        border: 1.5px solid #ffffff; color: #00f2ff; text-align: center; 
        font-weight: bold; font-family: monospace; padding: 4px; 
        margin: 10px 0 8px 0; text-transform: uppercase; font-size: 13px;
    }

    /* CARDS DE ATIVOS (EM VEZ DE TABELA LARGA) */
    .mobile-card {
        background: #0d1b22; border: 1.5px solid #ffffff; border-radius: 6px;
        padding: 10px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;
        font-family: monospace;
    }
    .card-left { text-align: left; }
    .card-right { text-align: right; }
    .asset-name { font-size: 15px; color: #FFD700; font-weight: bold; }
    .asset-price { font-size: 18px; color: #fff; font-weight: bold; display: block; }
    .asset-var { font-size: 14px; font-weight: bold; }

    /* PAINÉIS DE CÁLCULO */
    .calc-panel { border: 2px solid #ffffff; border-radius: 8px; padding: 10px; background: #0a141a; font-family: monospace; margin-bottom: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #444; font-size: 14px; font-weight: bold; }
    
    /* BARRA DE FORÇA MOBILE */
    .bar-wrapper-dual { background: #0a141a; padding: 15px 10px; border: 2px solid #ffffff; border-radius: 8px; text-align: center; margin-top: 10px; }
    .force-scale { display: flex; justify-content: space-between; font-size: 10px; font-family: monospace; font-weight: bold; margin-bottom: 6px; }
    .scale-left { color: #00ff88; width: 50%; display: flex; justify-content: space-around; }
    .scale-right { color: #ff4d4d; width: 50%; display: flex; justify-content: space-around; }
    .force-container-dual { background: #111; height: 24px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .sinal-indicator { font-size: 18px; font-weight: 950; margin-top: 10px; }
    
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS (SEU CÓDIGO ORIGINAL) ---
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
        return {"vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, "max_fut": max_fut, "p75_up": p75_up, "p25_up": p25_up, "p25_down": p25_down, "p75_down": p75_down, "min_fut": min_fut, "v_v": v_final * 100, "spreed": v_spreed, "var_axis": var_axis, "p_v": p_v, "p_r": p_r, "seta": seta_txt, "seta_cor": seta_cor}
    except: return None

# --- SIDEBAR ADM ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")

placeholder = st.empty()

while True:
    tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
    ewz_live = fetch("EWZ")
    spot_live = fetch("USDBRL=X")
    res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol, spot_live)
    now = datetime.now()

    with placeholder.container():
        # CABEÇALHO MOBILE
        st.markdown(f"""
            <div class="header-container">
                <h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL</span></h1>
                <div class="clock-row">
                    <span class="clock-item">🇧🇷 BR: <span class="br-green">{now.astimezone(tz_sp).strftime('%H:%M:%S')}</span></span>
                    <span class="clock-item">🇺🇸 NY: <span>{now.astimezone(tz_ny).strftime('%H:%M:%S')}</span></span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if res:
            dolfut_calc = a_dol * (1 + (res['v_v'] / 100))
            dolfut_com_spread = res['vivo'] + res['spreed']
            
            # --- GRADE DE ATIVOS EM CARDS (MAIS LEITURA NO CELULAR) ---
            st.markdown('<div class="section-title">GRADE PRINCIPAL</div>', unsafe_allow_html=True)
            
            # DOLFUT CARD
            cor_v = "#00ff00" if res['v_v'] >= 0 else "#ff4d4d"
            st.markdown(f"""
                <div class="mobile-card" style="border-left: 5px solid {cor_v};">
                    <div class="card-left"><span class="asset-name">DOLFUT</span><span class="asset-price">{(dolfut_calc/1000):.4f}</span></div>
                    <div class="card-right"><span class="asset-var" style="color:{cor_v};">{res['v_v']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)

            # OUTROS ATIVOS
            outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "PETROLEO": "BZ=F"}
            for lbl, sym in outros.items():
                d = spot_live if lbl == "DOLSPOT" else (ewz_live if lbl == "EWZ" else fetch(sym))
                var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                color = "#00ff00" if var >= 0 else "#ff4d4d"
                price = d['at']/1000 if lbl == "DOLSPOT" else d['at']
                fmt = ".4f" if lbl == "DOLSPOT" else ".2f"
                st.markdown(f"""
                    <div class="mobile-card">
                        <div class="card-left"><span class="asset-name">{lbl}</span><span class="asset-price">{price:{fmt}}</span></div>
                        <div class="card-right"><span class="asset-var" style="color:{color};">{var:+.2f}%</span></div>
                    </div>
                """, unsafe_allow_html=True)

            # --- PROJEÇÕES E CÁLCULOS ---
            st.markdown('<div class="section-title">PROJEÇÕES E JUSTO</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="calc-panel">
                    <div class="calc-row" style="color:#ff4d4d;"><span>MAX FUT</span> <span>{res['max_fut']:.2f}</span></div>
                    <div class="calc-row"><span>AXIS ATUAL</span> <span style="color:#00f2ff;">{a_dol:.2f}</span></div>
                    <div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MIN FUT</span> <span>{res['min_fut']:.2f}</span></div>
                </div>
                <div class="calc-panel">
                    <div class="calc-row"><span>P. JUSTO</span> <span style="color:#ffffff;">{res['fraja']:.2f}</span></div>
                    <div class="calc-row"><span>MÉDIA DOL</span> <span>{res['medio']:.2f}</span></div>
                    <div class="calc-row" style="border-bottom:none;"><span>SPREAD</span> <span style="color:#ff4d4d;">{res['spreed']:.2f}</span></div>
                </div>
            """, unsafe_allow_html=True)

            # --- BARRA DE FORÇA ---
            st.markdown(f"""
                <div class="bar-wrapper-dual">
                    <div class="force-scale">
                        <div class="scale-left"><span>100%</span><span>50%</span><span>30%</span></div>
                        <div class="scale-right"><span>30%</span><span>50%</span><span>100%</span></div>
                    </div>
                    <div class="force-container-dual">
                        <div class="center-line"></div>
                        <div style="width: 50%; height: 100%; background: #050a0e;">
                            <div style="background: #00ff88; float: right; height: 100%; width: {res['p_v']}%;"></div>
                        </div>
                        <div style="width: 50%; height: 100%; background: #050a0e;">
                            <div style="background: #ff4d4d; float: left; height: 100%; width: {res['p_r']}%;"></div>
                        </div>
                    </div>
                    <div class="sinal-indicator blink" style="color:{res['seta_cor']};">{res['seta']}</div>
                </div>
            """, unsafe_allow_html=True)

    time.sleep(2)
