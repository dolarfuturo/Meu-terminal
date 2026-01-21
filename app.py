import streamlit as st
import yfinance as yf
import time
import pandas as pd

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL (Persistência de dados)
if 'v_global' not in st.session_state:
    st.session_state.v_global = {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas_mural": "RESUMO DA ABERTURA E AGENDA: AGUARDANDO ATUALIZAÇÃO...",
        "notas": "MURAL: AGUARDANDO...",
        "notas2": "INFORMATIVO: OPERACIONAL ATIVO"
    }

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
    
    @keyframes pulse_dot { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
    .update-dot { color: #00ff00; animation: pulse_dot 0.8s infinite; margin-right: 8px; font-size: 14px; }

    .t-header { text-align: center; padding: 15px 0 5px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; display: flex; justify-content: center; align-items: center; }
    .t-bold { color: #fff; font-weight: 900; }
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 18px; font-weight: 700; letter-spacing: 1px; font-family: 'Chakra Petch'; }
    .vies-indicator { font-size: 13px; font-weight: 900; letter-spacing: 2px; margin-top: 6px; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; }
    .d-value { font-size: 26px; font-family: 'Chakra Petch'; font-weight: 700; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; min-height: 100px; }
    .note-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; line-height: 1.5; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 160px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 30s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def fetch_data(ticker):
    try:
        # Forçamos o download sem cache para o Spot mexer
        df = yf.download(ticker, period="1d", interval="1m", progress=False, label="ticker_download")
        if not df.empty:
            last = float(df['Close'].iloc[-1])
            prev = float(df['Open'].iloc[0]) # Comparação com abertura do dia para variação real
            var = ((last - prev) / prev * 100)
            return {"last": last, "var": var}
    except: pass
    return {"last": 0.0, "var": 0.0}

ui_area = st.empty()

while True:
    # Coleta de dados com limpeza de cache para garantir movimento
    s_m = fetch_data("BRL=X")
    d_m = fetch_data("DX-Y.NYB")
    e_m = fetch_data("EWZ")
    eu_m = fetch_data("EURUSD=X")
    
    if s_m["last"] > 0:
        spot = s_m["last"]
        spr = d_m["var"] - e_m["var"]
        paridade = st.session_state.v_global["ajuste"] * (1 + (spr/100))
        justo = round((spot + 0.0310) * 2000) / 2000
        
        v_clr = "#00ff00" if s_m['var'] >= 0 else "#ff4444"
        
        with ui_area.container():
            # PAINEL ADM NO TOPO
            if st.session_state.user_type == "ADM":
                with st.expander("⚙️ VARIÁVEIS"):
                    with st.form("adm_f"):
                        c1, c2 = st.columns(2)
                        st.session_state.v_global["ajuste"] = c1.number_input("PARIDADE", value=st.session_state.v_global["ajuste"], format="%.4f")
                        st.session_state.v_global["ref"] = c2.number_input("REF", value=st.session_state.v_global["ref"], format="%.4f")
                        st.session_state.v_global["notas_mural"] = st.text_area("MURAL", value=st.session_state.v_global["notas_mural"])
                        if st.form_submit_button("SALVAR"): st.rerun()

            # TÍTULO COM PONTO VERDE AO LADO DO T
            st.markdown(f'<div class="t-header"><div class="t-title"><span class="update-dot">●</span>TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
            
            # SPOT BRANCO + VAR COLORIDA SEM ()
            st.markdown(f"""
            <div class="s-container">
                <div class="s-text">
                    SPOT <span style="color:#fff">{spot:.4f}</span> 
                    <span style="color:{v_clr}; margin-left:12px;">{s_m['var']:+.2f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # DADOS FINANCEIROS
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="d-value c-jus">{justo:.4f}</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="note-box"><div class="note-content">{st.session_state.v_global["notas_mural"]}</div></div>', unsafe_allow_html=True)

            # ESTEIRA RODAPÉ
            def f_tk(d, n):
                c = "#00ff00" if d['var'] >= 0 else "#ff4444"
                return f"<span class='tk-item'><b>{n}</b> {d['last']:.4f} <span style='color:{c}'>{d['var']:+.2f}%</span></span>"

            btk = f"{f_tk(s_m,'SPOT')} {f_tk(d_m,'DXY')} {f_tk(e_m,'EWZ')} {f_tk(eu_m,'EURUSD')}"
            st.markdown(f'<div class="f-bar"><div class="tk-wrap"><div class="tk-move">{btk} {btk} {btk}</div></div></div>', unsafe_allow_html=True)
    
    time.sleep(1)
