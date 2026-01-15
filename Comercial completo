import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL (SIMULANDO BANCO DE DADOS DO ADM)
@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.3845, # Valor do Fechamento/Ajuste B3
        "ref": 5.3845,    # PTAX de referência
        "mural": "MERCADO TRABALHANDO ABAIXO DO AJUSTE. ALVO NA BASE DE 5.362,5."
    }

v_global = get_global_vars()

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_type = None

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'] { display: none; } .stButton button { width: 100%; background-color: #111; color: white; border: 1px solid #333; margin-top: 20px; font-family: 'Orbitron'; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:150px;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#555; font-size:12px; letter-spacing:5px;'>ACESSO RESTRITO</h2>", unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="CHAVE DO TERMINAL")
        if st.button("CONECTAR"):
            if senha == "admin123":
                st.session_state.auth = True
                st.session_state.user_type = "ADM"
                st.rerun()
            elif senha == "trader123":
                st.session_state.auth = True
                st.session_state.user_type = "USER"
                st.rerun()
    st.stop()

# 4. CSS PROFISSIONAL (MINIMALISTA)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; }
    
    /* CABEÇALHO E SPOT */
    .t-header { text-align: center; padding: 15px 0; border-bottom: 1px solid #111; background: #050505; }
    .spot-label { color: #888; font-size: 10px; letter-spacing: 3px; }
    .spot-value { color: #fff; font-size: 42px; font-weight: 900; font-family: 'Chakra Petch'; }
    
    /* RADAR DE OPORTUNIDADE */
    .radar-box { padding: 10px 20px; background: #080808; border-bottom: 1px solid #111; text-align: center; }
    .radar-label { font-size: 9px; color: #444; letter-spacing: 2px; margin-bottom: 5px; }
    
    /* GRIDS DE PREÇO */
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 20px 25px; border-bottom: 1px solid #0f0f0f; }
    .d-label { font-size: 11px; color: #666; font-weight: 700; letter-spacing: 1px; }
    .d-value { font-size: 28px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    /* CORES INSTITUCIONAIS */
    .c-spot { color: #ffffff; } .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; }
    
    /* RODAPÉ E TICKER */
    .f-bar { position: fixed; bottom: 0; width: 100%; background: #050505; border-top: 1px solid #222; padding: 10px 0; z-index: 100; }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; }
    .tk-move { display: inline-block; animation: slide 30s linear infinite; }
    .tk-item { padding-right: 40px; font-family: 'Chakra Petch'; font-size: 13px; color: #aaa; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# 5. MOTOR DE DADOS
def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        data = t.history(period="1d", interval="1m")
        last = data['Close'].iloc[-1]
        prev = t.fast_info.previous_close
        var = ((last - prev) / prev * 100)
        return {"last": last, "var": var}
    except:
        return {"last": 0.0, "var": 0.0}

# 6. INTERFACE
ui_area = st.empty()

while True:
    s_m = get_data("BRL=X")
    d_m = get_data("DX-Y.NYB")
    
    if s_m["last"] > 0:
        spot_real = s_m["last"]
        # Lógica ADM centralizada
        equi = v_global["ajuste"]
        distorcaoo = (spot_real - equi) * 1000 # Distorção em pontos
        
        # Definição de Cor do Radar
        radar_color = "#00cc66" if abs(distorcaoo) > 15 else "#444"
        radar_msg = "OPORTUNIDADE DE EXAUSTÃO" if abs(distorcaoo) > 20 else "MERCADO EM EQUILÍBRIO"

        with ui_area.container():
            # PAINEL ADM (Só visível para você)
            if st.session_state.user_type == "ADM":
                with st.expander("TORRE DE COMANDO (ADM)"):
                    v_global["ajuste"] = st.number_input("DEFINIR EQUILÍBRIO (PTAX/AJUSTE)", value=v_global["ajuste"], format="%.4f")
                    v_global["mural"] = st.text_input("MENSAGEM PARA ASSINANTES", value=v_global["mural"])
                    if st.button("ATUALIZAR TERMINAIS"): st.rerun()

            # CABEÇALHO COM SPOT
            st.markdown(f"""
                <div class="t-header">
                    <div class="spot-label">DÓLAR SPOT (REAL TIME)</div>
                    <div class="spot-value c-spot">{spot_real:.4f}</div>
                </div>
            """, unsafe_allow_html=True)

            # RADAR DE OPORTUNIDADE (SPOT vs EQUILÍBRIO)
            st.markdown(f"""
                <div class="radar-box">
                    <div class="radar-label" style="color:{radar_color}">{radar_msg}</div>
                    <div style="background:#111; height:4px; width:100%; border-radius:10px; overflow:hidden;">
                        <div style="background:{radar_color}; height:100%; width:{min(abs(distorcaoo)*4, 100)}%; transition:0.5s;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # BLOCO DE PREÇOS (LIMPO)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO ADM</div><div class="d-value c-equi">{equi:.4f}</div></div>', unsafe_allow_html=True)
            
            # Cálculo de 11 e 22 pontos (Frequência Automática)
            st.markdown(f"""
            <div class="d-row">
                <div class="d-label">ZONA DE EXAUSTÃO (BASE)</div>
                <div style="display:flex; gap:20px;">
                    <div style="text-align:right"><span class="d-label" style="display:block">MIN (-22)</span><span class="d-value c-min">{(equi - 0.0220):.4f}</span></div>
                    <div style="text-align:right"><span class="d-label" style="display:block">MAX (+22)</span><span class="d-value c-max">{(equi + 0.0220):.4f}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="d-row">
                <div class="d-label">ZONA DE CORREÇÃO (FREQUÊNCIA)</div>
                <div style="display:flex; gap:20px;">
                    <div style="text-align:right"><span class="d-label" style="display:block">SUP (-11)</span><span class="d-value" style="color:#aa6600">{(equi - 0.0110):.4f}</span></div>
                    <div style="text-align:right"><span class="d-label" style="display:block">RES (+11)</span><span class="d-value" style="color:#aa6600">{(equi + 0.0110):.4f}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # RODAPÉ COM TICKER
            ticker_html = f"<span class='tk-item'><b>SPOT</b> {spot_real:.4f}</span> <span class='tk-item'><b>DXY</b> {d_m['last']:.2f} ({d_m['var']:+.2f}%)</span> <span class='tk-item'><b>MURAL:</b> {v_global['mural']}</span>"
            st.markdown(f"""
                <div class="f-bar">
                    <div class="tk-wrap">
                        <div class="tk-move">{ticker_html} {ticker_html}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    time.sleep(2)
