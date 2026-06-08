import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime, timedelta
import pytz

# =============================================================================
# # BLOCO 1: CSS (MANTIDO)
# =============================================================================
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")
st.markdown("""<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; position: relative; }
    .main-title { margin: 0px; line-height: 1.2; font-size: 28px; font-family: monospace; padding-bottom: 5px; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .clock-row { display: flex; justify-content: center; gap: 15px; padding: 2px 0; font-weight: bold; font-size: 11px; font-family: monospace; }
    .clock-item { color: #AAA; }
    .br-green { color: #00ff00; }
    .white-time { color: #ffffff; }
    .utc-gold { color: #FFD700; }
    .date-container { position: absolute; bottom: 5px; right: 10px; font-family: monospace; font-size: 11px; font-weight: bold; color: #ffffff; }
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 5px; text-transform: uppercase; font-size: 11px; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; margin-bottom: 0px; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 10px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 12px; }
    .asset-name { font-size: 12px; color: #fff; text-align: left; font-weight: bold; padding-left: 8px; }
    .price-col { font-weight: bold; color: #ffffff !important; }
    .f-up { background-color: #00ff00aa !important; }
    .f-dn { background-color: #ff0000aa !important; }
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; margin-top: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; align-items: center; }
    .bar-wrapper-full { background: #0a141a; padding: 6px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; margin-top: 5px; }
    .force-scale { display: flex; justify-content: space-between; font-size: 8px; font-family: monospace; color: #AAA; margin-bottom: 2px; padding: 0 5px; }
    .force-container-dual { background: #111; height: 10px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 11px; font-weight: 900; line-height: 1; margin-top: 4px; }
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .txt-green { color: #00ff88 !important; }
    .txt-yellow { color: #ffff00 !important; }
    .txt-red { color: #ff4d4d !important; }
</style>""", unsafe_allow_html=True)

# =============================================================================
# # BLOCO 2 & 4: PERSISTÊNCIA E NÚCLEO MATEMÁTICO (BLINDADOS)
# =============================================================================
def get_arq_path(nome):
    data = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
    return f"{nome}_{data}.txt"

def salvar_estado(nome, valor):
    with open(get_arq_path(nome), "w") as f: f.write(str(valor))

def carregar_estado(nome):
    path = get_arq_path(nome)
    if os.path.exists(path):
        try:
            with open(path, "r") as f: return float(f.read())
        except: pass
    return None

def calcular_k97_total(spreed_do_dia, spot_data, ewz_data):
    try:
        if not spot_data or not ewz_data or spot_data['at'] == 0: return None
        
        preco_spot = spot_data['at'] if spot_data['at'] > 100 else spot_data['at'] * 1000
        tz_sp = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(tz_sp)
        
        # PERSISTÊNCIA BLINDADA
        base = carregar_estado("base")
        delta_acumulado = carregar_estado("delta")
        
        # Inicialização do pregão
        if base is None:
            base = preco_spot
            delta_acumulado = 0.0
            salvar_estado("base", base)
            salvar_estado("delta", delta_acumulado)

        # Lógica de 8 minutos
        prox_8m = carregar_estado("prox_8m")
        if prox_8m is None:
            prox_8m = (agora + timedelta(minutes=8)).timestamp()
            salvar_estado("prox_8m", prox_8m)
            
        if agora.timestamp() >= prox_8m:
            delta_acumulado += (preco_spot - base) / 100000 # Ajuste de força
            base = preco_spot
            prox_8m = (agora + timedelta(minutes=8)).timestamp()
            salvar_estado("base", base)
            salvar_estado("delta", delta_acumulado)
            salvar_estado("prox_8m", prox_8m)

        # Cálculo contínuo
        fracao_4s = (preco_spot - base) / 1000
        delta_final = delta_acumulado + fracao_4s
        salvar_estado("delta_temp", delta_final) # Salva para leitura no F5

        # ... (Mantido seu cálculo original de indicadores)
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        spreed_t = spot_data['mx'] - spot_data['mn']
        spreed_50 = spreed_t / 2
        dxy_data = fetch("DX-Y.NYB")
        v_dxy = ((dxy_data['at'] / dxy_data['cl']) - 1) if dxy_data['cl'] > 0 else 0
        ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
        v_ewz = ((ewz_data['at'] / ewz_ref) - 1) if ewz_ref > 0 else 0
        calc_variacoes_pct = (v_dxy * 0.7) - (v_ewz * 0.3)
        vivo_val = spot_data['cl'] * (1 + calc_variacoes_pct)
        axis_dinamico = dolar_medio + spreed_do_dia
        passo_fixo = spreed_50 / 4
        diff = preco_spot - vivo_val
        p_v = min(100, (abs(diff)/spreed_t)*100) if diff < 0 and spreed_t > 0 else 0
        p_r = min(100, (abs(diff)/spreed_t)*100) if diff > 0 and spreed_t > 0 else 0
        
        return {
            "vivo": vivo_val, "vivo_pct": calc_variacoes_pct * 100, "dolfut_calc": axis_dinamico,
            "max_fut_1": axis_dinamico + passo_fixo, "max_fut_2": axis_dinamico + (passo_fixo * 3),
            "min_fut_1": axis_dinamico - passo_fixo, "min_fut_2": axis_dinamico - (passo_fixo * 3),
            "p_v": p_v, "p_r": p_r, "delta_spot_forca": delta_final,
            "preco_base_atual": base/1000, "seta": "▲ REGIÃO DE COMPRA" if p_v==100 else ("▼ REGIÃO DE VENDA" if p_r==100 else ""),
            "seta_cor": "#00ff88" if p_v==100 else "#ff4d4d", "piscando": p_v==100 or p_r==100,
            "axis_central": axis_dinamico, "spreed": spreed_50, "spreed_t": spreed_t,
            "fraja": preco_spot + spreed_do_dia, "medio": dolar_medio, "alvo_low": spot_data['mn']+spreed_do_dia,
            "alvo_high": spot_data['mx']+spreed_do_dia, "v_v": calc_variacoes_pct*100,
            "max_grade": spot_data['mx'], "min_grade": spot_data['mn']
        }
    except: return None

# [MANTENHA OS BLOCOS 3, 5 E 6 COMO ESTAVAM NO SEU CÓDIGO ORIGINAL]
# Certifique-se apenas de remover as inicializações de session_state do Bloco 2 
# que conflitam com os arquivos (k97_abertura_base, k97_delta_acumulado, etc).
