import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. AUTO-REFRESH (Faz o SPOT mexer a cada 1 segundo)
# Isso evita que a tela fique preta por causa de um loop infinito travado
st.markdown("""
    <head><meta http-equiv="refresh" content="1"></head>
""", unsafe_allow_html=True)

# 3. ESTADO GLOBAL
if 'v_global' not in st.session_state:
    st.session_state.v_global = {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas_mural": "RESUMO DA ABERTURA E AGENDA: AGUARDANDO ATUALIZAÇÃO...",
        "notas": "MURAL: AGUARDANDO...",
        "notas2": "INFORMATIVO: OPERACIONAL ATIVO"
    }

# 4. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'] { display: none; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("CHAVE", type="password")
        if st.button("ENTRAR"):
            if senha in ["admin123", "trader123"]:
                st.session_state.auth = True
                st.session_state.user_type = "ADM" if senha == "admin123" else "USER"
                st.rerun()
    st.stop()

# 5. CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; }
    
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }
    .dot { color: #00ff00; animation: blink 1s infinite; margin-right: 8px; }

    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid #222; }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    
    .s-container { text-align: center; padding: 15px 0; border-bottom: 2px solid #333; }
    .s-text { font-size: 22px; font-weight: 700; font-family: 'Chakra Petch'; }
    
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #fff; font-weight: 900; }
    .d-value { font-size: 28px; font-family: 'Chakra Petch'; font-weight: 700; color: #cc9900; }
</style>
""", unsafe_allow_html=True)

# 6. COLETA DE DADOS (SPOT)
def get_data():
    try:
        # Pega o ticker do dólar
        df = yf.download("BRL=X", period="1d", interval="1m", progress=False)
        if not df.empty:
            last = float(df['Close'].iloc[-1])
            prev = float(df['Open'].iloc[0])
            var = ((last - prev) / prev * 100)
            return last, var
    except: pass
    return 0.0, 0.0

spot, var_spot = get_data()
v_clr = "#00ff00" if var_spot >= 0 else "#ff4444"

# --- INTERFACE ---

# PAINEL ADM NO TOPO
if st.session_state.get("user_type") == "ADM":
    with st.expander("⚙️ VARIÁVEIS"):
        with st.form("adm_f"):
            st.session_state.v_global["ajuste"] = st.number_input("PARIDADE", value=st.session_state.v_global["ajuste"], format="%.4f")
            st.session_state.v_global["notas_mural"] = st.text_area("MURAL", value=st.session_state.v_global["notas_mural"])
            if st.form_submit_button("SALVAR"): st.rerun()

# TÍTULO COM PONTO VERDE AO LADO DO T
st.markdown(f'<div class="t-header"><div class="t-title"><span class="dot">●</span>TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)

# SPOT BRANCO + VARIAÇÃO VERDE/VERMELHO SEM ( )
st.markdown(f"""
<div class="s-container">
    <div class="s-text">
        SPOT <span style="color:#fff">{spot:.4f}</span> 
        <span style="color:{v_clr}; margin-left:12px;">{var_spot:+.2f}%</span>
    </div>
</div>
""", unsafe_allow_html=True)

# PARIDADE
spr = 0.0 # Simplificado para evitar erro de tela preta
paridade = st.session_state.v_global["ajuste"] * (1 + (spr/100))
st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value">{paridade:.4f}</div></div>', unsafe_allow_html=True)

# MURAL
st.markdown(f'<div style="padding:20px; color:#666; font-size:13px; font-family:Chakra Petch;">{st.session_state.v_global["notas_mural"]}</div>', unsafe_allow_html=True)
