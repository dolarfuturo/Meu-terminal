import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - TERMINAL COMPLETO", layout="wide")

# --- MOTOR DE CÁLCULO K97 (VIVO + MICROS) ---
def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        # 1. PREÇO VIVO AGORA
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 2
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        
        # 2. ALVOS DE EXAUSTÃO
        var_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2
        var_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2
        alvo_max = eixo_dol * (1 + (var_pos / 100))
        alvo_min = eixo_dol * (1 + (var_neg / 100))
        
        # 3. MICROS VARIÁVEIS (SUA DIVISÃO MÉDIA)
        p50_up = (eixo_dol + alvo_max) / 2
        p25_up = (eixo_dol + p50_up) / 2
        p75_up = (p50_up + alvo_max) / 2
        
        p50_down = (eixo_dol + alvo_min) / 2
        p25_down = (eixo_dol + p50_down) / 2
        p75_down = (p50_down + alvo_min) / 2
        
        return {
            "vivo": dolar_vivo, "v_atual": var_atual,
            "max": alvo_max, "p75_up": p75_up, "p50_up": p50_up, "p25_up": p25_up,
            "min": alvo_min, "p75_down": p75_down, "p50_down": p50_down, "p25_down": p25_down
        }
    except: return None

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
    .vivo-box { background: #161b22; border: 2px solid #ffcc00; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 15px; }
    .price-row { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 22px; font-weight: bold; }
    .eixo-box { background: #1e2226; border: 2px solid #00f2ff; padding: 10px; text-align: center; margin: 5px 0; border-radius: 5px; }
    .label-k97 { color: #00f2ff; font-size: 13px; font-weight: bold; }
    .valor-vivo { font-size: 45px; font-family: 'Arial Black'; color: #ffcc00; line-height: 1.1; }
</style>""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ CALIBRAÇÃO")
    e_ewz = st.number_input("EIXO EWZ:", value=37.85, format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f")

data = fetch_data()

if data:
    res = calcular_k97_total(e_ewz, data["at"], data["mx"], data["mn"], e_dol)
    
    if res:
        # --- BLOCO 1: PREÇO VIVO (O QUE ESTÁ ACONTECENDO AGORA) ---
        st.markdown('<div class="vivo-box">', unsafe_allow_html=True)
        st.markdown('<div class="label-k97">DÓLAR SINTÉTICO VIVO</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="valor-vivo">{res["vivo"]:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#848e9c; font-size:16px;">Var EWZ: {res["v_atual"]:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- BLOCO 2: ESCADA DE MICROS VARIÁVEIS ---
        # Resistências
        st.markdown(f'<div class="price-row" style="color:#ff4d4d; border-top: 2px solid #ff4d4d;"><span>MÁXIMA SINTÉTICA</span> <span>{res["max"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#ff7675;"><span>NÍVEL 75%</span> <span>{res["p75_up"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#fab1a0;"><span>NÍVEL 50%</span> <span>{res["p50_up"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#ffeaa7;"><span>NÍVEL 25%</span> <span>{res["p25_up"]:.2f}</span></div>', unsafe_allow_html=True)

        # Eixo
        st.markdown(f'<div class="eixo-box"><div class="label-k97">EIXO DOLFUT</div><div style="font-size:30px; font-weight:900;">{e_dol:.2f}</div></div>', unsafe_allow_html=True)

        # Suportes
        st.markdown(f'<div class="price-row" style="color:#ffeaa7;"><span>NÍVEL 25%</span> <span>{res["p25_down"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#81ecec;"><span>NÍVEL 50%</span> <span>{res["p50_down"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#55efc4;"><span>NÍVEL 75%</span> <span>{res["p75_down"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#00ff88; border-bottom: 2px solid #00ff88;"><span>MÍNIMA SINTÉTICA</span> <span>{res["min"]:.2f}</span></div>', unsafe_allow_html=True)

        st.caption(f"EWZ VIVO: {data['at']:.2f} | MÁX: {data['mx']:.2f} | MÍN: {data['mn']:.2f}")

time.sleep(2)
st.rerun()
