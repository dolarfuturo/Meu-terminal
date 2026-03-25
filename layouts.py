import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO (FORÇANDO EXPANDIDO)
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* REMOVE CABEÇALHOS PADRÃO PARA LIMPAR O VISUAL */
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    
    .stApp { background-color: #050a0e !important; }

    /* FORÇAR BARRA LATERAL PRETA E VISÍVEL */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 2px solid #d4a017;
        min-width: 250px !important;
    }
    
    /* ESTILO DOS INPUTS NO PAINEL ADM */
    .stNumberInput label { color: #d4a017 !important; font-weight: bold !important; }
    div.stButton > button {
        width: 100%;
        background-color: #d4a017 !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
    }

    /* SEU CSS ORIGINAL DO TERMINAL */
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 8px; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 6px; background: #0a141a; font-family: monospace; margin-bottom: 4px; }
    .calc-row { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    .bar-wrapper-dual { background: #0a141a; padding: 12px 10px 6px 10px; border: 2.5px solid #ffffff; border-radius: 8px; text-align: center; position: relative; }
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 4px 0; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# 2. MOTOR DE DADOS E FUNÇÕES (SEM ALTERAÇÃO)
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
        return (df['High'].iloc[-1] + df['Low'].iloc[-1]) / 2 if not df.empty else 37.85
    except: return 37.85

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol, spot_data):
    try:
        if p_ewz_atual == 0: return None
        v_spreed = (spot_data['mx'] - spot_data['mn']) / 8
        v_spot = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        v_ewz = ((p_ewz_atual / fetch("EWZ")['cl']) - 1) if fetch("EWZ")['cl'] > 0 else 0
        v_final = (v_spot * 0.6) - (v_ewz * 0.4)
        dist_base = abs(eixo_dol - ((spot_data['mx'] + spot_data['mn']) / 2))
        diff = spot_data['at'] - eixo_dol
        p_v = min(100, (abs(diff)/(dist_base*2))*100) if diff < 0 and dist_base > 0 else 0
        p_r = min(100, (abs(diff)/(dist_base*2))*100) if diff >= 0 and dist_base > 0 else 0
        return {
            "vivo": spot_data['at'], "fraja": eixo_dol * (1 + (v_final / 2)), "medio": (spot_data['mx'] + spot_data['mn']) / 2, "ewz_med": (max_ewz + min_ewz) / 2,
            "max_fut": spot_data['mx'] + v_spreed, "p75_up": (spot_data['mx'] + v_spreed) - v_spreed, "p25_up": eixo_dol + v_spreed, "p25_down": eixo_dol - v_spreed,
            "p75_down": (spot_data['mn'] + v_spreed) + v_spreed, "min_fut": spot_data['mn'] + v_spreed, "v_v": v_final * 100, "spreed": v_spreed,
            "var_axis": ((spot_data['at'] + v_spreed) / eixo_dol - 1) * 100, "p_v": p_v, "p_r": p_r, 
            "seta": "▲ COMPRA" if p_v >= 100 else ("▼ VENDA" if p_r >= 100 else ""), "seta_cor": "#00ff88" if p_v >= 100 else "#ff4d4d"
        }
    except: return None

# 3. PAINEL ADM (SIDEBAR FIXA)
if 'a_ewz' not in st.session_state: st.session_state.a_ewz = float(calcular_sentinela())
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00

with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    new_ewz = st.number_input("AXIS EWZ:", value=st.session_state.a_ewz, format="%.2f", step=0.01)
    new_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol, format="%.2f", step=0.50)
    
    if st.button("SALVAR E ATUALIZAR"):
        st.session_state.a_ewz = new_ewz
        st.session_state.a_dol = new_dol
        st.rerun()
    
    st.markdown("---")
    st.info("O terminal atualiza automaticamente a cada 2 segundos.")

# 4. LOOP DO TERMINAL
placeholder = st.empty()

while True:
    tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
    ewz_live = fetch("EWZ")
    spot_live = fetch("USDBRL=X")
    res = calcular_k97_total(st.session_state.a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], st.session_state.a_dol, spot_live)

    with placeholder.container():
        if res:
            # HEADER E GRIDS (IGUAL AO SEU ORIGINAL)
            st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL DOLLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">SP</span><br><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M:%S')}</span></div></div></div>""", unsafe_allow_html=True)
            
            c_main, c_side = st.columns([3, 1])
            with c_main:
                # Tabela Principal
                html_table = f"""<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Var</th></tr></thead><tbody>
                <tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(st.session_state.a_dol * (1 + (res['v_v']/100))/1000):.4f}</td><td style='color:{"#00ff00" if res['v_v'] >= 0 else "#ff4d4d"}'>{res['v_v']:+.2f}%</td></tr>
                </tbody></table></div>"""
                st.markdown(html_table, unsafe_allow_html=True)

            with c_side:
                # Painel de Cálculos Direito
                st.markdown(f"""<div class="calc-panel"><div class="calc-row"><span>AXIS</span> <span>{st.session_state.a_dol:.2f}</span></div><div class="calc-row"><span>P. JUSTO</span> <span>{res['fraja']:.2f}</span></div></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="bar-wrapper-dual"><div class="force-container-dual"><div class="fill-green" style="width: {res['p_v']}%;"></div><div class="fill-red" style="width: {res['p_r']}%;"></div></div><div class="blink" style="color:{res['seta_cor']}; font-weight:bold;">{res['seta']}</div></div>""", unsafe_allow_html=True)

    time.sleep(2)
