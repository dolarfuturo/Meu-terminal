import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas_mural": "AGUARDANDO ATUALIZAÇÃO...",
        "notas": "OPERACIONAL ATIVO",
        "notas2": "SISTEMA AUTOMÁTICO"
    }

v_global = get_global_vars()

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_type = None

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'] { display: none !important; } .stButton button { width: 100%; background-color: #222; color: white; border: 1px solid #444; margin-top: 20px; }</style>", unsafe_allow_html=True)
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

# 4. CSS DO TERMINAL COM ANIMAÇÕES
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    /* Animação de Batimento para o Spot */
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.02); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    .live-update { animation: pulse 0.8s ease-in-out; }

    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    
    .s-container { text-align: center; padding: 15px 0; margin-bottom: 5px; border-bottom: 2px solid #333; }
    .s-text { font-size: 24px; font-weight: 700; letter-spacing: 1px; font-family: 'Chakra Petch'; }
    .s-subtext { font-size: 10px; color: #666; font-weight: 400; margin-top: 4px; }
    .vies-indicator { font-size: 14px; font-weight: 900; letter-spacing: 2px; margin-top: 8px; }

    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; }
    .sub-item { text-align: center; min-width: 75px; }
    .sub-l { font-size: 8px; color: #888; display: block; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .note-box { background: #050505; border-top: 1px solid #111; padding: 20px; min-height: 100px; }
    .note-content { font-family: 'Chakra Petch'; font-size: 14px; color: #999; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 120px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; margin-top: 10px; }
    .tk-move { display: inline-block; animation: slide 30s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE DADOS (FORÇANDO REFRESH)
def get_data(ticker):
    try:
        # download sem threads para evitar travamentos no streamlit
        df = yf.download(ticker, period="1d", interval="1m", progress=False, prepost=True, threads=False)
        if not df.empty:
            last = float(df['Close'].iloc[-1])
            prev = float(yf.Ticker(ticker).fast_info.previous_close)
            var = ((last - prev) / prev * 100) if prev != 0 else 0
            return {"last": last, "prev": prev, "var": var}
    except:
        pass
    return None

# Valores de fallback
cache_data = {
    "BRL=X": {"last": v_global["ajuste"], "prev": v_global["ajuste"], "var": 0.0},
    "DX-Y.NYB": {"last": 100.0, "var": 0.0},
    "EWZ": {"last": 30.0, "var": 0.0},
    "EURUSD=X": {"last": 1.08, "var": 0.0}
}

# 6. LOOP PRINCIPAL (1 SEGUNDO)
ui_area = st.empty()

while True:
    # Atualiza Tickers
    for t in cache_data.keys():
        res = get_data(t)
        if res: cache_data[t] = res

    # Variáveis de cálculo
    s = cache_data["BRL=X"]
    d = cache_data["DX-Y.NYB"]
    e = cache_data["EWZ"]
    
    spot = s["last"]
    spr = d["var"] - e["var"]
    paridade = v_global["ajuste"] * (1 + (spr/100))
    justo = round((spot + 0.0310) * 2000) / 2000
    
    # Cores dinâmicas
    spot_clr = "#00ff88" if s["var"] >= 0 else "#ff4444"
    if spot < (paridade - 0.0030): fut_txt, fut_clr = "▲▲ FUTURO COMPRADO", "#00ff88"
    elif spot > (paridade + 0.0030): fut_txt, fut_clr = "▼▼ FUTURO VENDIDO", "#ff4444"
    else: fut_txt, fut_clr = "● MERCADO EM EQUILÍBRIO", "#777"

    with ui_area.container():
        # Painel ADM (Oculto por padrão)
        if st.session_state.user_type == "ADM":
            with st.expander("AJUSTES TÉCNICOS"):
                with st.form("adm"):
                    v_global["ajuste"] = st.number_input("Paridade", value=v_global["ajuste"], format="%.4f")
                    v_global["ref"] = st.number_input("Ref", value=v_global["ref"], format="%.4f")
                    v_global["notas_mural"] = st.text_area("Mural", v_global["notas_mural"])
                    if st.form_submit_button("ATUALIZAR"): st.rerun()

        st.markdown('<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
        
        # CONTAINER DO SPOT COM ANIMAÇÃO DE PULSO (BONECOS SE MEXENDO)
        st.markdown(f"""
        <div class="s-container live-update">
            <div class="s-text">
                SPOT <span style="color:{spot_clr}">{spot:.4f}</span> 
                <span style="font-size:16px; margin-left:10px; color:{spot_clr}">({s['var']:+.2f}%)</span>
            </div>
            <div class="s-subtext">FECHAMENTO ANTERIOR: {s['prev']:.4f}</div>
            <div class="vies-indicator" style="color:{fut_clr}">{fut_txt}</div>
        </div>
        """, unsafe_allow_html=True)

        # Grids de Preço
        st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{paridade:.4f}</div></div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="d-row">
            <div class="d-label">PREÇO JUSTO</div>
            <div class="sub-grid">
                <div class="sub-item"><span class="sub-l">MÍN</span><span class="sub-v" style="color:#ff4444">{(round((spot+0.0220)*2000)/2000):.4f}</span></div>
                <div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v" style="color:#0088ff">{justo:.4f}</span></div>
                <div class="sub-item"><span class="sub-l">MÁX</span><span class="sub-v" style="color:#00ff88">{(round((spot+0.0420)*2000)/2000):.4f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="note-box">
            <div style="font-size:9px; color:#444; letter-spacing:2px; font-weight:900; margin-bottom:10px;">MORNING CALL</div>
            <div class="note-content">{v_global["notas_mural"]}</div>
        </div>
        """, unsafe_allow_html=True)

        # Rodapé e Ticker
        def fmt_tk(d, n):
            c = "#00ff88" if d['var'] >= 0 else "#ff4444"
            return f"<span class='tk-item'><b>{n}</b> {d['last']:.2f} <span style='color:{c}'>({d['var']:+.2f}%)</span></span>"

        btk = f"{fmt_tk(cache_data['DX-Y.NYB'],'DXY')} {fmt_tk(cache_data['EWZ'],'EWZ')} {fmt_tk(cache_data['EURUSD=X'],'EURUSD')} <span class='tk-item'><b>SPREAD</b> {spr:+.2f}%</span>"
        
        st.markdown(f"""
        <div class="f-bar">
            <div style="font-size:11px; color:#ffff99; letter-spacing:1px;">{v_global["notas"]}</div>
            <div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div>
        </div>
        """, unsafe_allow_html=True)

    time.sleep(1)
