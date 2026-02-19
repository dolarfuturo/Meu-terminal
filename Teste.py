import streamlit as st
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import hashlib
import uuid
from streamlit_gsheets import GSheetsConnection

# 1. SETUP & CONFIGURAÇÃO VISUAL SHARK
st.set_page_config(page_title="SHARK VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
    [data-testid="stVerticalBlock"] > div:first-child {
        position: sticky; top: 0; z-index: 999999; background-color: #000000; border-bottom: 2px solid #D4AF37;
    }
    .dot { 
        height: 12px !important; width: 12px !important; background-color: #00FF00 !important; 
        border-radius: 50% !important; display: inline-block !important;
        box-shadow: 0 0 10px #00FF00 !important; animation: pulse-glow 1s infinite alternate !important;
        margin-right: 8px !important;
    }
    @keyframes pulse-glow { from { opacity: 1; transform: scale(1); } to { opacity: 0.2; transform: scale(0.8); } }
    .title-gold { color: #D4AF37; font-size: 26px; font-weight: 900; text-align: center; margin: 5px 0; }
    .header-grid { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; background: #080808; padding: 10px 0; }
    .h-col { font-size: 9px; color: #FFF; text-align: center; font-weight: bold; }
    .row-container { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; align-items: center; padding: 12px 0; border-bottom: 1px solid #222; }
    .w-col { text-align: center; font-family: monospace; font-size: 15px; font-weight: bold; color: #FFF; }
    .vision-block { display: flex; justify-content: center; gap: 30px; padding: 5px 0; background: #050505; border-bottom: 2px solid #333; }
    div.stButton > button { background-color: #D4AF37; color: black; font-weight: bold; width: 100%; border-radius: 5px; border: none; }
    .stApp { background-color: #000000; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

def verificar_acesso():
    # Conexão com o Google Sheets via Secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
    CHAVE_MESTRA_ADM = "SHARK_ADM_2026" 
    
    if "autenticado" not in st.session_state:
        st.markdown("<h1 style='text-align:center; color:#D4AF37; font-family:monospace;'>SHAKE VISION LOGIN</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            chave = st.text_input("", type="password", placeholder="Digite a Chave...")
            btn = st.button("ACESSAR TERMINAL CRYPTO")
        
        if btn and chave:
            if chave == CHAVE_MESTRA_ADM:
                st.session_state.update({"autenticado": True, "usuario": "ADMINISTRADOR", "role": "admin", "session_id": "MASTER"})
                st.rerun()
            
            try:
                # Lendo a base de clientes
                df = conn.read(ttl=0)
                hash_t = hashlib.sha256(chave.encode()).hexdigest()
                df.columns = df.columns.str.strip()
                
                # Busca o usuário ativo
                idx_list = df.index[(df['HASH_SENHA'].astype(str).str.strip() == hash_t) & (df['STATUS'].str.strip() == 'ATIVO')].tolist()
                
                if idx_list:
                    row_idx = idx_list[0]
                    # CORREÇÃO DA LINHA 68: Adicionado os colchetes []
                    novo_id = str(uuid.uuid4())[:8]
                    
                    # Grava o novo ID de sessão na coluna E (SESSAO)
                    conn.update(data=[[novo_id]], range=f"E{row_idx + 2}")
                    
                    st.session_state.update({
                        "autenticado": True, 
                        "usuario": df.loc[row_idx, 'CLIENTE'],
                        "session_id": novo_id, 
                        "role": "user"
                    })
                    st.rerun()
                else:
                    st.error("❌ Chave Inválida ou Expirada.")
            except Exception as e:
                st.error(f"Erro ao conectar: {e}")
        st.stop()

verificar_acesso()

# CONFIGURAÇÕES DE MOEDAS
COINS_CONFIG = {
    "BTC-USD": {"label": "BTC/USDT", "dec": 0}, "ETH-USD": {"label": "ETH/USDT", "dec": 0},
    "SOL-USD": {"label": "SOL/USDT", "dec": 2}, "XRP-USD": {"label": "XRP/USDT", "dec": 4},
    "BNB-USD": {"label": "BNB/USDT", "dec": 2}, "DOGE-USD": {"label": "DOGE/USDT", "dec": 4},
    "LINK-USD": {"label": "LINK/USDT", "dec": 2}, "ADA-USD": {"label": "ADA/USDT", "dec": 4}
}

def get_alpha_midpoint(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False)
        return (data['High'].max() + data['Low'].min()) / 2
    except: return 0

# Inicialização de preços âncora
for t in COINS_CONFIG:
    if f'mp_{t}' not in st.session_state:
        val = get_alpha_midpoint(t)
        st.session_state[f'rv_{t}'] = val
        st.session_state[f'mp_{t}'] = val

placeholder = st.empty()

# LOOP DE ATUALIZAÇÃO COM TRAVA DE SESSÃO
while True:
    try:
        # VERIFICAÇÃO DE DISPOSITIVO DUPLICADO
        if st.session_state.get("role") == "user":
            conn = st.connection("gsheets", type=GSheetsConnection)
            check_df = conn.read(ttl=0)
            check_df.columns = check_df.columns.str.strip()
            user_row = check_df[check_df['CLIENTE'] == st.session_state['usuario']]
            
            if not user_row.empty:
                id_atual = str(user_row.iloc[0]['SESSAO']).strip()
                if id_atual != st.session_state["session_id"]:
                    st.error("⚠️ ACESSO BLOQUEADO: Sua conta foi conectada em outro dispositivo.")
                    st.stop()

        # RENDERIZAÇÃO DO TERMINAL
        with placeholder.container():
            now = datetime.now(pytz.timezone('America/Sao_Paulo'))
            st.markdown(f"""
                <div class="top-header-fixed">
                    <div class="top-bar">
                        <div class="live-indicator"><span class="dot"></span> {st.session_state['usuario']} | ONLINE</div>
                        <div style="color:#888; font-family:monospace; font-size:11px;">BRASÍLIA: {now.strftime('%H:%M:%S')}</div>
                    </div>
                    <div class="title-gold">SHARK VISION TERMINAL</div>
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
                
                # Lógica simplificada de níveis (Exemplo)
                levels = [1.02, 1.015, 1.01, 1.005, 0.995, 0.99, 0.985, 0.98]
                vals = [mp * l for l in levels]

                st.markdown(f"""
                    <div class="row-container">
                        <div class="w-col" style="color:#D4AF37; font-size:13px;">{info['label']}</div>
                        <div class="w-col">{price:,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FF4444;">{vals[0]:,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFA500;">{vals[1]:,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFFF00;">{vals[2]:,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00CED1;">{vals[3]:,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00CED1;">{vals[4]:,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFFF00;">{vals[5]:,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFA500;">{vals[6]:,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00FF00;">{vals[7]:,.{info['dec']}f}</div>
                    </div>
                """, unsafe_allow_html=True)
        time.sleep(2)
    except Exception as e:
        time.sleep(5)
