import streamlit as st
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import hashlib

# 1. CONFIGURAÇÃO INICIAL (DEVE SER A PRIMEIRA COISA)
st.set_page_config(page_title="SHARK VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS COMPLETO (PONTO PISCANDO + TOPO FIXO)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container {padding: 0rem !important;}

    /* TRAVA O CABEÇALHO NO TOPO */
    [data-testid="stVerticalBlock"] > div:first-child {
        position: sticky;
        top: 0;
        z-index: 999999;
        background-color: #000000;
        border-bottom: 2px solid #D4AF37;
    }

    /* PONTO VERDE PISCANDO */
    .dot { 
        height: 12px !important; width: 12px !important; 
        background-color: #00FF00 !important; 
        border-radius: 50% !important; 
        display: inline-block !important;
        box-shadow: 0 0 10px #00FF00 !important;
        animation: pulse-glow 1s infinite alternate !important;
        margin-right: 8px !important;
    }
    @keyframes pulse-glow {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0.2; transform: scale(0.8); }
    }

    .title-gold { color: #D4AF37; font-size: 26px; font-weight: 900; text-align: center; margin: 5px 0; }
    .header-grid { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; background: #080808; padding: 10px 0; }
    .h-col { font-size: 9px; color: #FFF; text-align: center; font-weight: bold; }
    .row-container { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; align-items: center; padding: 12px 0; border-bottom: 1px solid #222; }
    .w-col { text-align: center; font-family: monospace; font-size: 15px; font-weight: bold; color: #FFF; }
    .vision-block { display: flex; justify-content: center; gap: 30px; padding: 5px 0; background: #050505; border-bottom: 2px solid #333; }
    
    div.stButton > button { background-color: #D4AF37; color: black; font-weight: bold; width: 100%; border-radius: 5px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 3. SISTEMA DE ACESSO
def verificar_acesso():
    URL_SISTEMA = "https://docs.google.com/spreadsheets/d/1m86_Lj5p7tV9U4sNIKudbU1DVWFgAfaSXSIRATo6G70/export?format=csv"
    CHAVE_MESTRA_ADM = "SHARK_ADM_2026" 
    
    if "autenticado" not in st.session_state:
        st.markdown("<h1 style='text-align:center; color:#D4AF37; font-family:monospace; margin-top:50px;'>SHAKE VISION LOGIN</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            chave = st.text_input("", type="password", placeholder="Chave de Acesso...")
            btn = st.button("ACESSAR TERMINAL CRYPTO")
        
        if btn and chave:
            if chave == CHAVE_MESTRA_ADM:
                st.session_state["autenticado"], st.session_state["usuario"] = True, "ADMINISTRADOR"
                st.rerun()
            try:
                df = pd.read_csv(URL_SISTEMA)
                hash_t = hashlib.sha256(chave.encode()).hexdigest()
                df.columns = df.columns.str.strip()
                valido = df[(df['HASH_SENHA'].astype(str).str.strip() == hash_t) & (df['STATUS'].str.strip() == 'ATIVO')]
                if not valido.empty:
                    st.session_state["autenticado"], st.session_state["usuario"] = True, valido.iloc[0]['CLIENTE']
                    st.rerun()
                else:
                    st.error("❌ Chave Inválida.")
            except:
                pass 
        st.stop()

verificar_acesso()

# 4. CONFIGURAÇÃO DE DADOS
COINS_CONFIG = {
    "BTC-USD": {"label": "BTC/USDT", "dec": 0}, "ETH-USD": {"label": "ETH/USDT", "dec": 0},
    "SOL-USD": {"label": "SOL/USDT", "dec": 3}, "XRP-USD": {"label": "XRP/USDT", "dec": 3},
    "BNB-USD": {"label": "BNB/USDT", "dec": 3}, "DOGE-USD": {"label": "DOGE/USDT", "dec": 3},
    "HYPE-USD": {"label": "HYPE/USDT", "dec": 2}
}

# Inicializa estados de ancoragem
for t in COINS_CONFIG:
    if f'mp_{t}' not in st.session_state:
        st.session_state[f'mp_{t}'] = yf.Ticker(t).fast_info['last_price']
        st.session_state[f'rv_{t}'] = st.session_state[f'mp_{t}']

placeholder = st.empty()

# 5. LOOP DO TERMINAL
while True:
    try:
        now_br = datetime.now(pytz.timezone('America/Sao_Paulo'))
        with placeholder.container():
            st.markdown(f"""
                <div class="top-header-fixed">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 20px; background: #050505;">
                        <div style="color:white; font-size:11px; font-weight:bold; display: flex; align-items: center;">
                            <span class="dot"></span> {st.session_state.get('usuario', 'USER')} | ONLINE
                        </div>
                        <div style="color:#888; font-family:monospace; font-size:11px;">
                            BRASÍLIA: <b>{now_br.strftime('%H:%M:%S')}</b>
                        </div>
                    </div>
                    <div class="title-gold">TERMINAL NEXUS CRYPTO</div>
                    <div style="color:white; font-size:10px; text-align:center; letter-spacing:3px; padding-bottom:5px;">VISÃO DE TUBARÃO</div>
                    <div class="header-grid">
                        <div class="h-col">CÓDIGO</div><div class="h-col">PREÇO</div>
                        <div class="h-col" style="color:#FF4444;">EXAUST. T.</div><div class="h-col" style="color:#FFA500;">TOPO</div>
                        <div class="h-col" style="color:#FFFF00;">DECISÃO</div><div class="h-col" style="color:#00CED1;">RESPIRO</div>
                        <div class="h-col" style="color:#00CED1;">RESP. F.</div><div class="h-col" style="color:#FFFF00;">DECIS. F.</div>
                        <div class="h-col" style="color:#FFA500;">FUNDO</div><div class="h-col" style="color:#00FF00;">EXAUST. F.</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            for t, info in COINS_CONFIG.items():
                price = yf.Ticker(t).fast_info['last_price']
                mp = st.session_state[f'mp_{t}']
                g = 1.0122 if t in ["BTC-USD", "ETH-USD"] else 1.0244
                
                # Lógica Escada
                if ((price / mp) - 1) * 100 >= (g-1)*100: st.session_state[f'mp_{t}'] = mp * g
                elif ((price / mp) - 1) * 100 <= -(g-1)*100: st.session_state[f'mp_{t}'] = mp * (2 - g)

                st.markdown(f"""
                    <div class="row-container">
                        <div class="w-col" style="color:#D4AF37; font-size:13px;">{info['label']}</div>
                        <div class="w-col">{price:,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FF4444;">{(mp * g):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFA500;">{(mp * (1+(g-1)*0.6)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFFF00;">{(mp * (1+(g-1)*0.4)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00CED1;">{(mp * (1+(g-1)*0.2)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00CED1;">{(mp * (1-(g-1)*0.2)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFFF00;">{(mp * (1-(g-1)*0.4)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFA500;">{(mp * (1-(g-1)*0.6)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00FF00;">{(mp * (2-g)):,.{info['dec']}f}</div>
                    </div>
                """, unsafe_allow_html=True)
        time.sleep(1)
    except:
        time.sleep(2)
