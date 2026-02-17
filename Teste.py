import streamlit as st
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import hashlib

# 1. SETUP ALPHA & TRAVA DE SEGURANÇA 
st.set_page_config(page_title="SHARK VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

def verificar_acesso():
    URL_SISTEMA = "https://docs.google.com/spreadsheets/d/1m86_Lj5p7tV9U4sNIKudbU1DVWFgAfaSXSIRATo6G70/export?format=csv"
    
    if "autenticado" not in st.session_state:
        st.markdown("<h1 style='text-align:center; color:#D4AF37; font-family:monospace;'>SHAKE VISION LOGIN</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:white;'>Terminal K97 - Insira sua Chave de Licença</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            chave = st.text_input("", type="password", placeholder="Digite a Chave...")
        
        if chave:
            try:
                df = pd.read_csv(URL_SISTEMA)
                hash_tentativa = hashlib.sha256(chave.encode()).hexdigest()
                df.columns = df.columns.str.strip()
                df['HASH_SENHA'] = df['HASH_SENHA'].astype(str).str.strip()
                df['STATUS'] = df['STATUS'].astype(str).str.strip()

                valido = df[(df['HASH_SENHA'] == hash_tentativa) & (df['STATUS'] == 'ATIVO')]
                
                if not valido.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = valido.iloc[0]['CLIENTE']
                    st.rerun()
                else:
                    st.error("❌ Acesso Negado: Chave incorreta ou plano expirado.")
            except Exception as e:
                st.error(f"Erro de conexão com banco de dados: {e}")
        st.stop()

verificar_acesso()

COINS_CONFIG = {
    "BTC-USD": {"label": "BTC/USDT", "dec": 0},
    "ETH-USD": {"label": "ETH/USDT", "dec": 0},
    "SOL-USD": {"label": "SOL/USDT", "dec": 2},
    "XRP-USD": {"label": "XRP/USDT", "dec": 2}
}

def get_alpha_midpoint(ticker):
    try:
        price = yf.Ticker(ticker).fast_info['last_price']
        return price if price else 0
    except: return 0

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .top-header-fixed { position: sticky; top: 0; background: #000000; z-index: 1000; border-bottom: 2px solid #D4AF37; }
    .top-bar { display: flex; justify-content: space-between; align-items: center; padding: 5px 20px; background: #050505; }
    .clocks { display: flex; gap: 30px; color: #888; font-family: monospace; font-size: 12px; }
    .title-gold { color: #D4AF37; font-size: 28px; font-weight: 900; text-align: center; }
    .header-grid { display: grid; grid-template-columns: 1.5fr 1.2fr 1fr 1fr 1fr 1fr 1fr 1fr; width: 100%; padding: 10px 0; background: #080808; }
    .h-col { font-size: 10px; color: #FFF; text-align: center; font-weight: 800; }
    .row-container { display: grid; grid-template-columns: 1.5fr 1.2fr 1fr 1fr 1fr 1fr 1fr 1fr; width: 100%; align-items: center; padding: 12px 0; border-bottom: 1px solid #222;}
    .w-col { text-align: center; font-family: 'monospace'; font-size: 17px; font-weight: 800; color: #FFF; }
    .vision-block { display: flex; justify-content: center; gap: 60px; padding: 10px 0; border-bottom: 2px solid #333; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

for t in COINS_CONFIG:
    if f'rv_{t}' not in st.session_state:
        val = get_alpha_midpoint(t)
        st.session_state[f'rv_{t}'] = val
        st.session_state[f'mp_{t}'] = val

placeholder = st.empty()

while True:
    try:
        with placeholder.container():
            tz_br, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
            now_br, now_ny, now_ld = datetime.now(tz_br), datetime.now(tz_ny), datetime.now(tz_ld)

            st.markdown(f"""
                <div class="top-header-fixed">
                    <div class="top-bar">
                        <div class="live-indicator">{st.session_state['usuario']} | ONLINE</div>
                        <div class="clocks">
                            <div class="clock-item">BR: <b>{now_br.strftime('%H:%M:%S')}</b></div>
                            <div class="clock-item">NY: <b>{now_ny.strftime('%H:%M:%S')}</b></div>
                            <div class="clock-item">LD: <b>{now_ld.strftime('%H:%M:%S')}</b></div>
                        </div>
                    </div>
                    <div class="title-gold">SHARK VISION CRYPTO</div>
                    <div class="header-grid">
                        <div class="h-col">CÓDIGO</div><div class="h-col">PREÇO</div>
                        <div class="h-col" style="color:#FF4444;">EXAUSTÃO T.</div><div class="h-col" style="color:#FFA500;">TOPO</div>
                        <div class="h-col" style="color:#FFFF00;">DECISÃO</div><div class="h-col" style="color:#00CED1;">RESPIRO</div>
                        <div class="h-col" style="color:#FFA500;">FUNDO</div><div class="h-col" style="color:#00FF00;">EXAUSTÃO F.</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            for t, info in COINS_CONFIG.items():
                price = yf.Ticker(t).fast_info['last_price']
                mp, rv = st.session_state[f'mp_{t}'], st.session_state[f'rv_{t}']
                
                # PARÂMETROS SIMÉTRICOS K97
                p_ex_t, p_top, p_dec, p_res = 1.0122, 1.0082, 1.0061, 1.0040
                p_fun, p_ex_f = 0.9939, 0.9878 # Simetria: -0.61% e -1.22%
                
                var_escada = ((price / mp) - 1) * 100
                if var_escada >= 1.22: st.session_state[f'mp_{t}'] = mp * 1.0122
                elif var_escada <= -1.22: st.session_state[f'mp_{t}'] = mp * 0.9878
                
                var_reset = ((price / rv) - 1) * 100
                cor_v = "#00FF00" if var_reset >= 0 else "#FF4444"
                
                st.markdown(f"""
                    <div class="row-container">
                        <div class="w-col" style="color:#D4AF37;">{info['label']}</div>
                        <div class="w-col">
                            <div>{price:,.{info['dec']}f}</div>
                            <div style="color:{cor_v}; font-size:10px;">{var_reset:+.2f}%</div>
                        </div>
                        <div class="w-col" style="color:#FF4444;">{(mp * p_ex_t):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFA500;">{(mp * p_top):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFFF00;">{(mp * p_dec):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00CED1;">{(mp * p_res):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFA500;">{(mp * p_fun):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00FF00;">{(mp * p_ex_f):,.{info['dec']}f}</div>
                    </div>
                    <div class="vision-block">
                        <div style="color:#BBB; font-size:12px;">RESETVISION: <b>{rv:,.{info['dec']}f}</b></div>
                        <div style="color:#00e6ff; font-size:12px;">ÂNCOVISION: <b>{mp:,.{info['dec']}f}</b></div>
                    </div>
                """, unsafe_allow_html=True)
        
        time.sleep(1)
    except Exception as e:
        st.error(f"Erro no loop: {e}")
        time.sleep(5)
