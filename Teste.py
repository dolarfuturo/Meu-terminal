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
                valido = df[(df['HASH_SENHA'] == hash_tentativa) & (df['STATUS'] == 'ATIVO')]
                if not valido.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = valido.iloc[0]['CLIENTE']
                    st.rerun()
                else: st.error("❌ Acesso Negado.")
            except: st.error("Erro de conexão.")
        st.stop()

verificar_acesso()

COINS_CONFIG = {
    "BTC-USD": {"label": "BTC/USDT", "dec": 0}, "ETH-USD": {"label": "ETH/USDT", "dec": 0},
    "SOL-USD": {"label": "SOL/USDT", "dec": 2}, "XRP-USD": {"label": "XRP/USDT", "dec": 2},
    "BNB-USD": {"label": "BNB/USDT", "dec": 4}, "DOGE-USD": {"label": "DOGE/USDT", "dec": 4},
    "LINK-USD": {"label": "LINK/USDT", "dec": 4}, "ADA-USD": {"label": "ADA/USDT", "dec": 2},
    "AVAX-USD": {"label": "AVAX/USDT", "dec": 2}, "DOT-USD": {"label": "DOT/USDT", "dec": 2},
    "MATIC-USD": {"label": "MATIC/USDT", "dec": 4}, "PEPE-USD": {"label": "PEPE/USDT", "dec": 4},
    "SUI-USD": {"label": "SUI/USDT", "dec": 2}, "NEAR-USD": {"label": "NEAR/USDT", "dec": 2},
    "APT-USD": {"label": "APT/USDT", "dec": 6}, "OP-USD": {"label": "OP/USDT", "dec": 3},
    "ARB-USD": {"label": "ARB/USDT", "dec": 2}, "INJ-USD": {"label": "INJ/USDT", "dec": 2},
    "RNDR-USD": {"label": "RNDR/USDT", "dec": 3}, "HYPE-USD": {"label": "HYPE/USDT", "dec": 4}
}

def get_alpha_midpoint(ticker):
    try: return yf.Ticker(ticker).fast_info['last_price']
    except: return 0

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .top-header-fixed { position: sticky; top: 0; background: #000000; z-index: 1000; border-bottom: 2px solid #D4AF37; }
    .top-bar { display: flex; justify-content: space-between; align-items: center; padding: 5px 20px; background: #050505; }
    .clocks { display: flex; gap: 30px; color: #888; font-family: monospace; font-size: 12px; }
    .title-gold { color: #D4AF37; font-size: 28px; font-weight: 900; text-align: center; }
    .header-grid { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; width: 100%; padding: 10px 0; background: #080808; }
    .h-col { font-size: 9px; color: #FFF; text-align: center; font-weight: 800; }
    .row-container { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; width: 100%; align-items: center; padding: 10px 0; }
    .w-col { text-align: center; font-family: 'monospace'; font-size: 15px; font-weight: 800; color: #FFF; }
    .vision-block { display: flex; justify-content: center; gap: 60px; padding: 5px 0 15px 0; border-bottom: 2px solid #333; }
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
            tz_br = pytz.timezone('America/Sao_Paulo')
            now_br = datetime.now(tz_br)

            st.markdown(f"""
                <div class="top-header-fixed">
                    <div class="top-bar">
                        <div style="color:white; font-size:12px;">{st.session_state['usuario']} | ONLINE</div>
                        <div class="clocks"><div>BRASÍLIA: <b>{now_br.strftime('%H:%M:%S')}</b></div></div>
                    </div>
                    <div class="title-gold">SHARK VISION CRYPTO</div>
                    <div class="header-grid">
                        <div class="h-col">CÓDIGO</div><div class="h-col">PREÇO</div>
                        <div class="h-col" style="color:#FF4444;">EXAUST. T</div><div class="h-col" style="color:#FF8C00;">TOPO</div>
                        <div class="h-col" style="color:#FFA500;">DECISÃO</div><div class="h-col" style="color:#FFFF00;">RESPIRO</div>
                        <div class="h-col" style="color:#00CED1;">RESP. F</div><div class="h-col" style="color:#20B2AA;">DECIS. F</div>
                        <div class="h-col" style="color:#3CB371;">FUNDO</div><div class="h-col" style="color:#00FF00;">EXAUST. F</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            for t, info in COINS_CONFIG.items():
                price = yf.Ticker(t).fast_info['last_price']
                mp, rv = st.session_state[f'mp_{t}'], st.session_state[f'rv_{t}']
                
                # PARÂMETROS TÉCNICOS K97 - GRADE COMPLETA
                if t in ["BTC-USD", "ETH-USD"]:
                    # 1.22 (Ex) | 0.82 (Topo) | 0.61 (Dec) | 0.40 (Res)
                    m_ex, m_top, m_dec, m_res = 1.0122, 1.0082, 1.0061, 1.0040
                    g_trigger = 1.22
                else:
                    # Alts (Dobro): 2.44 | 1.64 | 1.22 | 0.80
                    m_ex, m_top, m_dec, m_res = 1.0244, 1.0164, 1.0122, 1.0080
                    g_trigger = 2.44

                var_escada = ((price / mp) - 1) * 100
                if var_escada >= g_trigger: st.session_state[f'mp_{t}'] = mp * m_ex
                elif var_escada <= -g_trigger: st.session_state[f'mp_{t}'] = mp * (2 - m_ex)
                
                var_reset = ((price / rv) - 1) * 100
                cor_v = "#00FF00" if var_reset >= 0 else "#FF4444"
                blink_t = "animation: blink 0.4s infinite;" if (var_escada >= (g_trigger * 0.9)) else ""
                blink_f = "animation: blink 0.4s infinite;" if (var_escada <= -(g_trigger * 0.9)) else ""

                st.markdown(f"""
                    <div class="row-container">
                        <div class="w-col" style="color:#D4AF37; font-size:13px;">{info['label']}</div>
                        <div class="w-col">
                            <div style="font-size:14px;">{price:,.{info['dec']}f}</div>
                            <div style="color:{cor_v}; font-size:9px;">{var_reset:+.2f}%</div>
                        </div>
                        <div class="w-col" style="color:#FF4444; {blink_t}">{(mp * m_ex):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FF8C00;">{(mp * m_top):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFA500;">{(mp * m_dec):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFFF00;">{(mp * m_res):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00CED1;">{(mp * (2-m_res)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#20B2AA;">{(mp * (2-m_dec)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#3CB371;">{(mp * (2-m_top)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00FF00; {blink_f}">{(mp * (2-m_ex)):,.{info['dec']}f}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Rodapé Vision
            st.markdown(f"""
                <div class="vision-block">
                    <div style="color:#BBB; font-size:12px;">STATUS: <b>PROCESSANDO FLUXO K97</b></div>
                    <div style="color:#00e6ff; font-size:12px;">ESTRATÉGIA: <b>AMORTIZAÇÃO RECORRENTE (R$ 125)</b></div>
                </div>
            """, unsafe_allow_html=True)
            
        time.sleep(1)
    except: time.sleep(2)
