import streamlit as st
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import hashlib
import uuid
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="NEXUS CRYPTO LIVE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
    .dot { 
        height: 12px; width: 12px; background-color: #00FF00; 
        border-radius: 50%; display: inline-block;
        box-shadow: 0 0 10px #00FF00; animation: pulse-glow 1s infinite alternate;
        margin-right: 8px;
    }
    @keyframes pulse-glow { from { opacity: 1; transform: scale(1); } to { opacity: 0.2; transform: scale(0.8); } }
    .title-gold { color: #D4AF37; font-size: 26px; font-weight: 900; text-align: center; margin: 5px 0; }
    .header-grid { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; background: #080808; padding: 10px 0; }
    .h-col { font-size: 9px; color: #FFF; text-align: center; font-weight: bold; }
    .row-container { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; align-items: center; padding: 12px 0; border-bottom: 1px solid #222; }
    .w-col { text-align: center; font-family: monospace; font-size: 15px; font-weight: bold; color: #FFF; }
    div.stButton > button { background-color: #D4AF37; color: black; font-weight: bold; width: 100%; border-radius: 5px; border: none; height: 45px; }
    .stApp { background-color: #000000; }
    .top-header-fixed { position: sticky; top: 0; background: #000000; z-index: 1000; border-bottom: 2px solid #D4AF37; }
    .top-bar { display: flex; justify-content: space-between; align-items: center; padding: 5px 20px; background: #050505; border-bottom: 1px solid #1a1a1a; }
    .clocks { display: flex; gap: 30px; color: #888; font-family: monospace; font-size: 11px; }
    .live-indicator { display: flex; align-items: center; gap: 8px; color: #FFF; font-size: 11px; font-weight: bold; }
    .subtitle-white { color: #FFFFFF; font-size: 12px; text-align: center; letter-spacing: 4px; text-transform: lowercase; margin-bottom: 5px; }
    .loading-container { text-align: center; color: #D4AF37; font-family: monospace; padding: 40px; border: 1px solid #333; border-radius: 10px; background: #050505; margin-top: 50px;}
    .blink { animation: blinker 1.5s linear infinite; font-weight: bold; }
    @keyframes blinker { 50% { opacity: 0; } }
    @keyframes blink-alert { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# 2. VERIFICAÇÃO DE ACESSO
def verificar_acesso():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        CHAVE_MESTRA_ADM = "SHARK_ADM_2026" 
        
        if "autenticado" not in st.session_state:
            placeholder_login = st.empty()
            with placeholder_login.container():
                st.markdown("<h1 style='text-align:center; color:#D4AF37; font-family:monospace; margin-top:50px;'>NEXUS CRYPTO LOGIN</h1>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1,2,1])
                with col2:
                    chave = st.text_input("", type="password", placeholder="Digite sua Chave...")
                    btn = st.button("ACESSAR TERMINAL CRYPTO")
            
            if btn and chave:
                placeholder_login.markdown("<div class='loading-container'><h2 class='blink'>AGUARDE...</h2><p style='color: #888;'>Conectando ao Terminal</p></div>", unsafe_allow_html=True)
                if chave == CHAVE_MESTRA_ADM:
                    st.session_state.update({"autenticado": True, "usuario": "ADMINISTRADOR", "role": "admin", "session_id": "MASTER"})
                    st.rerun()
                try:
                    df = conn.read(ttl=0)
                    df.columns = df.columns.str.strip().str.upper()
                    hash_t = hashlib.sha256(chave.encode()).hexdigest()
                    user_match = df[(df['HASH_SENHA'].astype(str).str.strip() == hash_t) & (df['STATUS'].str.strip() == 'ATIVO')]
                    if not user_match.empty:
                        data_limite = pd.to_datetime(user_match.iloc[0]['VALIDADE'], dayfirst=True).date()
                        hoje = datetime.now(pytz.timezone('America/Sao_Paulo')).date()
                        if hoje > data_limite:
                            placeholder_login.error(f"❌ ACESSO EXPIRADO EM {data_limite.strftime('%d/%m/%Y')}.")
                            st.stop()
                        row_idx = user_match.index[0]
                        novo_id = str(uuid.uuid4())[:8]
                        df.iloc[row_idx, df.columns.get_loc('SESSAO')] = novo_id
                        conn.update(data=df)
                        st.session_state.update({"autenticado": True, "usuario": user_match.iloc[0]['CLIENTE'], "session_id": novo_id, "role": "user", "last_api_check": time.time()})
                        st.rerun()
                    else:
                        placeholder_login.error("❌ Chave Inválida ou Inativa.")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")
                    time.sleep(2)
            st.stop()
    except Exception as e:
        st.error(f"Falha crítica no terminal: {e}")
        st.stop()

verificar_acesso()

# 3. LÓGICA DE CÁLCULO
def get_calculation_date():
    br_tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(br_tz)
    if now.weekday() == 5: return now - timedelta(days=1)
    if now.weekday() == 6: return now - timedelta(days=2)
    if now.weekday() == 0 and now.hour < 18: return now - timedelta(days=3)
    if now.hour < 18: return now - timedelta(days=1)
    return now

def get_alpha_midpoint(ticker):
    try:
        br_tz = pytz.timezone('America/Sao_Paulo')
        target_date = get_calculation_date()
        df = yf.download(ticker, start=target_date.strftime('%Y-%m-%d'), interval="1m", progress=False)
        if df.empty: return yf.Ticker(ticker).fast_info['last_price']
        df.index = df.index.tz_convert(br_tz)
        df_window = df.between_time('11:30', '18:00')
        if not df_window.empty:
            return (float(df_window['High'].max()) + float(df_window['Low'].min())) / 2
        return yf.Ticker(ticker).fast_info['last_price']
    except Exception: return 0

COINS_CONFIG = {
    "BTC-USD": {"label": "BTC/USDT", "dec": 0}, "ETH-USD": {"label": "ETH/USDT", "dec": 0},
    "SOL-USD": {"label": "SOL/USDT", "dec": 3}, "XRP-USD": {"label": "XRP/USDT", "dec": 3},
    "BNB-USD": {"label": "BNB/USDT", "dec": 3}, "DOGE-USD": {"label": "DOGE/USDT", "dec": 3},
    "LINK-USD": {"label": "LINK/USDT", "dec": 3}, "ADA-USD": {"label": "ADA/USDT", "dec": 3},
    "AVAX-USD": {"label": "AVAX/USDT", "dec": 3}, "DOT-USD": {"label": "DOT/USDT", "dec": 3},
    "MATIC-USD": {"label": "MATIC/USDT", "dec": 3}, "PEPE-USD": {"label": "PEPE/USDT", "dec": 3},
    "SUI-USD": {"label": "SUI/USDT", "dec": 3}, "NEAR-USD": {"label": "NEAR/USDT", "dec": 3},
    "APT-USD": {"label": "APT/USDT", "dec": 3}, "OP-USD": {"label": "OP/USDT", "dec": 3},
    "ARB-USD": {"label": "ARB/USDT", "dec": 3}, "INJ-USD": {"label": "INJ/USDT", "dec": 3},
    "RNDR-USD": {"label": "RNDR/USDT", "dec": 3}, "HYPE-USD": {"label": "HYPE/USDT", "dec": 2}
}

for t in COINS_CONFIG:
    if f'rv_{t}' not in st.session_state:
        val = get_alpha_midpoint(t)
        st.session_state[f'rv_{t}'] = val
        st.session_state[f'mp_{t}'] = val

placeholder = st.empty()

# 4. LOOP DE ATUALIZAÇÃO
while True:
    try:
        if st.session_state.get("role") == "user":
            if time.time() - st.session_state.get("last_api_check", 0) > 15:
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    check_df = conn.read(ttl=0)
                    check_df.columns = check_df.columns.str.strip().str.upper()
                    user_row = check_df[check_df['CLIENTE'] == st.session_state['usuario']]
                    if not user_row.empty and str(user_row.iloc[0]['SESSAO']).strip() != st.session_state["session_id"]:
                        st.session_state.clear()
                        st.rerun()
                    st.session_state["last_api_check"] = time.time()
                except Exception: pass

        tz_br, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
        now_br = datetime.now(tz_br)

        with placeholder.container():
            st.markdown(f"""
                <div class="top-header-fixed">
                    <div class="top-bar">
                        <div class="live-indicator"><span class="dot"></span> {st.session_state['usuario']} | ONLINE</div>
                        <div class="clocks">
                            <div class="clock-item">BRASÍLIA: <b>{now_br.strftime('%H:%M:%S')}</b></div>
                            <div class="clock-item">NEW YORK: <b>{datetime.now(tz_ny).strftime('%H:%M:%S')}</b></div>
                            <div class="clock-item">LONDON: <b>{datetime.now(tz_ld).strftime('%H:%M:%S')}</b></div>
                        </div>
                    </div>
                    <div class="title-gold">TERMINAL NEXUS CRYPTO</div>
                    <div class="subtitle-white">visão de tubarão</div>
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
                mp, rv = st.session_state[f'mp_{t}'], st.session_state[f'rv_{t}']
                
                g_ex, g_top, g_dec, g_res = (1.0122, 1.0082, 1.0061, 1.0040) if t in ["BTC-USD", "ETH-USD"] else (1.0244, 1.0164, 1.0122, 1.0080)
                trigger = 1.22 if t in ["BTC-USD", "ETH-USD"] else 2.44
                
                var_escada = ((price / mp) - 1) * 100
                if var_escada >= trigger: st.session_state[f'mp_{t}'] = mp * g_ex
                elif var_escada <= -trigger: st.session_state[f'mp_{t}'] = mp * (2 - g_ex)
                
                var_reset = ((price / rv) - 1) * 100
                cor_v, seta_v = ("#00FF00", "▲") if var_reset >= 0 else ("#FF4444", "▼")
                blink_t = "animation: blink-alert 0.4s infinite;" if (var_escada >= trigger*0.9) else ""
                blink_f = "animation: blink-alert 0.4s infinite;" if (var_escada <= -trigger*0.9) else ""

                st.markdown(f"""
                    <div class="row-container">
                        <div class="w-col" style="color:#D4AF37; font-size:13px;">{info['label']}</div>
                        <div class="w-col">
                            <div style="font-size:14px;">{price:,.{info['dec']}f}</div>
                            <div style="color:{cor_v}; font-size:9px;">{seta_v} {var_reset:+.2f}%</div>
                        </div>
                        <div class="w-col" style="color:#FF4444; {blink_t}">{(mp * g_ex):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFA500;">{(mp * g_top):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFFF00;">{(mp * g_dec):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00CED1;">{(mp * g_res):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00CED1;">{(mp * (2-g_res)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFFF00;">{(mp * (2-g_dec)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#FFA500;">{(mp * (2-g_top)):,.{info['dec']}f}</div>
                        <div class="w-col" style="color:#00FF00; {blink_f}">{(mp * (2-g_ex)):,.{info['dec']}f}</div>
                    </div>
                    <div style="display: flex; justify-content: center; gap: 30px; padding: 5px 0; background: #050505; border-bottom: 2px solid #333;">
                        <div style="color:#666; font-size:9px;">RESET: <b style="color:#BBB;">{rv:,.{info['dec']}f}</b></div>
                        <div style="color:#666; font-size:9px;">ÂNCORAVISION: <b style="color:#00e6ff;">{mp:,.{info['dec']}f}</b></div>
                    </div>
                """, unsafe_allow_html=True)
        time.sleep(1)
    except Exception as e:
        time.sleep(5)
