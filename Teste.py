import streamlit as st
import yfinance as yf
import time
from datetime import datetime, timedelta
import pytz

# Configuração para Tablet
st.set_page_config(page_title="K97 - EIXO MÉDIO AUTO", layout="wide")

# --- FUNÇÃO PARA PEGAR MÁX/MÍN DO PREGÃO ANTERIOR ---
@st.cache_data(ttl=60)
def calcular_eixo_anterior():
    try:
        t = yf.Ticker("EWZ")
        # Pegamos os últimos 5 dias para garantir que pegamos o último pregão útil
        df = t.history(period="5d", interval="30m", prepost=False) 
        
        # Pegar as datas únicas e selecionar a penúltima (ontem útil)
        datas_disponiveis = df.index.normalize().unique()
        data_ontem = datas_disponiveis[-2] 
        
        # Filtrar o pregão das 10:30 às 17:00 (Horário de Brasília aprox.)
        # No yfinance, o horário vem em UTC ou local de NY. Ajustamos para o miolo do pregão.
        df_ontem = df.loc[data_ontem.strftime('%Y-%m-%d')]
        
        max_ontem = df_ontem['High'].max()
        min_ontem = df_ontem['Low'].min()
        
        eixo_calculado = (max_ontem + min_ontem) / 2
        return eixo_calculado, max_ontem, min_ontem
    except:
        return 37.85, 0, 0 # Valor padrão caso falhe

@st.cache_data(ttl=2)
def fetch_live_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        return {"at": df['Close'].iloc[-1], "mx": df['High'].max(), "mn": df['Low'].min()}
    except: return None

# --- MOTOR DE CÁLCULO K97 ---
def calcular_k97(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 2
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 3.6
        dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
        
        alvo_max = eixo_dol * (1 + (((eixo_ewz / min_ewz) - 1) * 100 / 2 / 100))
        alvo_min = eixo_dol * (1 + (((eixo_ewz / max_ewz) - 1) * 100 / 2 / 100))
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "v_atual": var_atual,
            "max": alvo_max, "min": alvo_min,
            "p50_up": (eixo_dol + alvo_max) / 2,
            "p50_down": (eixo_dol + alvo_min) / 2
        }
    except: return None

# --- ESTILO ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .vivo-box { background: #161b22; border: 2px solid #ffcc00; padding: 15px; text-align: center; border-radius: 8px; }
    .label-k97 { color: #00f2ff; font-size: 12px; font-weight: bold; }
    .valor-vivo { font-size: 40px; font-family: 'Arial Black'; color: #ffcc00; }
    .metric-card { background: #1c1c1c; padding: 10px; border-radius: 5px; border: 1px solid #333; margin-top: 5px; }
</style>""", unsafe_allow_html=True)

# Lógica de Inicialização
eixo_auto, m_ontem, mn_ontem = calcular_eixo_anterior()
data_live = fetch_live_data()

with st.sidebar:
    st.header("⚙️ CONFIG K97")
    eixo_final = st.number_input("EIXO EWZ (MÉDIA ONTEM):", value=float(eixo_auto), format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT (AJUSTE B3):", value=5219.50)
    st.caption(f"Ref Ontem: Máx {m_ontem:.2f} | Mín {mn_ontem:.2f}")

if data_live:
    res = calcular_k97(eixo_final, data_live["at"], data_live["mx"], data_live["mn"], e_dol)
    if res:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown(f'<div class="vivo-box"><div class="label-k97">SINTÉTICO (2.0)</div><div class="valor-vivo">{res["vivo"]:.2f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><div class="label-k97">SINTÉTICO (3.6)</div><div style="font-size:24px; font-weight:bold;">{res["fraja"]:.2f}</div></div>', unsafe_allow_html=True)
            st.metric("EWZ VIVO", f"{data_live['at']:.2f}", delta=f"{res['v_atual']:+.2f}%")

        with c2:
            st.write("### ESCADA DE EXAUSTÃO")
            st.info(f"EIXO DOLFUT: {e_dol:.2f}")
            st.error(f"MÁXIMA SINTÉTICA: {res['max']:.2f}")
            st.warning(f"ALVO 50% UP: {res['p50_up']:.2f}")
            st.success(f"ALVO 50% DN: {res['p50_down']:.2f}")
            st.success(f"MÍNIMA SINTÉTICA: {res['min']:.2f}")

time.sleep(2)
st.rerun()
