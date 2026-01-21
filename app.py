import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
if 'v_global' not in st.session_state:
    st.session_state.v_global = {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas_mural": "RESUMO DA ABERTURA E AGENDA: AGUARDANDO ATUALIZAÇÃO..."
    }

# 3. CONTROLE DE ACESSO (SEM BUG DE TELA BRANCA)
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

# 4. AUTO-REFRESH (SÓ ATIVA APÓS LOGIN PARA NÃO BUGAR)
st.markdown('<head><meta http-equiv="refresh" content="2"></head>', unsafe_allow_html=True)

# 5. CSS DO TERMINAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
    .update-dot { color: #00ff00; animation: blink 1s infinite; margin-right: 8px; font-size: 14px; }

    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; display: flex; justify-content: center; align-items: center; }
    .t-bold { color: #fff; font-weight: 900; }
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; border-bottom: 2px solid #222; }
    .s-text { font-size: 18px; font-weight: 700; letter-spacing: 1px; font-family: 'Chakra Petch'; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; }
    .d-value { font-size: 26px; font-family: 'Chakra Petch'; font-weight: 700; color: #cc9900; }
    .note-box { background: #050505; border-top: 1px solid #111; padding: 15px 20px; min-height: 100px; }
    .note-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# 6. DADOS
def get_spot():
    try:
        df = yf.download("BRL=X", period="1d", interval="1m", progress=False)
        if not df.empty:
            last = float(df['Close'].iloc[-1])
            prev = float(df['Open'].iloc[0])
            var = ((last - prev) / prev * 100)
            return last, var
    except: pass
    return 0.0, 0.0

spot, var_spot = get_spot()
v_clr = "#00cc66" if var_spot >= 0 else "#cc3333"

# 7. INTERFACE
# PAINEL ADM NO TOPO
if st.session_state.user_type == "ADM":
    with st.expander("⚙️ VARIÁVEIS DO SISTEMA"):
        with st.form("adm_panel"):
            c1, c2 = st.columns(2)
            st.session_state.v_global["ajuste"] = c1.number_input("PARIDADE", value=st.session_state.v_global["ajuste"], format="%.4f")
            st.session_state.v_global["ref"] = c2.number_input("REF INST", value=st.session_state.v_global["ref"], format="%.4f")
            st.session_state.v_global["notas_mural"] = st.text_area("MORNING CALL", value=st.session_state.v_global["notas_mural"])
            if st.form_submit_button("SALVAR"): st.rerun()

# TÍTULO COM PONTO VERDE AO LADO DO T
st.markdown(f'<div class="t-header"><div class="t-title"><span class="update-dot">●</span>TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)

# SPOT BRANCO + VARIAÇÃO VERDE/VERMELHA SEM ()
st.markdown(f"""
<div class="s-container">
    <div class="s-text">
        SPOT <span style="color:#fff">{spot:.4f}</span> 
        <span style="color:{v_clr}; margin-left:10px;">{var_spot:+.2f}%</span>
    </div>
</div>
""", unsafe_allow_html=True)

# DADOS
st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value">{st.session_state.v_global["ajuste"]:.4f}</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="d-row"><div class="d-label">REF. INSTITUCIONAL</div><div class="d-value" style="color:#00cccc">{st.session_state.v_global["ref"]:.4f}</div></div>', unsafe_allow_html=True)

# MURAL
st.markdown(f'<div class="note-box"><div class="note-content">{st.session_state.v_global["notas_mural"]}</div></div>', unsafe_allow_html=True)
