import streamlit as st
import pandas as pd
import time  

# 1. SETUP DO TERMINAL K97
st.set_page_config(page_title="ALPHA VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

def verificar_acesso():
    # LINK EXTRAÍDO DA SUA IMAGEM 1000030168.png
    URL_SISTEMA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGR5bx-l2wuOzwfOdQK10D42lB-oG2zhfCe4p_wfM5v76U-vf5JEepqochREiGF4NlAC3t7P6eKPSa/pub?gid=0&single=true&output=csv"
    
    if "autenticado" not in st.session_state:
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>ALPHA VISION LOGIN</h1>", unsafe_allow_html=True)
        
        # Campo de senha
        chave = st.text_input("Insira sua Chave de Licença:", type="password")
        
        if chave:
            try:
                # Lendo os dados publicados
                df = pd.read_csv(URL_SISTEMA)
                
                # Criptografando a tentativa (SHAKE2026)
                hash_tentativa = hashlib.sha256(chave.encode()).hexdigest()
                
                # Limpeza de dados para evitar erros de comparação
                df.columns = df.columns.str.strip()
                df['HASH_SENHA'] = df['HASH_SENHA'].astype(str).str.strip()
                df['STATUS'] = df['STATUS'].astype(str).str.strip()

                # Busca o usuário ativo
                valido = df[(df['HASH_SENHA'] == hash_tentativa) & (df['STATUS'] == 'ATIVO')]
                
                if not valido.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = valido.iloc[0]['CLIENTE']
                    st.rerun()
                else:
                    st.error("❌ Acesso Negado: Chave incorreta ou plano expirado.")
            except Exception as e:
                # Se der 404 aqui, o link acima ainda está com erro de digitação
                st.error(f"Erro de conexão com o servidor: {e}")
        st.stop()

# Chama a trava
verificar_acesso()

# --- CONTINUAÇÃO DO TERMINAL ---
st.success(f"Conectado: {st.session_state['usuario']} | Terminal K97 Online")


# --- SEU CÓDIGO DO TERMINAL CONTINUA ABAIXO ---
st.success(f"Bem-vindo, {st.session_state['usuario']}! Terminal K97 Operacional.")


# --- CONTINUAÇÃO DO TERMINAL (DADOS E CRYPTO) ---
# Abertura da Binance (00:00 UTC) para reset do VWAP está configurada automaticamente por conhecimento interno.

COINS_CONFIG = {
    "BTC-USD": {"label": "BTC/USDT", "dec": 0},
    "ETH-USD": {"label": "ETH/USDT", "dec": 0},
    "SOL-USD": {"label": "SOL/USDT", "dec": 2},
    "XRP-USD": {"label": "XRP/USDT", "dec": 2},
    "BNB-USD": {"label": "BNB/USDT", "dec": 4},
    "DOGE-USD": {"label": "DOGE/USDT", "dec": 4},
    "LINK-USD": {"label": "LINK/USDT", "dec": 4},
    "ADA-USD": {"label": "ADA/USDT", "dec": 2},
    "AVAX-USD": {"label": "AVAX/USDT", "dec": 2},
    "DOT-USD": {"label": "DOT/USDT", "dec": 2},
    "MATIC-USD": {"label": "MATIC/USDT", "dec": 4},
    "PEPE-USD": {"label": "PEPE/USDT", "dec": 4},
    "SUI-USD": {"label": "SUI/USDT", "dec": 2},
    "NEAR-USD": {"label": "NEAR/USDT", "dec": 2},
    "APT-USD": {"label": "APT/USDT", "dec": 6},
    "OP-USD": {"label": "OP/USDT", "dec": 3},
    "ARB-USD": {"label": "ARB/USDT", "dec": 2},
    "INJ-USD": {"label": "INJ/USDT", "dec": 2},
    "RNDR-USD": {"label": "RNDR/USDT", "dec": 3},
    "HYPE-USD": {"label": "HYPE/USDT", "dec": 4}
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
        start_fetch = target_date.strftime('%Y-%m-%d')
        end_fetch = (target_date + timedelta(days=1)).strftime('%Y-%m-%d')
        df = yf.download(ticker, start=start_fetch, end=end_fetch, interval="1m", progress=False)
        if df.empty: return yf.Ticker(ticker).fast_info['last_price']
        df.index = df.index.tz_convert(br_tz)
        df_window = df.between_time('11:30', '18:00')
        if not df_window.empty:
            return (float(df_window['High'].max()) + float(df_window['Low'].min())) / 2
        return yf.Ticker(ticker).fast_info['last_price']
    except: return 0

# CSS AVANÇADO PARA TRAVAMENTO REAL
st.markdown("""
    <style>
    /* Reset de overflow para permitir o sticky */
    .stApp { background-color: #000000; }
    [data-testid="stVerticalBlock"] > div:first-child {
        position: sticky;
        top: 0;
        z-index: 1000;
        background-color: #000000;
    }
    
    .top-header-fixed {
        position: sticky;
        top: 0;
        background: #000000;
        z-index: 1000;
        border-bottom: 2px solid #D4AF37;
    }

    .top-bar { display: flex; justify-content: space-between; align-items: center; padding: 5px 20px; background: #050505; border-bottom: 1px solid #1a1a1a; }
    .clocks { display: flex; gap: 30px; color: #888; font-family: monospace; font-size: 12px; }
    .clock-item b { color: #FFF; }
    .live-indicator { display: flex; align-items: center; gap: 8px; color: #FFF; font-size: 12px; font-weight: bold; }
    .dot { height: 8px; width: 8px; background-color: #00FF00; border-radius: 50%; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { transform: scale(0.9); opacity: 1; box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); } 70% { transform: scale(1); opacity: 0.6; box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); } 100% { transform: scale(0.9); opacity: 1; } }
    
    .title-gold { color: #D4AF37; font-size: 28px; font-weight: 900; text-align: center; margin-top: 5px; }
    .subtitle-white { color: #FFFFFF; font-size: 12px; text-align: center; letter-spacing: 4px; text-transform: lowercase; margin-bottom: 5px; }
    
    .header-grid { display: grid; grid-template-columns: 1.5fr 1.2fr 1fr 1fr 1fr 1fr 1fr 1fr; width: 100%; padding: 10px 0; background: #080808; }
    .h-col { font-size: 10px; color: #FFF; text-align: center; font-weight: 800; }
    
    .row-container { display: grid; grid-template-columns: 1.5fr 1.2fr 1fr 1fr 1fr 1fr 1fr 1fr; width: 100%; align-items: center; padding: 12px 0 2px 0; }
    .w-col { text-align: center; font-family: 'monospace'; font-size: 17px; font-weight: 800; color: #FFF; }
    .vision-block { display: flex; justify-content: center; gap: 60px; padding: 2px 0 12px 0; border-bottom: 3px solid #333; margin-bottom: 2px; }
    
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
            # CABEÇALHO TRAVADO (SÓ APARECE UMA VEZ NO TOPO DO CONTAINER)
            st.markdown(f"""
                <div class="top-header-fixed">
                    <div class="top-bar">
                        <div class="live-indicator"><span class="dot"></span> LIVESTREAM</div>
                        <div class="clocks">
                            <div class="clock-item">BRASÍLIA: <b>{now_br.strftime('%H:%M:%S')}</b></div>
                            <div class="clock-item">NEW YORK: <b>{now_ny.strftime('%H:%M:%S')}</b></div>
                            <div class="clock-item">LONDON: <b>{now_ld.strftime('%H:%M:%S')}</b></div>
                        </div>
                    </div>
                    <div class="title-gold">ALPHA VISION CRYPTO</div>
                    <div class="subtitle-white">visão de tubarão</div>
                    <div class="header-grid">
                        <div class="h-col">CÓDIGO</div><div class="h-col">PREÇO ATUAL</div>
                        <div class="h-col" style="color:#FF4444;">EXAUSTÃO T.</div><div class="h-col">PRÓX. TOPO</div>
                        <div class="h-col" style="color:#FFFF00;">DECISÃO</div><div class="h-col">RESPIRO</div>
                        <div class="h-col">PRÓX. AO F.</div><div class="h-col" style="color:#00FF00;">EXAUSTÃO F.</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            for t, info in COINS_CONFIG.items():
                price = yf.Ticker(t).fast_info['last_price']
                mp, rv = st.session_state[f'mp_{t}'], st.session_state[f'rv_{t}']
                
                if t in ["BTC-USD", "ETH-USD"]: g_ex, g_mov, g_dec, g_res, label_regua = 1.35, 1.0122, 1.0061, 1.0040, "1.22%"
                else: g_ex, g_mov, g_dec, g_res, label_regua = 1.0270, 1.244, 1.0122, 1.0080, "2.44%"
                
                var_escada = ((price / mp) - 1) * 100
                if var_escada >= g_ex: st.session_state[f'mp_{t}'] = mp * g_mov
                elif var_escada <= -g_ex: st.session_state[f'mp_{t}'] = mp * (2 - g_mov)
                
                var_reset = ((price / rv) - 1) * 100
                cor_v, seta_v = ("#00FF00", "▲") if var_reset >= 0 else ("#FF4444", "▼")
                abs_v = abs(var_escada)
                fundo_d = "background: rgba(255, 255, 0, 0.15);" if (g_ex*0.44 <= abs_v <= g_ex*0.48) else ""
                blink_t = "animation: blink 0.4s infinite;" if (g_ex*0.88 <= var_escada < g_ex) else ""
                blink_f = "animation: blink 0.4s infinite;" if (-g_ex < var_escada <= -g_ex*0.88) else ""

                st.markdown(f"""
                    <div class="row-container">
                        <div class="w-col" style="color:#D4AF37;">{info['label']}</div>
                        <div class="w-col">
                            <div style="font-weight: bold;">{f"{price:,.{info['dec']}f}"}</div>
                            <div style="color:{cor_v}; font-size:10px;">{seta_v} {var_reset:+.2f}%</div>
                        </div>
                        <div class="w-col" style="color:#FF4444; {blink_t}">{f"{(mp * (1 + (g_ex/100))):,.{info['dec']}f}"}</div>
                        <div class="w-col" style="color:#FFA500;">{f"{(mp * g_mov):,.{info['dec']}f}"}</div>
                        <div class="w-col" style="{fundo_d} color:#FFFF00;">{f"{(mp * g_dec):,.{info['dec']}f}"}</div>
                        <div class="w-col" style="color:#00CED1;">{f"{(mp * g_res):,.{info['dec']}f}"}</div>
                        <div class="w-col" style="color:#FFA500;">{f"{(mp * (2 - g_mov)):,.{info['dec']}f}"}</div>
                        <div class="w-col" style="color:#00FF00; {blink_f}">{f"{(mp * (1 - (g_ex/100))):,.{info['dec']}f}"}</div>
                    </div>
                    <div class="vision-block">
                        <div class="v-item"><div style="color:#666; font-size:8px;">RESETVISION</div><div style="color:#BBB; font-size:14px; font-weight:bold;">{f"{rv:,.{info['dec']}f}"}</div></div>
                        <div class="v-item"><div style="color:#666; font-size:8px;">ÂNCOVISION ({label_regua})</div><div style="color:#00e6ff; font-size:14px; font-weight:bold;">{f"{mp:,.{info['dec']}f}"}</div></div>
                    </div>
                """, unsafe_allow_html=True)
        time.sleep(1)
    except: time.sleep(5)
