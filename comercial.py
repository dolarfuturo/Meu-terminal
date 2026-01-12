import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL (Sincroniza ajustes e anotações)
@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas": "MURAL: AGUARDANDO ATUALIZAÇÃO..."
    }

v_global = get_global_vars()

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_type = None

if not st.session_state.auth:
    st.markdown("""
    <style>
        .stApp { background-color: #000; }
        [data-testid="stHeader"], label { display: none !important; }
        .stButton button { 
            width: 100%; background-color: #222; color: white; 
            border: 1px solid #444; font-family: sans-serif;
            letter-spacing: 2px; margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:150px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="CHAVE DE ACESSO")
        if st.button("ENTRAR"):
            if senha == "admin123":
                st.session_state.auth = True
                st.session_state.user_type = "ADM"
                st.rerun()
            elif senha == "trader123":
                st.session_state.auth = True
                st.session_state.user_type = "USER"
                st.rerun()
    st.stop()

# 4. CSS DO TERMINAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 12px; font-weight: 700; letter-spacing: 2px; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 22px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; }
    .sub-l { font-size: 8px; color: #888; display: block; margin-bottom: 2px; font-weight: 400; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }

    .f-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; height: 140px; 
        background: #050505; border-top: 1px solid #222; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; 
    }
    .f-notes { font-family: 'Chakra Petch'; font-size: 11px; color: #ffff99; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; max-width: 90%; text-align: center; }
    .f-arrows { font-size: 16px; margin: 5px 0; letter-spacing: 8px; }
    .f-line { width: 85%; height: 1px; background: rgba(255,255,255,0.1); }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE DADOS
def get_market():
    try:
        br_tz = pytz.timezone('America/Sao_Paulo')
        agora_br = datetime.now(br_tz)
        hora_atual = agora_br.hour
        d = {}
        # Coleta moedas (Forex 24h)
        for t in ["BRL=X", "EURUSD=X"]:
            tick = yf.Ticker(t)
            inf = tick.fast_info
            d[t] = {"p": inf['last_price'], "v": ((inf['last_price'] - inf['previous_close']) / inf['previous_close']) * 100}
        
        # Coleta índices (Pre-Market inteligente)
        tkrs_ny = {"DX-Y.NYB": "DXY", "EWZ": "EWZ"}
        for t, label in tkrs_ny.items():
            tick = yf.Ticker(t)
            if hora_atual >= 8:
                inf = tick.info
                cp = inf.get('preMarketPrice') or inf.get('regularMarketPrice') or inf.get('previousClose')
                pc = inf.get('regularMarketPreviousClose') or inf.get('previousClose')
            else:
                inf = tick.fast_info
                cp = inf['last_price']
                pc = inf['previous_close']
            v_pct = ((cp - pc) / pc) * 100 if cp and pc else 0.0
            d[t] = {"p": cp, "v": v_pct}
        
        spr_val = d["DX-Y.NYB"]["v"] - d["EWZ"]["v"]
        return d, spr_val
    except:
        return None, 0.0

# 6. LOOP DE EXECUÇÃO
ui_area = st.empty()

while True:
    m_data, spr = get_market()
    if m_data:
        spot = m_data["BRL=X"]["p"]
        justo = round((spot + 0.0310) * 2000) / 2000
        diff = spot - justo
        
        if diff < -0.0015: msg, clr, arr = "● DOLAR BARATO", "#00aa55", "▲ ▲ ▲ ▲ ▲"
        elif diff > 0.0015: msg, clr, arr = "● DOLAR CARO", "#aa3333", "▼ ▼ ▼ ▼ ▼"
        else: msg, clr, arr = "● DOLAR NEUTRO", "#aaaa00", "◄ ◄ ◄ ► ► ►"
            
        with ui_area.container():
            if st.session_state.user_type == "ADM":
                with st.expander("PAINEL ADM"):
                    v_global["ajuste"] = st.number_input("PARIDADE", value=v_global["ajuste"], format="%.4f", step=0.0001)
                    v_global["ref"] = st.number_input("REF INST", value=v_global["ref"], format="%.4f", step=0.0001)
                    v_global["notas"] = st.text_input("NOTAS", value=v_global["notas"])

            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {clr}77"><div class="s-text" style="color:{clr}">{msg}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{(v_global["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value c-equi">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            # PREÇO JUSTO
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{justo:.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            # REF INST
            st.markdown(f'<div class="d-row" style="border-bottom:none;"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{(round((v_global["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((v_global["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # FUNÇÃO DO TICKER CORRIGIDA
            def f_tk(t_code, label):
                try:
                    price = m_data[t_code]['p']
                    var = m_data[t_code]['v']
                    color = "#00aa55" if var >= 0 else "#aa3333"
                    p_fmt = f"{price:.4f}" if label == "SPOT" else f"{price:.2f}"
                    return f"<span class='tk-item'><b>{label}</b> {p_fmt} <span style='color:{color}'>({var:+.2f}%)</span></span>"
                except: return ""

            btk = f"{f_tk('BRL=X','SPOT')} {f_tk('DX-Y.NYB','DXY')} {f_tk('EWZ','EWZ')} {f_tk('EURUSD=X','EURUSD')} <span class='tk-item'><b>SPREAD</b> {spr:+.2f}%</span>"
            
            st.markdown(f"""
                <div class="f-bar">
                    <div class="f-notes">{v_global['notas']}</div>
                    <div class="f-line"></div>
                    <div class="f-arrows" style="color:{clr}">{arr}</div>
                    <div class="f-line"></div>
                    <div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div>
                </div>
            """, unsafe_allow_html=True)
            
    time.sleep(2)
