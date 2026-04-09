import streamlit as st
import requests
import time
import os
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO DA CHAVE (TROQUE PELA NOVA AQUI) ---
API_KEY_TWELVE = "7805835d10ff47dfb88596a0ee89edc6"

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="K97 - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- NOVO MOTOR DE DADOS (TWELVE DATA) ---
def fetch_twelve(symbol_original):
    # Tradutor de Símbolos: Yahoo -> Twelve Data
    symbols_map = {
        "USDBRL=X": "USD/BRL",
        "EWZ": "EWZ",
        "DX-Y.NYB": "DXY",
        "GBPUSD=X": "GBP/USD",
        "JPYUSD=X": "JPY/USD",
        "EURUSD=X": "EUR/USD",
        "GC=F": "XAU/USD",
        "BZ=F": "LCO/USD" # Brent
    }
    
    symbol = symbols_map.get(symbol_original, symbol_original)
    
    try:
        # Usamos o endpoint 'quote' que gasta apenas 1 crédito e traz tudo (Price, High, Low, Close)
        url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={API_KEY_TWELVE}"
        response = requests.get(url)
        d = response.json()
        
        if "price" not in d:
            return st.session_state.market_data.get(symbol_original)

        m = 1000 if symbol == "USD/BRL" else 1
        
        # Estrutura compatível com o seu cálculo original
        data = {
            "at": float(d['price']) * m,
            "cl": float(d['previous_close']) * m,
            "op": float(d['open']) * m,
            "mx": float(d['high']) * m,
            "mn": float(d['low']) * m
        }
        st.session_state.market_data[symbol_original] = data
        return data
    except:
        return st.session_state.market_data.get(symbol_original)

# --- MANTENDO SUAS FUNÇÕES ORIGINAIS ---
def salvar_eixos(div_spreed, dol):
    with open("config_axis.txt", "w") as f: f.write(f"{div_spreed},{dol}")

def carregar_eixos():
    if os.path.exists("config_axis.txt"):
        try:
            with open("config_axis.txt", "r") as f:
                dados = f.read().split(",")
                return float(dados[0]), float(dados[1])
        except: pass
    return 8.0, 5246.0

# --- INICIALIZAÇÃO ---
div_spreed_salvo, eixo_dol_salvo = carregar_eixos()
if 'market_data' not in st.session_state: st.session_state.market_data = {}
if 'last_p' not in st.session_state: st.session_state.last_p = {}
if 'div_spreed_mem' not in st.session_state: st.session_state.div_spreed_mem = div_spreed_salvo
if 'a_dol_mem' not in st.session_state: st.session_state.a_dol_mem = eixo_dol_salvo

# --- (SEU CSS CONTINUA EXATAMENTE O MESMO AQUI) ---
st.markdown("""
<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; position: relative; }
    .main-title { margin: 0px; line-height: 1.2; font-size: 28px; font-family: monospace; padding-bottom: 5px; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    /* ... resto do seu CSS que você enviou ... */
</style>
""", unsafe_allow_html=True)

