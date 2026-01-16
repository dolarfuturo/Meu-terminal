import streamlit as st
import yfinance as yf
import time

# 1. SETUP
st.set_page_config(page_title="TERMINAL DÓLAR", layout="wide", initial_sidebar_state="collapsed")

# 2. INICIALIZAÇÃO DE VARIÁVEIS (MANTENDO O RESTO)
defaults = {
    'ptax': 5.4000, 'fech': 5.4000, 'ref': 5.4000, 'ajuste': 5.4000,
    'v22': 0.0220, 'v31': 0.0310, 'v42': 0.0420,
    'txt_topo': "GERENCIAMENTO É A CHAVE",
    'show_settings': False
}
for key, value in defaults.items():
    if key not in st.session_state: st.session_state[key] = value

# 3. CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], footer, [data-testid="stToolbar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    
    .stNumberInput div div input, .stTextInput div div input { 
        background-color: #111 !important; color: #fff !important; border: 1px solid #333 !important; font-size: 11px !important; 
    }
    .stButton button { background-color: #111 !important; color: #888 !important; border: 1px solid #333 !important; font-size: 10px !important; }

    .t-header { text-align: center; padding-top: 5px; }
    .t-title { font-size: 24px; letter-spacing: 5px; font-weight: 300; } 
    .t-bold { font-weight: 900; } 
    .t-line { width: 60%; height: 1px; background: #333; margin: 8px auto 10px auto; }
    
    .gauge-container { position: relative; width: 140px; height: 70px; margin: 0 auto; overflow: hidden; }
    .gauge-bg { position: absolute; top: 0; left: 0; width: 140px; height: 140px; border-radius: 50%; background: conic-gradient(#ff3333 0deg 60deg, #ffff00 60deg 120deg, #00ff88 120deg 180deg, #000 180deg); transform: rotate(-90deg); }
    .gauge-cover { position: absolute; top: 10px; left: 10px; width: 120px; height: 120px; background: #000; border-radius: 50%; }
    .gauge-needle { position: absolute; bottom: 0; left: 50%; width: 2px; height: 60px; background: #fff; transform-origin: bottom center; transition: all 0.5s ease; }

    .btn-alerta { width: 220px; margin: 8px auto; padding: 4px; border-radius: 4px; font-size: 10px; font-weight: 900; text-align: center; letter-spacing: 2px; }
    
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; border-bottom: 1px solid #111; }
    .d-label { font-size: 10px; font-weight: 900; color: #777; }
    .d-value { font-size: 19px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .corr-box { display: flex; flex-direction: column; align-items: center; font-family: 'Chakra Petch'; font-size: 14px; }
    .val-11 { font-weight: 700; color: #ffff00; }
    .val-22 { font-weight: 400; color: #ffff00; }

    .txt-editavel { text-align: center; font-family: 'Chakra Petch'; font-size: 11px; color: #666; margin-top: 15px; margin-bottom: 35px; text-transform: uppercase; }

    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 35px; background: #050505; border-top: 1px solid #222; display: flex; align-items: center; z-index: 999; overflow: hidden; }
    .tk-move { white-space: nowrap; animation: move 30s linear infinite; display: flex; align-items: center; }
    .tk-item { padding-right: 50px; font-family: 'Chakra Petch'; font-size: 11px; font-weight: 700; }
    @keyframes move { from { transform: translateX(100%); } to { transform: translateX(-100%); } }
</style>
""", unsafe_allow_html=True)

# 4. BOTÃO SET/FECHAR
if st.button("⚙️ SET" if not st.session_state.show_settings else "✖ FECHAR"):
    st.session_state.show_settings = not st.session_state.show_settings
    st.rerun()

# 5. MENU DE VARIÁVEIS (EXATAMENTE O QUE PEDIU)
if st.session_state.show_settings:
    with st.container():
        c1, c2, c3, c4 = st.columns(4)
        st.session_state.ptax = c1.number_input("PTAX", value=st.session_state.ptax, format="%.4f")
        st.session_state.fech = c2.number_input("FECH", value=st.session_state.fech, format="%.4f")
        st.session_state.ref = c3.number_input("REF", value=st.session_state.ref, format="%.4f")
        st.session_state.ajuste = c4.number_input("PARID", value=st.session_state.ajuste, format="%.4f")
        
        v1, v2, v3 = st.columns(3)
        st.session_state.v22 = v1.number_input("VAR 22", value=st.session_state.v22, format="%.4f")
        st.session_state.v31 = v2.number_input("VAR 31", value=st.session_state.v31, format="%.4f")
        st.session_state.v42 = v3.number_input("VAR 42", value=st.session_state.v42, format="%.4f")
        
        st.session_state.txt_topo = st.text_input("TEXTO SOBRE O TICKER", value=st.session_state.txt_topo)
