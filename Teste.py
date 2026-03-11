import streamlit as st
import yfinance as yf
import time
from datetime import datetime, timedelta
import pytz

# Configuração para Tablet
st.set_page_config(page_title="K97 - EIXO MÉDIO AUTO", layout="wide")

# --- FUNÇÃO PARA PEGAR MÁX/MÍN DO PREGÃO ANTERIOR (10:30 - 17:00) ---
@st.cache_data(ttl=3600) # Atualiza apenas uma vez por hora (eixo de ontem é fixo)
def calcular_eixo_anterior():
    try:
        t = yf.Ticker("EWZ")
        # Pegamos os últimos dias para garantir que pegamos o pregão útil
        df = t.history(period="5d", interval="15m", prepost=False) 
        if df.empty: return 37.85, 0, 0
        
        # Identificar as datas e pegar a do último pregão fechado
        datas_unicas = df.index.normalize().unique()
        data_ontem = datas_unicas[-2] 
        
        # Filtrar apenas o dia de ontem
        df_ontem = df.loc[data_ontem.strftime('%Y-%m-%d')].copy()
        
        # Filtrar o intervalo específico: 10:30 às 17:00 (Horário de Brasília)
        # Nota: O yfinance usa o horário de NY. 10:30 BR costuma ser 09:30 ou 08:30 NY dependendo do fuso.
        # Para garantir, filtramos pelo miolo do pregão onde a liquidez é máxima.
        df_filtrado = df_ontem.between_time('09:30', '16:00') # Horário padrão NYSE
        
        max_periodo = df_filtrado['High'].max()
        min_periodo = df_filtrado['Low'].min()
        eixo_calculado = (max_periodo + min_periodo) / 2
        
        return eixo_calculado, max_periodo, min_periodo
    except:
        return 37.85, 0, 0

@st.cache_data(ttl=2)
def fetch_live_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        if df.empty: return None
        return {"at": df['Close'].iloc[-1], "mx": df['High'].max(), "mn": df['Low'].min()}
    except: return None

# --- MOTOR DE CÁLCULO K97 ---
def calcular_k97(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        # Sintético 2.0
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 2
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        
        # Sintético 3.6 (Fraja)
        var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 3.6
        dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
        
        # Alvos de Exaustão (Escada)
        var_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2
        var_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2
        alvo_max = eixo_dol * (1 + (var_pos / 100))
        alvo_min = eixo_dol * (1 + (var_neg / 100))
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "v_atual": var_atual,
            "max": alvo_max, "min": alvo_min,
            "p50_up": (eixo_dol + alvo_max) / 2,
            "p50_down": (eixo_dol + alvo_min) / 2
        }
    except: return None

# --- ESTILO VISUAL ---
st.markdown("""
<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .vivo-box { background: #161b22; border: 2px solid #ffcc00; padding: 15px; text-align: center; border-radius: 8px; }
    .label-k97 { color: #00f2ff; font-size: 13px; font-weight: bold; }
    .valor-vivo { font-size: 42px; font-family: 'Arial Black'; color: #ffcc00; line-height: 1; }
    .price-row { display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #2d333b; font-size: 18px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Lógica de Execução
eixo_auto, mx_ant, mn_ant = calcular_eixo_anterior()
data_live = fetch_live_data()

with st.sidebar:
    st.header("⚙️ K97 CONTROL")
    eixo_final = st.number_input("EIXO EWZ (AUTO):", value=float(eixo_auto), format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT (AJUSTE):", value=5219.50)
    st.markdown(f"**Ref Ontem (10:30-17:00):**")
    st.write(f"Máx: {mx_ant:.2f} | Mín: {mn_ant:.2f}")

if data_live:
    res = calcular_k97(eixo_final, data_live["at"], data_live["mx"], data_live["mn"], e_dol)
    if res:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown(f'<div class="vivo-box"><div class="label-k97">SINTÉTICO (2.0)</div><div class="valor-vivo">{res["vivo"]:.2f}</div></div>', unsafe_allow_html=True)
            st.write(f"Sintético (3.6): **{res['fraja']:.2f}**")
            st.metric("EWZ VIVO", f"{data_live['at']:.2f}", delta=f"{res['v_atual']:+.2f}%")
        
        with c2:
            st.markdown(f'<div class="price-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res["max"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#fab1a0;"><span>50% UP</span> <span>{res["p50_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center; padding:5px; background:#1e2226; color:#00f2ff; margin:5px 0;">EIXO: {e_dol:.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#81ecec;"><span>50% DN</span> <span>{res["p50_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{res["min"]:.2f}</span></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
