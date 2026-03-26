import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração focada em Mobile (Centralizado e Compacto)
st.set_page_config(layout="centered", page_title="BAIR - CALCULADORA", initial_sidebar_state="collapsed")

# --- CSS: FOCO EM BLOCOS DE CÁLCULO ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    
    /* CABEÇALHO COMPACTO */
    .header-container { text-align: center; padding: 5px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 15px; }
    .main-title { margin: 0px; font-size: 22px; font-family: monospace; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    
    .clock-row { display: flex; justify-content: center; gap: 15px; font-size: 12px; font-family: monospace; color: #AAA; }

    .section-title { 
        border: 1.5px solid #ffffff; color: #00f2ff; text-align: center; 
        font-weight: bold; font-family: monospace; padding: 5px; 
        margin: 15px 0 10px 0; text-transform: uppercase; font-size: 14px;
    }

    /* BLOCOS DE CÁLCULO ESTILO TERMINAL */
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 12px; background: #0a141a; font-family: monospace; margin-bottom: 12px; }
    .calc-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #333; font-size: 16px; font-weight: bold; }
    .axis-box { text-align: center; padding: 15px; color: #00f2ff; font-size: 22px; font-weight: bold; border-top: 2px solid #444; border-bottom: 2px solid #444; margin: 10px 0; }

    /* BARRA DE FORÇA (MAIOR PARA MOBILE) */
    .bar-wrapper-dual { background: #0a141a; padding: 20px 15px; border: 2.5px solid #ffffff; border-radius: 8px; text-align: center; }
    .force-scale { display: flex; justify-content: space-between; font-size: 11px; font-family: monospace; font-weight: bold; margin-bottom: 8px; }
    .scale-left { color: #00ff88; width: 50%; display: flex; justify-content: space-around; }
    .scale-right { color: #ff4d4d; width: 50%; display: flex; justify-content: space-around; }
    
    .force-container-dual { background: #111; height: 30px; width: 100%; border-radius: 5px; position: relative; overflow: hidden; display: flex; border: 1px solid #555; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    
    .sinal-indicator { font-size: 22px; font-weight: 950; margin-top: 15px; letter-spacing: 1px; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }

    /* Esconder Sidebar no Mobile por padrão */
    [data-testid="stSidebar"] { background-color: #0a141a; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS (SEU CÓDIGO ORIGINAL MANTIDO) ---
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
        if d.empty: return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1] * m, "cl": (ref_close or d['Open'].iloc[0]) * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0}

@st.cache_data(ttl=600)
def calcular_sentinela():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d")
        return (df['High'].iloc[-2] + df['Low'].iloc[-2]) / 2
    except: return 37.85

def calcular_k97_total(eixo_ewz, p_ewz_atual, eixo_dol, spot_data):
    try:
        v_spreed = (spot_data['mx'] - spot_data['mn']) / 8
        v_spot = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        v_ewz = ((p_ewz_atual / fetch("EWZ")['cl']) - 1) if fetch("EWZ")['cl'] > 0 else 0
        v_final = (v_spot * 0.6) - (v_ewz * 0.4)
        
        dolar_fraja = eixo_dol * (1 + (v_final / 2))
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        
        max_fut = spot_data['mx'] + v_spreed
        min_fut = spot_data['mn'] + v_spreed
        
        diff = spot_data['at'] - eixo_dol
        dist_base = abs(eixo_dol - dolar_medio)
        
        p_v, p_r = 0, 0
        if dist_base > 0:
            if diff < 0: p_v = min(100, (abs(diff)/(dist_base*2))*100)
            else: p_r = min(100, (abs(diff)/(dist_base*2))*100)
            
        seta, cor = "", "#000"
        if p_v >= 100: seta, cor = "▲ REGIÃO DE COMPRA", "#00ff88"
        elif p_r >= 100: seta, cor = "▼ REGIÃO DE VENDA", "#ff4d4d"
        
        return {
            "max_fut": max_fut, "min_fut": min_fut, "fraja": dolar_fraja, "medio": dolar_medio,
            "spreed": v_spreed, "p_v": p_v, "p_r": p_r, "seta": seta, "seta_cor": cor,
            "p75_up": max_fut - v_spreed, "p25_up": eixo_dol + v_spreed,
            "p25_down": eixo_dol - v_spreed, "p75_down": (spot_data['mn'] + v_spreed) + v_spreed
        }
    except: return None

# --- UI MOBILE ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    st.markdown("### ⚙️ AJUSTE AXIS")
    a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, step=1.0)
    a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug))

placeholder = st.empty()

while True:
    spot_live = fetch("USDBRL=X")
    ewz_live = fetch("EWZ")
    res = calcular_k97_total(a_ewz, ewz_live['at'], a_dol, spot_live)
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))

    with placeholder.container():
        # Header
        st.markdown(f"""
            <div class="header-container">
                <h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - CALCULADORA</span></h1>
                <div class="clock-row"><span>🇧🇷 {now.strftime('%H:%M:%S')}</span></div>
            </div>
        """, unsafe_allow_html=True)

        if res:
            # BLOCO 1: PROJEÇÕES DE PREÇO
            st.markdown('<div class="section-title">PROJEÇÕES DE MERCADO</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="calc-panel">
                    <div class="calc-row" style="color:#ff4d4d;"><span>MAX FUT</span> <span>{res['max_fut']:.2f}</span></div>
                    <div class="calc-row" style="color:#ffa500;"><span>75% ALTA</span> <span>{res['p75_up']:.2f}</span></div>
                    <div class="calc-row" style="color:#ffa500;"><span>25% ALTA</span> <span>{res['p25_up']:.2f}</span></div>
                    <div class="axis-box">AXIS: {a_dol:.2f}</div>
                    <div class="calc-row" style="color:#ffa500;"><span>25% BAIXA</span> <span>{res['p25_down']:.2f}</span></div>
                    <div class="calc-row" style="color:#ffa500;"><span>75% BAIXA</span> <span>{res['p75_down']:.2f}</span></div>
                    <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MIN FUT</span> <span>{res['min_fut']:.2f}</span></div>
                </div>
            """, unsafe_allow_html=True)

            # BLOCO 2: JUSTO E MÉDIA
            st.markdown('<div class="section-title">VALORES DE REFERÊNCIA</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="calc-panel">
                    <div class="calc-row"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#fff;">{res['fraja']:.2f}</span></div>
                    <div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span>{res['medio']:.2f}</span></div>
                    <div class="calc-row" style="border-bottom: none;"><span style="color:#ff4d4d;">SPREAD</span> <span style="color:#00f2ff;">{res['spreed']:.2f}</span></div>
                </div>
            """, unsafe_allow_html=True)

            # BLOCO 3: BARRA DE FORÇA K97
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
