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
        "notas_mural": "RESUMO DA ABERTURA E AGENDA: AGUARDANDO ATUALIZAÇÃO...",
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
    
    @keyframes blinker { 50% { opacity: 0; } }
    .update-dot { color: #00ff00; margin-right: 8px; animation: blinker 1s linear infinite; }

    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 18px; font-weight: 700; letter-spacing: 1px; font-family: 'Chakra Petch'; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; display: flex; flex-direction: column; }
    .sub-l { font-size: 8px; color: #888; display: block; margin-bottom: 2px; font-weight: 400; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 160px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_clean_data(ticker):
    try:
        # Força o download sem usar cache do Streamlit ou da lib
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not data.empty:
            last = float(data['Close'].iloc[-1])
            prev = float(data['Open'].iloc[0])
            var = ((last - prev) / prev * 100)
            return {"last": last, "var": var}
    except: pass
    return {"last": 0.0, "var": 0.0}

ui_area = st.empty()
while True:
    s_m = get_clean_data("BRL=X")
    d_m = get_clean_data("DX-Y.NYB")
    e_m = get_clean_data("EWZ")
    
    if s_m["last"] > 0:
        spot = s_m["last"]
        spr = d_m["var"] - e_m["var"]
        paridade = v_global["ajuste"]*(1+(spr/100))
        
        v_clr = "#00cc66" if s_m['var'] >= 0 else "#cc3333"

        with ui_area.container():
            # PAINEL ADM
            if st.session_state.user_type == "ADM":
                with st.expander("⚙️ PAINEL"):
                    with st.form("adm_f"):
                        v_global["ajuste"] = st.number_input("PARIDADE", value=v_global["ajuste"], format="%.4f")
                        v_global["ref"] = st.number_input("REF INST", value=v_global["ref"], format="%.4f")
                        v_global["notas_mural"] = st.text_area("MORNING CALL", value=v_global["notas_mural"])
                        if st.form_submit_button("SALVAR"): st.rerun()

            # TÍTULO COM PONTO PISCANDO
            st.markdown(f'<div class="t-header"><div class="t-title"><span class="update-dot">●</span>TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
            
            # SPOT BRANCO + VARIAÇÃO
            st.markdown(f"""
            <div class="s-container">
                <div class="s-text">
                    SPOT <span style="color:#fff">{spot:.4f}</span> 
                    <span style="color:{v_clr}; margin-left:10px;">{s_m['var']:+.2f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # REGIÃO DE CORREÇÃO (VOLTOU)
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari" style="font-size:26px; font-family:Chakra Petch;">{paridade:.4f}</div></div>', unsafe_allow_html=True)
            
            # GRADES DE MIN/JUSTO/MAX (REGIAO DE CORRECAO)
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{(round((spot+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{(round((v_global["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((v_global["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div style="padding:20px; color:#999; font-family:Chakra Petch;">{v_global["notas_mural"]}</div>', unsafe_allow_html=True)

            # ESTEIRA
            btk = f"<span class='tk-item'><b>SPOT</b> {spot:.4f}</span> <span class='tk-item'><b>DXY</b> {d_m['last']:.2f}</span>"
            st.markdown(f'<div class="f-bar"><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
    
    time.sleep(1)
