import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - TERMINAL COLUNAS", layout="wide")

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

# --- ESTILO VISUAL DISCRETO ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .col-box { background: #161b22; padding: 10px; border-radius: 4px; border: 1px solid #2d333b; }
    .price-row-mini { display: flex; justify-content: space-between; padding: 5px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 15px; }
    .label-k97 { color: #00f2ff; font-size: 12px; font-weight: bold; margin-bottom: 5px; }
    .valor-discreto { font-size: 32px; font-family: 'monospace'; font-weight: bold; color: #ffcc00; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ AJUSTE")
    e_ewz = st.number_input("EIXO EWZ:", value=37.85, format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f")

data = fetch_data()

if data:
    res = calcular_k97_total(e_ewz, data["at"], data["mx"], data["mn"], e_dol)
    if res:
        c1, c2 = st.columns([1, 1])

        with c1:
            st.markdown('<div class="col-box">', unsafe_allow_html=True)
            st.markdown('<div class="label-k97">DÓLAR SINTÉTICO VIVO</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="valor-discreto">{res["vivo"]:.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:14px; color:#848e9c;">Var: {res["v_atual"]:+.2f}%</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="margin-top:10px;">', unsafe_allow_html=True)
            st.write(f"EWZ Atual: {data['at']:.2f}")
            st.write(f"Eixo Dol: {e_dol:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="col-box">', unsafe_allow_html=True)
            st.markdown('<div class="label-k97">ESCADA DE ALVOS</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res["max"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini"><span>75% UP</span> <span>{res["p75_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini"><span>50% UP</span> <span>{res["p50_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini"><span>25% UP</span> <span>{res["p25_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="background:#1e2226;"><span>EIXO</span> <span>{e_dol:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini"><span>25% DN</span> <span>{res["p25_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini"><span>50% DN</span> <span>{res["p50_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini"><span>75% DN</span> <span>{res["p75_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#00ff88; border-bottom:none;"><span>MÍNIMA</span> <span>{res["min"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.caption(f"Max EWZ: {data['mx']:.2f} | Min EWZ: {data['mn']:.2f}")

time.sleep(2)
st.rerun()
