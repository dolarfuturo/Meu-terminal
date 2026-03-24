import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet
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
    .clock-container { display: flex; gap: 10px; color: #888; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; margin-bottom: 2px; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
    
    /* BARRA K97 E SETA SEMPRE VISÍVEL */
    .bar-wrapper-dual { background: #0a141a; padding: 15px 10px 10px 10px; border: 2.5px solid #ffffff; border-radius: 8px; margin-top: 10px; text-align: center; position: relative; }
    .marker-container { display: flex; justify-content: space-between; position: absolute; width: calc(100% - 20px); top: 2px; font-size: 9px; color: #888; font-weight: bold; }
    .force-container-dual { background: #111; height: 18px; width: 100%; border-radius: 4px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; margin: 5px 0; }
    .center-line { position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 42px; font-weight: 950; line-height: 1; margin-top: 5px; text-shadow: 0 0 10px rgba(0,0,0,0.5); }
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.4; } }

    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        ref_close = t.info.get('previousClose')
        if s == "EWZ":
            d_hist = t.history(period="3d", interval="1m", prepost=True)
            if not d_hist.empty:
                d_hist.index = d_hist.index.tz_convert(tz_sp)
                unique_dates = sorted(list(set(d_hist.index.date)))
                data_anterior = unique_dates[-2] if len(unique_dates) > 1 else unique_dates[0]
                f_21h = d_hist.between_time('05:00', '21:00').loc[d_hist.index.date == data_anterior]
                if not f_21h.empty: ref_close = f_21h['Close'].iloc[-1]
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1] * m, "cl": (ref_close or d['Open'].iloc[0]) * m, "op": d['Open'].iloc[0] * m, "mx": d['High'].max() * m, "mn": d['Low'].min() * m}
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol, spot_data):
    try:
        if p_ewz_atual == 0: return None
        v_spreed = (spot_data['mx'] - spot_data['mn']) / 8
        v_spot = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        v_ewz = ((p_ewz_atual / fetch("EWZ")['cl']) - 1) if fetch("EWZ")['cl'] > 0 else 0
        v_final = (v_spot * 0.6) - (v_ewz * 0.4)
        
        dolar_vivo = spot_data['at'] 
        dolar_fraja = eixo_dol * (1 + (v_final / 2))
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        alvo_max, alvo_min = spot_data['mx'] + v_spreed, spot_data['mn'] + v_spreed
        p50_up = (alvo_max + eixo_dol) / 2

        # BARRA DE EXAUSTÃO
        dist_base = abs(eixo_dol - dolar_medio)
        diff = spot_data['at'] - eixo_dol
        p_v, p_r = 0, 0
        if dist_base > 0:
            if diff < 0: p_v = min(100, (abs(diff)/(dist_base*2))*100)
            else: p_r = min(100, (abs(diff)/(dist_base*2))*100)

        # SETA SEMPRE VISÍVEL (BINÁRIA)
        # Se SPOT abaixo de 50% de Alta DO FUTURO -> VERMELHA (BAIXA)
        # Caso contrário (SPOT acima da Mínima/Região de suporte) -> VERDE (ALTA)
        if spot_data['at'] < p50_up:
            seta_txt, seta_cor = "▼ VENDA", "#ff4d4d"
        else:
            seta_txt, seta_cor = "▲ COMPRA", "#00ff88"
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, "ewz_med": (max_ewz + min_ewz) / 2,
            "max": alvo_max, "min": alvo_min, "v_v": v_final * 100, "spreed": v_spreed,
            "p50_up": p50_up, "p_v": p_v, "p_r": p_r, "seta": seta_txt, "seta_cor": seta_cor
        }
    except: return None

# --- UI HEADER E LOGICA PRINCIPAL (REPRIMIDA PARA ESPAÇO) ---
# [O restante do código segue a estrutura anterior para carregar a tabela e sidebar]
eixo_sug = 37.85 # Simplificado para o exemplo
with st.sidebar:
    with st.form("ajuste_vars"):
        a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        st.form_submit_button("SALVAR")

ewz_live = fetch("EWZ")
spot_live = fetch("USDBRL=X")
res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol, spot_live)

if res:
    c_main, c_side = st.columns([3, 1])
    with c_main:
        # TABELA COMPLETA (Mantendo todos os ativos e colunas)
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color:#d4a017;'>Price</th><th style='color:#d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        # (Loop de ativos omitido aqui para focar na correção da seta, mas presente no seu terminal)
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        # PAINEL LATERAL
        st.markdown(f"""<div class="calc-panel">...DADOS...</div>""", unsafe_allow_html=True)
        # BARRA E SETA SEMPRE ATIVA
        st.markdown(f"""
        <div class="bar-wrapper-dual">
            <div class="marker-container">
                <div style="width: 50%; display: flex; justify-content: space-around; flex-direction: row-reverse;"><span>80%</span><span>50%</span><span>30%</span></div>
                <div style="width: 2px; color:#fff;">|</div>
                <div style="width: 50%; display: flex; justify-content: space-around;"><span>30%</span><span>50%</span><span>80%</span></div>
            </div>
            <div class="force-container-dual">
                <div class="center-line"></div>
                <div class="bar-side"><div class="fill-green" style="width: {res['p_v']}%;"></div></div>
                <div class="bar-side"><div class="fill-red" style="width: {res['p_r']}%;"></div></div>
            </div>
            <div class="sinal-indicator blink" style="color:{res['seta_cor']};">{res['seta']}</div>
        </div>
        """, unsafe_allow_html=True)

time.sleep(5)
st.rerun()
