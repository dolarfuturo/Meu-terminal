import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas": "MURAL: AGUARDANDO...",
        "notas2": "INFORMATIVO: OPERACIONAL ATIVO"
    }

v_global = get_global_vars()

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_type = None

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'], label { display: none !important; } .stButton button { width: 100%; background-color: #222; color: white; border: 1px solid #444; margin-top: 20px; }</style>", unsafe_allow_html=True)
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
    .t-header { text-align: center; padding: 15px 0 5px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 12px; font-weight: 700; letter-spacing: 2px; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 20px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; }
    .sub-l { font-size: 8px; color: #888; display: block; margin-bottom: 2px; font-weight: 400; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .v-peq { font-size: 15px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; opacity: 0.9; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 160px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .f-notes { font-family: 'Chakra Petch'; font-size: 11px; color: #ffff99; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1px; }
    .f-notes2 { font-family: 'Chakra Petch'; font-size: 10px; color: #aaaaaa; margin-bottom: 8px; }
    .f-arrows { font-size: 16px; margin: 5px 0; letter-spacing: 8px; }
    .f-line { width: 85%; height: 1px; background: rgba(255,255,255,0.1); }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
    
    /* ESTILO MANUAL POP */
    .m-box { background: #111; border: 1px solid #333; padding: 15px; border-radius: 5px; margin: 10px; }
    .m-item { font-size: 12px; margin-bottom: 8px; font-family: 'Chakra Petch'; }
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE DATA
def get_clean_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, prepost=True)
        t = yf.Ticker(ticker)
        prev = float(t.fast_info.previous_close)
        last = float(df['Close'].iloc[-1]) if not df.empty else prev
        var = ((last - prev) / prev * 100) if prev != 0 else 0
        return {"last": last, "prev": prev, "var": var}
    except:
        return {"last": 0.0, "prev": 0.0, "var": 0.0}

# 6. HEADER COM MANUAL E ADM
c1, c2, c3 = st.columns([1,2,1])
with c1:
    if st.session_state.user_type == "ADM":
        with st.expander("⚙️ ADM"):
            with st.form("adm"):
                v_global["ajuste"] = st.number_input("AJUSTE", value=v_global["ajuste"], format="%.4f")
                v_global["ref"] = st.number_input("REF", value=v_global["ref"], format="%.4f")
                v_global["notas"] = st.text_input("MURAL 1", value=v_global["notas"])
                v_global["notas2"] = st.text_input("MURAL 2", value=v_global["notas2"])
                if st.form_submit_button("OK"): st.rerun()
with c3:
    with st.popover("📖 AJUDA"):
        st.markdown("""
        <div class="m-box">
            <div class="m-item">🟢 <b>BARATO:</b> Procure COMPRA no gráfico.</div>
            <div class="m-item">🔴 <b>CARO:</b> Procure VENDA no gráfico.</div>
            <div class="m-item">🎯 <b>PARIDADE:</b> É o alvo real do preço.</div>
            <div class="m-item">⚠️ <b>EXTREMOS:</b> Bateu em MÍN/MÁX? O preço tende a voltar pro JUSTO.</div>
            <div class="m-item" style="color:#888; font-size:10px;">O Terminal dá a direção. O candle dá o clique.</div>
        </div>
        """, unsafe_allow_html=True)

# 7. LOOP DE EXECUÇÃO
ui_area = st.empty()
while True:
    d_m = get_clean_data("DX-Y.NYB")
    e_m = get_clean_data("EWZ")
    s_m = get_clean_data("BRL=X")
    eu_m = get_clean_data("EURUSD=X")
    
    if d_m["last"] > 0:
        spot = s_m["last"]
        spr = d_m["var"] - e_m["var"]
        justo = round((spot + 0.0310) * 2000) / 2000
        equilibrio = round((v_global["ref"] + 0.0220) * 2000) / 2000
        
        diff = spot - justo
        if diff < -0.0015: msg, clr, arr = "● DOLAR BARATO", "#00aa55", "▲ ▲ ▲ ▲ ▲"
        elif diff > 0.0015: msg, clr, arr = "● DOLAR CARO", "#aa3333", "▼ ▼ ▼ ▼ ▼"
        else: msg, clr, arr = "● DOLAR NEUTRO", "#aaaa00", "◄ ◄ ◄ ► ► ►"
            
        with ui_area.container():
            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {clr}77"><div class="s-text" style="color:{clr}">{msg}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{(v_global["ajuste"]*(1+(spr/100))):.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value c-equi">{equilibrio:.4f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{justo:.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{(round((v_global["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((v_global["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="d-row" style="border-bottom:none; padding-top:10px;"><div class="d-label" style="opacity:0.6;">REGIÃO DE CORREÇÃO</div><div class="sub-grid"><div class="sub-item"><span class="v-peq">{(equilibrio - 0.0110):.4f}</span></div><div class="sub-item"><span class="v-peq">{(equilibrio + 0.0110):.4f}</span></div></div></div>', unsafe_allow_html=True)

            def f_tk(d, n):
                v, p = d["var"], d["last"]
                c = "#00aa55" if v >= 0 else "#aa3333"
                pf = f"{p:.4f}" if n == "SPOT" else f"{p:.2f}"
                return f"<span class='tk-item'><b>{n}</b> {pf} <span style='color:{c}'>({v:+.2f}%)</span></span>"

            btk = f"{f_tk(s_m,'SPOT')} {f_tk(d_m,'DXY')} {f_tk(e_m,'EWZ')} {f_tk(eu_m,'EURUSD')} <span class='tk-item'><b>SPREAD</b> {spr:+.2f}%</span>"
            st.markdown(f'<div class="f-bar"><div class="f-notes">{v_global["notas"]}</div><div class="f-notes2">{v_global["notas2"]}</div><div class="f-line"></div><div class="f-arrows" style="color:{clr}">{arr}</div><div class="f-line"></div><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
