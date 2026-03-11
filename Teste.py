import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - ARBITRAGE SYSTEM", layout="wide")

# --- MOTOR K97 ---
def calcular_k97(eixo_ewz, p_atual, mx_ref, mn_ref, e_dol):
    try:
        # Variação Sintética (2.0)
        var_atual = ((eixo_ewz / p_atual) - 1) * 100 / 2
        dolar_vivo = e_dol * (1 + (var_atual / 100))
        
        # Projeção da Escada (Volatilidade Real de Terça)
        v_neg = ((eixo_ewz / mx_ref) - 1) * 100 / 2
        v_pos = ((eixo_ewz / mn_ref) - 1) * 100 / 2
        alvo_max = e_dol * (1 + (v_pos / 100))
        alvo_min = e_dol * (1 + (v_neg / 100))
        
        return {
            "vivo": dolar_vivo, "v_at": var_atual,
            "max": alvo_max, "p50_up": (e_dol + alvo_max) / 2,
            "min": alvo_min, "p50_down": (e_dol + alvo_min) / 2
        }
    except: return None

@st.cache_data(ttl=2)
def fetch_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        if df.empty: return None
        return {"at": df['Close'].iloc[-1]}
    except: return None

# --- UI / ESTILO ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .vivo-box { background: #161b22; border: 2px solid #ffcc00; padding: 20px; text-align: center; border-radius: 8px; }
    .price-row { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 20px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ K97 RESET")
    # Valores travados conforme sua validação
    e_ewz = st.number_input("EIXO EWZ (FIXO):", value=37.50, format="%.2f")
    mx_ref = st.number_input("MAX REF (TERÇA):", value=38.13, format="%.2f")
    mn_ref = st.number_input("MIN REF (TERÇA):", value=36.86, format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f", step=0.5)

data = fetch_data()

if data:
    res = calcular_k97(e_ewz, data['at'], mx_ref, mn_ref, e_dol)
    if res:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown(f'<div class="vivo-box"><div style="color:#00f2ff; font-size:14px;">DÓLAR SINTÉTICO (2.0)</div><div style="font-size:55px; font-family:Arial Black; color:#ffcc00;">{res["vivo"]:.2f}</div></div>', unsafe_allow_html=True)
            st.metric("EWZ VIVO", f"{data['at']:.2f}", delta=f"{res['v_at']:+.2f}%")
            
        with c2:
            st.markdown(f'<div class="price-row" style="color:#ff4d4d; border-top: 2px solid #ff4d4d;"><span>MÁXIMA</span> <span>{res["max"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#fab1a0;"><span>50% UP</span> <span>{res["p50_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center; padding:15px; color:#00f2ff; font-weight:bold; font-size:20px;">EIXO: {e_dol:.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#81ecec;"><span>50% DN</span> <span>{res["p50_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#00ff88; border-bottom: 2px solid #00ff88;"><span>MÍNIMA</span> <span>{res["min"]:.2f}</span></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
