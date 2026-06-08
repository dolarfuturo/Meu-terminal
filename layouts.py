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

# =============================================================================
# # BLOCO 2: MEMÓRIA DA SESSÃO E PERSISTÊNCIA
# =============================================================================
def salvar_eixos(div_spreed):
    with open("config_axis.txt", "w") as f: f.write(f"{div_spreed}")

def carregar_eixos():
    if os.path.exists("config_axis.txt"):
        try:
            with open("config_axis.txt", "r") as f: return float(f.read().split(",")[0])
        except: pass
    return 8.0

def carregar_historico_dolfut_diario():
    data_hoje = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
    if os.path.exists("dolfut_history.txt"):
        try:
            with open("dolfut_history.txt", "r") as f:
                conteudo = f.read().split(",")
                if conteudo[0] == data_hoje: return float(conteudo[1]), float(conteudo[2])
        except: pass
    return float('-inf'), float('inf')

def salvar_historico_dolfut_diario(mx, mn):
    data_hoje = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
    with open("dolfut_history.txt", "w") as f: f.write(f"{data_hoje},{mx},{mn}")

# Estado inicial
if 'market_data' not in st.session_state: st.session_state.market_data = {}
if 'last_p' not in st.session_state: st.session_state.last_p = {}
if 'div_spreed_mem' not in st.session_state: st.session_state.div_spreed_mem = carregar_eixos()
max_init, min_init = carregar_historico_dolfut_diario()
if 'dolfut_max_auto' not in st.session_state: st.session_state.dolfut_max_auto = max_init
if 'dolfut_min_auto' not in st.session_state: st.session_state.dolfut_min_auto = min_init
if 'c_spot_fech_val' not in st.session_state: st.session_state.c_spot_fech_val = 0.0
if 'c_du_val' not in st.session_state: st.session_state.c_du_val = 22
if 't_br_val' not in st.session_state: st.session_state.t_br_val = 14.50
if 't_us_val' not in st.session_state: st.session_state.t_us_val = 3.75
if 'last_valid_res' not in st.session_state: st.session_state.last_valid_res = None

# =============================================================================
# # BLOCO 3: CONEXÃO COM API
# =============================================================================
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return st.session_state.market_data.get(s, {"at": 0.0, "cl": 1.0, "op": 0.0, "mx": 0.0, "mn": 0.0})
        m = 1000 if s == "USDBRL=X" else 1
        data = {"at": float(d['Close'].iloc[-1] * m), "cl": float(d['Open'].iloc[0] * m), "op": float(d['Open'].iloc[0] * m), "mx": float(d['High'].max() * m), "mn": float(d['Low'].min() * m)}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s, {"at": 0.0, "cl": 1.0, "op": 0.0, "mx": 0.0, "mn": 0.0})

# =============================================================================
# # BLOCO 4: NÚCLEO MATEMÁTICO (DELTA PERSISTENTE)
# =============================================================================
def calcular_k97_total(spreed_do_dia, spot_data, ewz_data):
    try:
        preco_spot_atual = spot_data['at'] if spot_data['at'] > 100 else spot_data['at'] * 1000
        arquivo_delta = "delta_persistente.txt"
        arquivo_base = "base_persistente.txt"
        
        # Carrega persistente
        if not os.path.exists(arquivo_delta):
            delta_final = 0.0
            base_ativa = preco_spot_atual
        else:
            with open(arquivo_delta, "r") as f: delta_final = float(f.read())
            with open(arquivo_base, "r") as f: base_ativa = float(f.read())
            
        # Atualiza Delta (cálculo de força)
        delta_final += (preco_spot_atual - base_ativa) / 1000
        
        # Salva persistente
        with open(arquivo_delta, "w") as f: f.write(str(delta_final))
        with open(arquivo_base, "w") as f: f.write(str(preco_spot_atual))
        
        cor_delta = "#00ff88" if delta_final > 0.000 else "#ff4d4d"
        
        output_res = {
            "vivo": 0, "vivo_pct": 0, "dolfut_calc": 0, "fraja": 0, "medio": 0, "axis_central": 0,
            "max_fut_1": 0, "max_fut_1_b": 0, "max_fut_2": 0, "max_fut_2_b": 0,
            "min_fut_1": 0, "min_fut_1_b": 0, "min_fut_2": 0, "min_fut_2_b": 0,
            "v_v": 0, "v_spot": 0, "spreed": 0, "p_v": 0, "p_r": 0, "seta": "", "seta_cor": "#000", "piscando": False,
            "max_grade": 0, "min_grade": 0, "alvo_low": 0, "alvo_high": 0, "spreed_t": 0,
            "delta_spot_forca": delta_final, "cor_delta": cor_delta,
            "base_forca_ciclo": 0, "is_reset": False, "preco_base_atual": base_ativa / 1000
        }
        return output_res
    except: return None

# =============================================================================
# # BLOCO 5: CONTROLES OPERACIONAIS FINANCEIROS
# =============================================================================
with st.sidebar:
    st.markdown("### 🧮 CALCULADORA DE JUROS (FRP)")
    with st.expander("CALCULAR SPREED", expanded=False):
        c_spot_fech = st.number_input("FECH SPOT:", value=st.session_state.c_spot_fech_val, format="%.3f")
        c_du = st.number_input("DIAS ÚTEIS (DU):", value=st.session_state.c_du_val, step=1)
        t_br = st.number_input("JUROS BRL (%):", value=st.session_state.t_br_val, format="%.2f")
        t_us = st.number_input("JUROS USD (%):", value=st.session_state.t_us_val, format="%.2f")
        st.session_state.c_spot_fech_val, st.session_state.c_du_val, st.session_state.t_br_val, st.session_state.t_us_val = c_spot_fech, c_du, t_br, t_us
        if c_spot_fech > 0:
            spreed_calc = c_spot_fech * ((t_br / 100) - (t_us / 100)) * (c_du / 252)
            st.markdown(f"**SPREED:** {spreed_calc:.2f}")
            if st.button("USAR ESTE SPREED NO ADM"): st.session_state.div_spreed_mem = spreed_calc; st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ PAINEL ADM")
    i_div = st.number_input("FRP (PARA JUSTO):", value=st.session_state.div_spreed_mem, format="%.2f")
    if st.button("SALVAR CONFIGURAÇÕES"):
        st.session_state.div_spreed_mem = i_div
        salvar_eixos(i_div)
        st.success("Salvo!"); time.sleep(0.5); st.rerun()

# =============================================================================
# # BLOCO 6: INTERFACE DO TERMINAL
# =============================================================================
placeholder = st.empty()
while True:
    res = calcular_k97_total(st.session_state.div_spreed_mem, fetch("USDBRL=X"), fetch("EWZ"))
    with placeholder.container():
        if res:
            st.markdown(f'''
            <div class="calc-panel">
                <div class="calc-row"><span style="color:#AAA;">PREÇO BASE</span> <span style="color:#ffffff;">{res['preco_base_atual']:.4f}</span></div>
                <div class="calc-row" style="border-bottom: none;">
                    <span style="color:#ffffff;">𝚫 SPOT (FORÇA)</span> 
                    <span style="color:{res['cor_delta']}; font-size: 14px; font-weight: bold;">{res['delta_spot_forca']:+.3f}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    time.sleep(4)
