import streamlit as st
import yfinance as yf
import time
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL DOLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. FUNÇÃO PARA CAPTURAR PTAX (Simulada via API do BCB)
def get_ptax_bcb():
    # Aqui entraria a chamada de API: https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/
    # Por enquanto, retorna valores base para o layout
    return {
        "P1": 5.4120, "P2": 5.4150, "P3": 0.0000, "P4": 0.0000, "OFICIAL": 0.0000
    }

# 3. ESTADO GLOBAL
if 'ajuste' not in st.session_state:
    st.session_state.ajuste = 5.4000
    st.session_state.ref = 5.4000
    st.session_state.mural = ""

# ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'], label { display: none !important; } .stButton button { width: 100%; background-color: #222; color: white; border: 1px solid #444; margin-top: 20px; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:150px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="CHAVE DE ACESSO")
        if st.button("ENTRAR"):
            if senha == "admin123":
                st.session_state.auth, st.session_state.user_type = True, "ADM"
                st.rerun()
            elif senha == "trader123":
                st.session_state.auth, st.session_state.user_type = True, "USER"
                st.rerun()
    st.stop()

# 4. CSS ORIGINAL ENCAIXADO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    .t-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-bottom: 1px solid #111; }
    .t-title { color: #555; font-size: 11px; letter-spacing: 3px; }
    .t-bold { color: #fff; font-weight: 900; }
    .spot-mini { font-family: 'Chakra Petch'; font-size: 26px; font-weight: 700; color: #fff; }
    
    .s-container { text-align: center; padding: 6px 0; border-bottom: 1px solid #111; position: relative; }
    .thermo-line { position: absolute; bottom: 0; left: 50%; height: 2px; transition: all 0.5s; transform: translateX(-50%); }
    .s-text { font-size: 10px; font-weight: 700; letter-spacing: 2px; }
    
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 10px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .sub-grid { display: flex; gap: 12px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 65px; display: flex; flex-direction: column; }
    .sub-l { font-size: 8px; color: #888; margin-bottom: 1px; }
    .sub-v { font-size: 17px; font-family: 'Chakra Petch'; font-weight: 700; }
    .d-value { font-size: 22px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    
    /* BLOCO PTAX */
    .ptax-grid { display: flex; justify-content: space-around; background: #080808; padding: 8px 0; border-bottom: 1px solid #111; }
    .pt-item { text-align: center; }
    .pt-l { font-size: 8px; color: #555; font-weight: 900; }
    .pt-v { font-size: 14px; font-family: 'Chakra Petch'; color: #aaa; }
    .pt-on { color: #00cccc; font-weight: 700; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 45px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; }
    .tk-move { display: inline-block; animation: slide 45s linear infinite; white-space: nowrap; }
    .tk-item { padding-right: 40px; display: inline-block; font-family: 'Chakra Petch'; font-size: 12px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_clean_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d", interval="1m")
        last = df['Close'].iloc[-1]
        var = ((last - t.fast_info.previous_close) / t.fast_info.previous_close * 100)
        return {"last": last, "var": var}
    except: return {"last": 0.0, "var": 0.0}

ui_area = st.empty()

while True:
    d_m, e_m, s_m, eu_m = get_clean_data("DX-Y.NYB"), get_clean_data("EWZ"), get_clean_data("BRL=X"), get_clean_data("EURUSD=X")
    ptax = get_ptax_bcb() # Chamada da PTAX
    
    if d_m["last"] > 0:
        spot = s_m["last"]
        spr = d_m["var"] - e_m["var"]
        justo = round((spot + 0.0310) * 2000) / 2000
        equi = round((st.session_state.ref + 0.0220) * 2000) / 2000
        
        dist_pts = abs(spot - equi) * 1000
        therm_width = min(dist_pts * 4, 100)
        
        diff_j = spot - justo
        if diff_j < -0.0015: msg, clr = "● PRECIFICAÇÃO DE ALTA", "#00ff88"
        elif diff_j > 0.0015: msg, clr = "● PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: msg, clr = "● PRECIFICAÇÃO NEUTRA", "#ffff00"
            
        with ui_area.container():
            # HEADER
            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div><div class="spot-mini">{spot:.4f}</div></div>', unsafe_allow_html=True)
            
            # TERMÔMETRO INTEGRADO
            st.markdown(f'<div class="s-container"><div class="s-text" style="color:{clr}">{msg}</div><div class="thermo-line" style="width: {therm_width}%; background: {clr}; box-shadow: 0 0 10px {clr};"></div></div>', unsafe_allow_html=True)
            
            # BLOCO PTAX AUTOMÁTICA (NOVO)
            st.markdown(f"""
                <div class="ptax-grid">
                    <div class="pt-item"><div class="pt-l">PRÉVIA 1</div><div class="pt-v {'pt-on' if ptax['P1']>0 else ''}">{ptax['P1']:.4f}</div></div>
                    <div class="pt-item"><div class="pt-l">PRÉVIA 2</div><div class="pt-v {'pt-on' if ptax['P2']>0 else ''}">{ptax['P2']:.4f}</div></div>
                    <div class="pt-item"><div class="pt-l">PRÉVIA 3</div><div class="pt-v {'pt-on' if ptax['P3']>0 else ''}">{ptax['P3']:.4f}</div></div>
                    <div class="pt-item"><div class="pt-l">PRÉVIA 4</div><div class="pt-v {'pt-on' if ptax['P4']>0 else ''}">{ptax['P4']:.4f}</div></div>
                    <div class="pt-item"><div class="pt-l">OFICIAL</div><div class="pt-v {'pt-on' if ptax['OFICIAL']>0 else ''}" style="color:#fff;">{ptax['OFICIAL']:.4f}</div></div>
                </div>
            """, unsafe_allow_html=True)

            # LINHAS DE PREÇO (ORIGINAIS)
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value" style="color:#cc9900">{(st.session_state.ajuste*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value" style="color:#00cccc">{equi:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v" style="color:#cc3333">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v" style="color:#0066cc">{justo:.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v" style="color:#00cc66">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v" style="color:#cc3333">{(round((st.session_state.ref+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v" style="color:#0066cc">{(round((st.session_state.ref+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v" style="color:#00cc66">{(round((st.session_state.ref+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            
            # RODAPÉ
            def f_tk(d, n):
                v, p = d["var"], d["last"]
                c = "#00ff88" if v >= 0 else "#ff3333"
                pf = f"{p:.4f}" if n == "SPOT" else f"{p:.2f}"
                return f"<span class='tk-item'><b>{n}</b> {pf} <span style='color:{c}'>({v:+.2f}%)</span></span>"

            mural = f"<span class='tk-item'><b>MURAL:</b> {st.session_state.mural}</span>" if st.session_state.mural else ""
            btk = f"{f_tk(s_m,'SPOT')} {f_tk(d_m,'DXY')} {f_tk(e_m,'EWZ')} {f_tk(eu_m,'EURUSD')} <span class='tk-item'><b>SPREAD</b> {spr:+.2f}%</span> {mural}"
            st.markdown(f'<div class="f-bar"><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
