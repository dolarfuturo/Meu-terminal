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

    except: return 0


st.markdown("""

    <style>

    .stApp { background-color: #000000; }

    .top-header-fixed { position: sticky; top: 0; background: #000000; z-index: 1000; border-bottom: 2px solid #D4AF37; }

    .top-bar { display: flex; justify-content: space-between; align-items: center; padding: 5px 20px; background: #050505; border-bottom: 1px solid #1a1a1a; }

    .clocks { display: flex; gap: 30px; color: #888; font-family: monospace; font-size: 11px; }

    .live-indicator { display: flex; align-items: center; gap: 8px; color: #FFF; font-size: 11px; font-weight: bold; }

    .dot { height: 8px; width: 8px; background-color: #00FF00; border-radius: 50%; animation: pulse 1.5s infinite; }

    @keyframes pulse { 0% { transform: scale(0.9); opacity: 1; } 70% { transform: scale(1); opacity: 0.6; } 100% { transform: scale(0.9); opacity: 1; } }

    .title-gold { color: #D4AF37; font-size: 24px; font-weight: 900; text-align: center; margin-top: 5px; }

    .subtitle-white { color: #FFFFFF; font-size: 12px; text-align: center; letter-spacing: 4px; text-transform: lowercase; margin-bottom: 5px; }

    .header-grid { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; width: 100%; padding: 10px 0; background: #080808; }

    .h-col { font-size: 9px; color: #FFF; text-align: center; font-weight: 800; }

    .row-container { display: grid; grid-template-columns: 1.2fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr; width: 100%; align-items: center; padding: 10px 0; }

    .w-col { text-align: center; font-family: 'monospace'; font-size: 15px; font-weight: 800; color: #FFF; }

    .vision-block { display: flex; justify-content: center; gap: 40px; padding: 5px 0; border-bottom: 2px solid #333; }

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

        tz_br, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')

        now_br, now_ny, now_ld = datetime.now(tz_br), datetime.now(tz_ny), datetime.now(tz_ld)


        with placeholder.container():

            st.markdown(f"""

                <div class="top-header-fixed">

                    <div class="top-bar">

                        <div class="live-indicator"><span class="dot"></span> {st.session_state['usuario']} |  ONLINE</div>

                        <div class="clocks">

                            <div class="clock-item">BRASÍLIA: <b>{now_br.strftime('%H:%M:%S')}</b></div>

                            <div class="clock-item">NEW YORK: <b>{now_ny.strftime('%H:%M:%S')}</b></div>

                            <div class="clock-item">LONDON: <b>{now_ld.strftime('%H:%M:%S')}</b></div>

                        </div>

                    </div>

                    <div class="title-gold">SHARK VISION CRYPTO</div>

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

                

                if t in ["BTC-USD", "ETH-USD"]:

                    g_ex, g_top, g_dec, g_res = 1.0122, 1.0082, 1.0061, 1.0040

                    label_regua = "1.22%"

                    trigger = 1.22

                else:

                    g_ex, g_top, g_dec, g_res = 1.0244, 1.0164, 1.0122, 1.0080

                    label_regua = "2.44%"

                    trigger = 2.44

                

                var_escada = ((price / mp) - 1) * 100

                if var_escada >= trigger: st.session_state[f'mp_{t}'] = mp * g_ex

                elif var_escada <= -trigger: st.session_state[f'mp_{t}'] = mp * (2 - g_ex)

                

                var_reset = ((price / rv) - 1) * 100

                cor_v, seta_v = ("#00FF00", "▲") if var_reset >= 0 else ("#FF4444", "▼")

                blink_t = "animation: blink 0.4s infinite;" if (var_escada >= trigger*0.9) else ""

                blink_f = "animation: blink 0.4s infinite;" if (var_escada <= -trigger*0.9) else ""


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

                    <div class="vision-block">

                        <div style="color:#666; font-size:9px;">RESET: <b style="color:#BBB;">{rv:,.{info['dec']}f}</b></div>

                        <div style="color:#666; font-size:9px;">ÂNCOVISION ({label_regua}): <b style="color:#00e6ff;">{mp:,.{info['dec']}f}</b></div>

                    </div>

                """, unsafe_allow_html=True)

        time.sleep(1)

    except Exception as e:

        time.sleep(5)




