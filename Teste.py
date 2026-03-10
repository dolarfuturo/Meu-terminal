import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - TERMINAL COMPACTO", layout="wide")

# --- MOTOR DE CÁLCULO K97 ---
def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 2
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        var_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2
        var_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2
        alvo_max = eixo_dol * (1 + (var_pos / 100))
        alvo_min = eixo_dol * (1 + (var_neg / 100))
        
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

@st.cache_data(ttl=2)
def fetch_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        return {"at": df['Close'].iloc[-1], "mx": df['High'].max(), "mn": df['Low'].min()} if not df.empty else None
    except: return None

# --- ESTILO VISUAL COMPACTO ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .vivo-box { background: #161b22; border: 2px solid #ffcc00; padding: 20px; text-align: center; border-radius: 8px; }
    .price-row-mini { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 16px; font-weight: bold; }
    .eixo-box-mini { background: #1e2226; border: 1px solid #00f2ff; padding: 5px; text-align: center; margin: 5px 0; border-radius: 4px; }
    .label-k97 { color: #00f2ff; font-size: 12px; font-weight: bold; }
    .valor-vivo { font-size: 50px; font-family: 'Arial Black'; color: #ffcc00; line-height: 1; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ AJUSTE")
    e_ewz = st.number_input("EIXO EWZ:", value=37.85, format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f")

data = fetch_data()

if data:
    res = calcular_k97_total(e_ewz, data["at"], data["mx"], data["mn"], e_dol)
    if res:
        col_esq, col_dir = st.columns([1, 1.2])

        with col_esq:
            st.markdown('<div class="vivo-box">', unsafe_allow_html=True)
            st.markdown('<div class="label-k97">DÓLAR SINTÉTICO VIVO</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="valor-vivo">{res["vivo"]:.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:#848e9c; font-size:14px;">Variação: {res["v_atual"]:+.2f}%</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.metric("EWZ ATUAL", f"{data['at']:.2f}")

        with col_dir:
            st.markdown(f'<div class="price-row-mini" style="color:#ff4d4d; border-top: 2px solid #ff4d4d;"><span>MÁXIMA</span> <span>{res["max"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ff7675;"><span>75% UP</span> <span>{res["p75_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#fab1a0;"><span>50% UP</span> <span>{res["p50_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ffeaa7;"><span>25% UP</span> <span>{res["p25_up"]:.2f}</span></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="eixo-box-mini"><div class="label-k97">EIXO: {e_dol:.2f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="price-row-mini" style="color:#ffeaa7;"><span>25% DOWN</span> <span>{res["p25_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#81ecec;"><span>50% DOWN</span> <span>{res["p50_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#55efc4;"><span>75% DOWN</span> <span>{res["p75_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#00ff88; border-bottom: 2px solid #00ff88;"><span>MÍNIMA</span> <span>{res["min"]:.2f}</span></div>', unsafe_allow_html=True)

        st.caption(f"MAX EWZ: {data['mx']:.2f} | MIN EWZ: {data['mn']:.2f}")

time.sleep(2)
st.rerun()