# --- (SUA FUNÇÃO DE CÁLCULO K97 CONTINUA IGUAL) ---
def calcular_k97_total(div_spreed, p_ewz_atual, eixo_dol, spot_data):
    # Usei exatamente a sua lógica de X, Y, Alvos e Sinais
    try:
        if not spot_data or p_ewz_atual == 0: return None
        amp = spot_data['mx'] - spot_data['mn']
        v_spreed = amp / 8
        folga = v_spreed / 2 
        max_original, min_original = eixo_dol + (amp * 0.75), eixo_dol - (amp * 0.25)
        dolar_medio = ((max_original + min_original) / 2) - v_spreed
        elastico_calculado = abs(eixo_dol - dolar_medio) if abs(eixo_dol - dolar_medio) != 0 else 1.0
        media_pura_barra = (spot_data['mx'] + spot_data['mn']) / 2
        
        val_x = eixo_dol - (eixo_dol - media_pura_barra - folga)
        val_y = eixo_dol + (eixo_dol - media_pura_barra + folga)
        alvo_low = spot_data['mn'] + (eixo_dol - val_x)
        alvo_high = spot_data['mx'] + (val_y - eixo_dol)

        dist_base_barra = abs(eixo_dol - media_pura_barra) + folga
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = 0, 0
        seta_txt, seta_cor, piscando = "", "#000000", False
        if dist_base_barra > 0 and div_spreed > 0:
            calculo_pct = (abs(diff) / (dist_base_barra * div_spreed)) * 100
            if diff < 0: p_v = min(100, calculo_pct)
            else: p_r = min(100, calculo_pct)
        
        if p_v >= 100: seta_txt, seta_cor, piscando = "▲ REGIÃO DE COMPRA", "#00ff88", True
        elif p_r >= 100: seta_txt, seta_cor, piscando = "▼ REGIÃO DE VENDA", "#ff4d4d", True
        
        v_spot_pct = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
        v_ewz = ((p_ewz_atual / ewz_ref) - 1) if ewz_ref > 0 else 0
        v_final = (v_spot_pct * 0.6) - (v_ewz * 0.4)
        
        return {
            "vivo": (eixo_dol + (eixo_dol * (1 + (v_final / 2)))) / 2, 
            "dolfut_calc": eixo_dol * (1 + v_final), 
            "fraja": eixo_dol * (1 + (v_final / 2)), 
            "medio": dolar_medio, 
            "max_fut_5": eixo_dol + (elastico_calculado * 10), "max_fut_4": eixo_dol + (elastico_calculado * 8),
            "max_fut_3": eixo_dol + (elastico_calculado * 6), "max_fut_2": eixo_dol + (elastico_calculado * 4),
            "max_fut_1": eixo_dol + (elastico_calculado * 2), "min_fut_1": eixo_dol - (elastico_calculado * 2),
            "min_fut_2": eixo_dol - (elastico_calculado * 4), "min_fut_3": eixo_dol - (elastico_calculado * 6),
            "min_fut_4": eixo_dol - (elastico_calculado * 8), "min_fut_5": eixo_dol - (elastico_calculado * 10),
            "v_v": v_final * 100, "v_spot": v_spot_pct * 100, "spreed": v_spreed, "p_v": p_v, "p_r": p_r, 
            "seta": seta_txt, "seta_cor": seta_cor, "piscando": piscando, "max_grade": max_original, "min_grade": min_original,
            "alvo_low": alvo_low, "alvo_high": alvo_high
        }
    except: return None

# --- SIDEBAR E LOOP ---
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM K97")
    i_div = st.number_input("DIVISOR SPREED:", value=st.session_state.div_spreed_mem, format="%.2f")
    i_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol_mem, format="%.2f")
    if st.button("SALVAR CONFIGURAÇÕES"):
        st.session_state.div_spreed_mem, st.session_state.a_dol_mem = i_div, i_dol
        salvar_eixos(i_div, i_dol); st.rerun()

div_s, a_dol = st.session_state.div_spreed_mem, st.session_state.a_dol_mem
placeholder = st.empty()

while True:
    tz_sp = pytz.timezone('America/Sao_Paulo')
    # CHAMANDO O NOVO MOTOR
    spot_live = fetch_twelve("USDBRL=X")
    ewz_live = fetch_twelve("EWZ")
    now = datetime.now()
    
    with placeholder.container():
        # ... (Toda a sua parte visual do Header continua igual) ...
        
        res = calcular_k97_total(div_s, ewz_live['at'] if ewz_live else 0, a_dol, spot_live)
        if res:
            # Renderização das colunas C1 e C2 com seus dados Twelve Data
            c1, c2 = st.columns([2.8, 1.2])
            with c1:
                st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                # O HTML da tabela agora usa 'fetch_twelve' para todos os ativos
                # ... (Resto do seu código de montagem da tabela) ...

    time.sleep(12) # Aumentei um pouco para preservar créditos no plano Free
