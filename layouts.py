import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime, timedelta
import pytz

# =============================================================================
# # BLOCO 1: CONFIGURAÇÃO DE AMBIENTE E ESTILIZAÇÃO VISUAL (CSS)
# =============================================================================
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    [data-testid="column"] { display: flex; flex-direction: column; justify-content: flex-start; gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { gap: 12px !important; margin-bottom: 0px !important; }
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
</style>
""", unsafe_allow_html=True)

# ... (Bloco 2 e 3 permanecem iguais) ...
def salvar_eixos(div_spreed):
    with open("config_axis.txt", "w") as f:
        f.write(f"{div_spreed}")

def carregar_eixos():
    if os.path.exists("config_axis.txt"):
        try:
            with open("config_axis.txt", "r") as f:
                return float(f.read().split(",")[0])
        except: pass
    return 8.0

def carregar_historico_dolfut_diario():
    data_hoje = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
    if os.path.exists("dolfut_history.txt"):
        try:
            with open("dolfut_history.txt", "r") as f:
                conteudo = f.read().split(",")
                if conteudo[0] == data_hoje:
                    return float(conteudo[1]), float(conteudo[2])
        except: pass
    return float('-inf'), float('inf')

def salvar_historico_dolfut_diario(mx, mn):
    data_hoje = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
    try:
        with open("dolfut_history.txt", "w") as f:
            f.write(f"{data_hoje},{mx},{mn}")
    except: pass

div_spreed_salvo = carregar_eixos()

if 'market_data' not in st.session_state: st.session_state.market_data = {}
if 'last_p' not in st.session_state: st.session_state.last_p = {}
if 'div_spreed_mem' not in st.session_state: st.session_state.div_spreed_mem = div_spreed_salvo

max_init, min_init = carregar_historico_dolfut_diario()
if 'dolfut_max_auto' not in st.session_state: st.session_state.dolfut_max_auto = max_init
if 'dolfut_min_auto' not in st.session_state: st.session_state.dolfut_min_auto = min_init

if 'last_spot_max' not in st.session_state: st.session_state.last_spot_max = 0.0
if 'last_spot_min' not in st.session_state: st.session_state.last_spot_min = float('inf')

if 'c_spot_fech_val' not in st.session_state: st.session_state.c_spot_fech_val = 0.0
if 'c_du_val' not in st.session_state: st.session_state.c_du_val = 22
if 't_br_val' not in st.session_state: st.session_state.t_br_val = 14.50
if 't_us_val' not in st.session_state: st.session_state.t_us_val = 3.75

if 'k97_abertura_base' not in st.session_state: st.session_state.k97_abertura_base = None
if 'k97_proximo_timestamp_8m' not in st.session_state: st.session_state.k97_proximo_timestamp_8m = None
if 'k97_delta_acumulado' not in st.session_state: st.session_state.k97_delta_acumulado = 0.0
if 'k97_base_forca_ciclo' not in st.session_state: st.session_state.k97_base_forca_ciclo = 0.0
if 'last_valid_res' not in st.session_state: st.session_state.last_valid_res = None

def fetch(s):
    fallback = {"at": 0.0, "cl": 1.0, "op": 0.0, "mx": 0.0, "mn": 0.0}
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        if s == "^TNX":
            info = t.fast_info
            d = t.history(period="1d", interval="1m")
            if d.empty: return st.session_state.market_data.get(s, fallback)
            data = {"at": float(info.last_price), "cl": float(info.previous_close if info.previous_close else d['Open'].iloc[0]), "op": float(d['Open'].iloc[0]), "mx": float(d['High'].max()), "mn": float(d['Low'].min())}
        else:
            d = t.history(period="1d", interval="1m", prepost=True)
            if d.empty: return st.session_state.market_data.get(s, fallback)
            ref_close = t.info.get('previousClose')
            if not ref_close: ref_close = d['Open'].iloc[0]
            if s == "EWZ":
                d_hist = t.history(period="3d", interval="1m", prepost=True)
                if not d_hist.empty:
                    d_hist.index = d_hist.index.tz_convert(tz_sp)
                    unique_dates = sorted(list(set(d_hist.index.date)))
                    data_anterior = unique_dates[-2] if len(unique_dates) > 1 else unique_dates[0]
                    f_21h = d_hist.between_time('05:00', '21:00').loc[d_hist.index.date == data_anterior]
                    if not f_21h.empty: ref_close = f_21h['Close'].iloc[-1]
            m = 1000 if s == "USDBRL=X" else 1
            data = {"at": float(d['Close'].iloc[-1] * m), "cl": float(ref_close * m), "op": float(d['Open'].iloc[0] * m), "mx": float(d['High'].max() * m), "mn": float(d['Low'].min() * m)}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s, fallback)

# =============================================================================
# # BLOCO 4: NÚCLEO MATEMÁTICO CENTRAL
# =============================================================================
def calcular_k97_total(spreed_do_dia, spot_data, ewz_data):
    try:
        if not spot_data or not ewz_data or spot_data['at'] == 0: return st.session_state.last_valid_res
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        spreed_t = spot_data['mx'] - spot_data['mn']
        spreed_50 = spreed_t / 2
        fraja_val = spot_data['at'] + spreed_do_dia
        dxy_data = fetch("DX-Y.NYB")
        v_dxy = ((dxy_data['at'] / dxy_data['cl']) - 1) if dxy_data['cl'] > 0 else 0
        ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
        v_ewz = ((ewz_data['at'] / ewz_ref) - 1) if ewz_ref > 0 else 0
        calc_variacoes_pct = (v_dxy * 0.7) - (v_ewz * 0.3)
        vivo_val = spot_data['cl'] * (1 + calc_variacoes_pct) 
        axis_dinamico = dolar_medio + spreed_do_dia
        passo_fixo = spreed_50 / 4
        alvo_low = spot_data['mn'] + spreed_do_dia
        alvo_high = spot_data['mx'] + spreed_do_dia
        diff = spot_data['at'] - vivo_val
        p_v, p_r = 0, 0
        seta_txt, seta_cor, piscando = "", "#000000", False
        if spreed_t > 0:
            calculo_pct = (abs(diff) / spreed_t) * 100 
            if diff < 0: p_v = min(100, calculo_pct)
            else: p_r = min(100, calculo_pct)
        if p_v >= 100: seta_txt, seta_cor, piscando = "▲ REGIÃO DE COMPRA", "#00ff88", True
        elif p_r >= 100: seta_txt, seta_cor, piscando = "▼ REGIÃO DE VENDA", "#ff4d4d", True
        v_spot_pct = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        dolfut_atual_calc = axis_dinamico * (1 + calc_variacoes_pct)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        now_br = datetime.now(tz_sp)
        
        # ... (Logica de histórico simplificada omitida para brevidade no exemplo) ...
        
        preco_spot_atual = spot_data['at'] if spot_data['at'] > 100 else spot_data['at'] * 1000
        agora_timestamp = datetime.now(tz_sp)
        
        # Lógica Delta
        if st.session_state.k97_abertura_base is None:
            st.session_state.k97_abertura_base = preco_spot_atual
        
        # Reset 8m
        if st.session_state.k97_proximo_timestamp_8m is None or agora_timestamp >= st.session_state.k97_proximo_timestamp_8m:
            st.session_state.k97_base_forca_ciclo = (preco_spot_atual - st.session_state.k97_abertura_base) / 1000
            st.session_state.k97_abertura_base = preco_spot_atual
            st.session_state.k97_proximo_timestamp_8m = agora_timestamp + timedelta(minutes=8)
            
        fracao_4s = (preco_spot_atual - st.session_state.k97_abertura_base) / 1000
        delta_calc = st.session_state.k97_base_forca_ciclo + fracao_4s

        output_res = {
            "vivo": vivo_val, "vivo_pct": calc_variacoes_pct * 100, "dolfut_calc": dolfut_atual_calc, 
            "axis_central": axis_dinamico, "max_fut_1": axis_dinamico + passo_fixo, "max_fut_1_b": axis_dinamico + (passo_fixo * 2),
            "max_fut_2": axis_dinamico + (passo_fixo * 3), "max_fut_2_b": axis_dinamico + (passo_fixo * 4),
            "min_fut_1": axis_dinamico - passo_fixo, "min_fut_1_b": axis_dinamico - (passo_fixo * 2),
            "min_fut_2": axis_dinamico - (passo_fixo * 3), "min_fut_2_b": axis_dinamico - (passo_fixo * 4),
            "v_v": calc_variacoes_pct * 100, "p_v": p_v, "p_r": p_r, "seta": seta_txt, "seta_cor": seta_cor, "piscando": piscando, 
            "max_grade": st.session_state.dolfut_max_auto, "min_grade": st.session_state.dolfut_min_auto, 
            "alvo_low": alvo_low, "alvo_high": alvo_high, "spreed_t": spreed_t,
            "delta_spot_forca": round(delta_calc, 2), # ARREDONDADO PARA 2 CASAS
            "base_forca_ciclo": round(st.session_state.k97_base_forca_ciclo, 2),
            "preco_base_atual": st.session_state.k97_abertura_base / 1000
        }
        st.session_state.last_valid_res = output_res
        return output_res
    except: return st.session_state.last_valid_res

# ... (Bloco 5 e 6 com a alteração no delta_atual visual) ...
# No Bloco 6, altere a exibição do delta para:
# <span style="color:{cor_delta_txt}; font-size: 14px; font-weight: bold;">{delta_atual:+.2f}</span>

# Ajuste final do loop:
# time.sleep(6)
