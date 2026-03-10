import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - PREÇO VIVO", layout="wide")

# --- MOTOR DE CÁLCULO K97 ---
def calcular_k97_completo(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        # 1. VARIAÇÃO REAL AGORA
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 2
        dolar_sintetico_vivo = eixo_dol * (1 + (var_atual / 100))
        
        # 2. VARIAÇÕES DE EXTREMO (MÁX/MÍN)
        var_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2
        var_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2
        
        alvo_max = eixo_dol * (1 + (var_pos / 100))
        alvo_min = eixo_dol * (1 + (var_neg / 100))
        
        # 3. PONTOS MÉDIOS
        p50_up = (eixo_dol + alvo_max) / 2
        p50_down = (eixo_dol + alvo_min) / 2
        
        return {
            "vivo": dolar_sintetico_vivo, "v_atual": var_atual,
            "max": alvo_max, "p50_up": p50_up,
            "min": alvo_min, "p50_down": p50_down
        }
    except:
        return None

# --- CAPTURA DE DADOS ---
@st.cache_data(ttl=2)
def fetch_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        if not df.empty:
            return {"at": df['Close'].iloc[-1], "mx": df['High'].max(), "mn": df['Low'].min()}
        return None
    except: return None

# --- ESTILO VISUAL ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .vivo-box { background: #161b22; border: 3px solid #ffcc00; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 20px; }
    .price-row { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 22px; font-weight: bold; }
    .label-k97 { color: #00f2ff; font-size: 14px; font-weight: bold; }
    .valor-principal { font-size: 55px; font-family: 'Arial Black'; color: #ffcc00; line-height: 1; }
</style>""", unsafe_allow_html=True)

st.title("K97 - TERMINAL REAL-TIME")

with st.sidebar:
    st.header("⚙️ CALIBRAÇÃO")
    e_ewz = st.number_input("EIXO EWZ:", value=37.85, format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f")

data = fetch_data()

if data:
    res = calcular_k97_completo(e_ewz, data["at"], data["mx"], data["mn"], e_dol)
    
    if res:
        # --- PREÇO REAL SINTÉTICO (CENTRAL) ---
        st.markdown('<div class="vivo-box">', unsafe_allow_html=True)
        st.markdown('<div class="label-k97">DÓLAR SINTÉTICO AGORA (PREÇO REAL)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="valor-principal">{res["vivo"]:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:18px; color:#848e9c;">Var EWZ: {res["v_atual"]:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- ESCADA DE ALVOS ---
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="price-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res["max"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#fab1a0;"><span>NÍVEL 50%</span> <span>{res["p50_up"]:.2f}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="price-row" style="color:#81ecec;"><span>NÍVEL 50%</span> <span>{res["p50_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{res["min"]:.2f}</span></div>', unsafe_allow_html=True)

        st.markdown(f'<div style="text-align:center; padding:10px; background:#1e2226; margin-top:10px;">EIXO REFERÊNCIA: {e_dol:.2f}</div>', unsafe_allow_html=True)
        st.info(f"EWZ VIVO: {data['at']:.2f} | MÁX: {data['mx']:.2f} | MÍN: {data['mn']:.2f}")

time.sleep(2)
st.rerun()
