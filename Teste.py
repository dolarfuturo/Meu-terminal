import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(page_title="K97 - TERMINAL AUTO", layout="wide")

# --- MOTOR DE CÁLCULO K97 ---
def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 2
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        
        var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 3.6
        dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
        
        var_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2
        var_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2
        alvo_max = eixo_dol * (1 + (var_pos / 100))
        alvo_min = eixo_dol * (1 + (var_neg / 100))
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "v_atual": var_atual,
            "max": alvo_max, "min": alvo_min,
            "p75_up": (eixo_dol + alvo_max) / 2 * 1.25, # Ajuste de escala micros
            "p50_up": (eixo_dol + alvo_max) / 2,
            "p25_up": (eixo_dol + ((eixo_dol + alvo_max) / 2)) / 2,
            "p50_down": (eixo_dol + alvo_min) / 2,
            "p25_down": (eixo_dol + ((eixo_dol + alvo_min) / 2)) / 2,
            "p75_down": (((eixo_dol + alvo_min) / 2) + alvo_min) / 2
        }
    except: return None

@st.cache_data(ttl=2)
def fetch_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        if not df.empty:
            return {"at": df['Close'].iloc[-1], "mx": df['High'].max(), "mn": df['Low'].min()}
        return None
    except: return None

# --- CONTROLE DE HORÁRIO ---
tz_sp = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(tz_sp)
hora_atual = agora.strftime("%H:%M")
mercado_aberto = "10:30" <= hora_atual <= "18:00"

# --- ESTILO ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .vivo-box { background: #161b22; border: 2px solid #ffcc00; padding: 15px; text-align: center; border-radius: 8px; }
    .fraja-box { background: #1c1c1c; border: 1px dashed #ffffff; padding: 10px; text-align: center; border-radius: 8px; margin-top: 10px; }
    .price-row-mini { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 16px; font-weight: bold; }
    .label-k97 { color: #00f2ff; font-size: 12px; font-weight: bold; }
