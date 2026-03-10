import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - ESCADA DE PREÇO", layout="wide")

# --- MOTOR DE CÁLCULO K97 (FRAÇÕES) ---
def calcular_escada_k97(eixo_ewz, max_ewz, min_ewz, eixo_dol):
    try:
        # Variações Máximas
        var_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2  # Alvo Baixo
        var_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2  # Alvo Cima
        
        alvo_max = eixo_dol * (1 + (var_pos / 100))
        alvo_min = eixo_dol * (1 + (var_neg / 100))
        
        # Frações para Cima (entre Eixo e Alvo Máximo)
        diff_cima = alvo_max - eixo_dol
        cima = {
            "f2": eixo_dol + (diff_cima / 2),
            "f4": eixo_dol + (diff_cima / 4),
            "f6": eixo_dol + (diff_cima / 6)
        }
        
        # Frações para Baixo (entre Eixo e Alvo Mínimo)
        diff_baixo = alvo_min - eixo_dol
        baixo = {
            "f2": eixo_dol + (diff_baixo / 2),
            "f4": eixo_dol + (diff_baixo / 4),
            "f6": eixo_dol + (diff_baixo / 6)
        }
        
        return alvo_max, alvo_min, cima, baixo
    except:
        return 0, 0, {}, {}

# --- CAPTURA DE DADOS ---
@st.cache_data(ttl=2)
def fetch_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        return {"at": df['Close'].iloc[-1], "mx": df['High'].max(), "mn": df['Low'].min()} if not df.empty else None
    except: return None

# --- ESTILO VISUAL ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .price-row { display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 22px; font-weight: bold; }
    .eixo-box { background: #1e2226; border: 2px solid #00f2ff; padding: 15px; text-align: center; margin: 10px 0; border-radius: 5px; }
    .label-k97 { color: #00f2ff; font-size: 14px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

st.title("K97 - ESCADA DE VOLATILIDADE")

with st.sidebar:
    st.header("⚙️ AJUSTE")
    e_ewz = st.number_input("EIXO EWZ:", value=35.70, format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")

data = fetch_data()

if data:
    alvo_up, alvo_down, c, b = calcular_escada_k97(e_ewz, data["mx"], data["mn"], e_dol)
    
    # --- PARTE SUPERIOR (PARA CIMA) ---
    st.markdown(f'<div class="price-row" style="color:#ff4d4d; border-top: 3px solid #ff4d4d;"><span>MÁXIMA SINTÉTICA (EWZ MÍN)</span> <span>{alvo_up:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="price-row" style="color:#ff7675;"><span>FRAÇÃO 2 (50%)</span> <span>{c["f2"]:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="price-row" style="color:#fab1a0;"><span>FRAÇÃO 4 (25%)</span> <span>{c["f4"]:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="price-row" style="color:#ffeaa7;"><span>FRAÇÃO 6 (16%)</span> <span>{c["f6"]:.2f}</span></div>', unsafe_allow_html=True)

    # --- CENTRO (EIXO) ---
    st.markdown(f'<div class="eixo-box"><div class="label-k97">EIXO DOLFUT (REFERÊNCIA)</div><div style="font-size:35px; font-weight:900;">{e_dol:.2f}</div></div>', unsafe_allow_html=True)

    # --- PARTE INFERIOR (PARA BAIXO) ---
    st.markdown(f'<div class="price-row" style="color:#a29bfe;"><span>FRAÇÃO 6 (16%)</span> <span>{b["f6"]:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="price-row" style="color:#81ecec;"><span>FRAÇÃO 4 (25%)</span> <span>{b["f4"]:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="price-row" style="color:#55efc4;"><span>FRAÇÃO 2 (50%)</span> <span>{b["f2"]:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="price-row" style="color:#00ff88; border-bottom: 3px solid #00ff88;"><span>MÍNIMA SINTÉTICA (EWZ MÁX)</span> <span>{alvo_down:.2f}</span></div>', unsafe_allow_html=True)

    st.info(f"EWZ VIVO: {data['at']:.2f} | MÁX: {data['mx']:.2f} | MÍN: {data['mn']:.2f}")

else:
    st.warning("Aguardando dados...")

time.sleep(2)
st.rerun()
