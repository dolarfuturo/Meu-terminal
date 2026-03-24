import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet K97
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO COMPACTA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; }
    .title-box { display: flex; align-items: center; gap: 8px; line-height: 1; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .sep-text { font-size: 46px; color: #ffffff; font-weight: 950; margin: 0 5px; }
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    
    /* ESTILO DA BARRA DE FORÇA BIDIRECIONAL */
    .bar-wrapper { background: #0a141a; padding: 15px 10px; border: 1px solid #444; border-radius: 8px; margin-top: 15px; }
    .force-container-dual { background: #111; height: 22px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1.5px solid #333; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; box-shadow: 0 0 5px #fff; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: linear-gradient(to left, #00ff88, #004422); float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: linear-gradient(to right, #ff4d4d, #880000); float: left; height: 100%; transition: width 0.4s; }
    
    .label-row { display: flex; justify-content: space-between; font-size: 10px; color: #888; margin-bottom: 5px; font-weight: bold; text-transform: uppercase; }
    .sinal-indicator { font-size: 38px; font-weight: 900; line-height: 1; margin-top: 10px; text-align: center; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }

    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; margin-bottom: 2px; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        ref_close = t.info.get('previousClose')
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1]*m, "cl": (ref_close or d['Open'].iloc[0])*m, "op": d['Open'].iloc[0]*m, "mx": d['High'].max()*m, "mn": d['Low'].min()*m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

# --- LÓGICA DE CÁLCULO SHAKE VISION ---
def calcular_k97_v2(eixo_dol, spot_data, p50_baixa, p50_alta):
    try:
        # 1. CÁLCULO DA BARRA (EXAUSTÃO)
        # Unidade X = Distância do Eixo até a Média
        dist_x = abs(eixo_dol - p50_baixa)
        dist_atual = spot_data['at'] - eixo_dol
        
        pct_verde = 0
        pct_vermelho = 0
        
        if dist_atual < 0: # ABAIXO DO EIXO = BARRA VERDE (COMPRA)
            # 1X = 50% do lado verde | 2X = 100% do lado verde
            pct_verde = min(100, (abs(dist_atual) / (dist_x * 2)) * 100)
        else: # ACIMA DO EIXO = BARRA VERMELHA (VENDA)
            pct_vermelho = min(100, (abs(dist_atual) / (dist_x * 2)) * 100)

        # 2. CÁLCULO DA SETA (DIREÇÃO/FLUXO) - INDEPENDENTE
        # Ex: Seta verde se preço sobe em relação ao último minuto (simplificado para o exemplo)
        seta_txt, seta_cor = "•", "#444"
        if spot_data['at'] > spot_data['op']: seta_txt, seta_cor = "▲ COMPRA", "#00ff88"
        if spot_data['at'] < spot_data['op']: seta_txt, seta_cor = "▼ VENDA", "#ff4d4d"

        return {"pct_v": pct_verde, "pct_r": pct_vermelho, "seta": seta_txt, "seta_cor": seta_cor}
    except: return None

# --- UI HEADER E DADOS (RESUMIDO PARA O BLOCO) ---
a_dol = st.sidebar.number_input("AXIS DOLFUT:", value=5246.00)
spot_live = fetch("USDBRL=X")
# Valores de exemplo para 50% baseados na sua lógica de simetria
p50_b = a_dol - 40
p50_a = a_dol + 40

res_barra = calcular_k97_v2(a_dol, spot_live, p50_b, p50_a)

# --- DISPLAY DA BARRA NO TERMINAL ---
if res_barra:
    st.markdown(f"""
    <div class="bar-wrapper">
        <div class="label-row">
            <span style="color:#00ff88;">Exaustão</span>
            <span style="color:#ffa500;">Média</span>
            <span style="color:#fff;">AXIS</span>
            <span style="color:#ffa500;">Média</span>
            <span style="color:#ff4d4d;">Exaustão</span>
        </div>
        <div class="force-container-dual">
            <div class="center-line"></div>
            <div class="bar-side">
                <div class="fill-green" style="width: {res_barra['pct_v']}%;"></div>
            </div>
            <div class="bar-side">
                <div class="fill-red" style="width: {res_barra['pct_r']}%;"></div>
            </div>
        </div>
        <div class="sinal-indicator blink" style="color:{res_barra['seta_cor']};">
            {res_barra['seta']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ... (Restante do seu código de tabelas e ticker)
