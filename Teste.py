import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - MICROS VARIAVEIS", layout="wide")

# --- MOTOR DE CÁLCULO K97 (COM FRACIONAMENTO) ---
def calcular_micros_k97(eixo_ewz, max_ewz, min_ewz, eixo_dol):
    try:
        # 1. Calcular as Variações Máximas
        var_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2  # Suporte (EWZ na Max)
        var_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2  # Resistência (EWZ na Min)
        
        # 2. Alvos Finais
        alvo_max = eixo_dol * (1 + (var_pos / 100))
        alvo_min = eixo_dol * (1 + (var_neg / 100))
        
        # 3. Gerar Micros Variáveis (Frações 2, 4, 6)
        def fracionar(inicio, fim):
            diff = fim - inicio
            return {
                "f2": inicio + (diff / 2),
                "f4": inicio + (diff / 4),
                "f6": inicio + (diff / 6)
            }
        
        micros_cima = fracionar(eixo_dol, alvo_max)
        micros_baixo = fracionar(eixo_dol, alvo_min)
        
        return alvo_max, alvo_min, micros_cima, micros_baixo, var_pos, var_neg
    except:
        return 0, 0, {}, {}, 0, 0

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
    .metric-val { font-size: 38px; font-family: 'Arial Black'; font-weight: 900; }
    .frame-box { border: 1px solid #3d444d; padding: 15px; background: #161b22; border-radius: 4px; margin-bottom: 10px; }
    .micro-row { display: flex; justify-content: space-between; padding: 5px; border-bottom: 1px solid #2d333b; font-size: 18px; }
    .label-k97 { color: #00f2ff; font-weight: bold; font-size: 14px; }
</style>""", unsafe_allow_html=True)

st.title("K97 - MICROS VARIÁVEIS DE CORREÇÃO")

with st.sidebar:
    st.header("⚙️ CALIBRAÇÃO")
    e_ewz = st.number_input("EIXO EWZ:", value=35.70, format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")

data = fetch_data()

if data:
    mx_alvo, mn_alvo, m_cima, m_baixo, v_p, v_n = calcular_micros_k97(e_ewz, data["mx"], data["mn"], e_dol)
    
    col1, col2 = st.columns(2)

    # --- COLUNA DE RESISTÊNCIAS (SUBIDA) ---
    with col1:
        st.markdown('<div class="frame-box" style="border-top: 4px solid #ff4d4d;">', unsafe_allow_html=True)
        st.markdown(f'<div class="label-k97">MÁXIMA SINTÉTICA (+{v_p:.2f}%)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val" style="color:#ff4d4d;">{mx_alvo:.2f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("📌 Pontos de Correção (Subida):")
        st.markdown(f'<div class="micro-row"><span>Fração 2 (50%)</span> <b>{m_cima["f2"]:.2f}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="micro-row"><span>Fração 4 (25%)</span> <b>{m_cima["f4"]:.2f}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="micro-row"><span>Fração 6 (16%)</span> <b>{m_cima["f6"]:.2f}</b></div>', unsafe_allow_html=True)

    # --- COLUNA DE SUPORTES (DESCIDA) ---
    with col2:
        st.markdown('<div class="frame-box" style="border-top: 4px solid #00ff88;">', unsafe_allow_html=True)
        st.markdown(f'<div class="label-k97">MÍNIMA SINTÉTICA ({v_n:.2f}%)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val" style="color:#00ff88;">{mn_alvo:.2f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("📌 Pontos de Correção (Descida):")
        st.markdown(f'<div class="micro-row"><span>Fração 2 (50%)</span> <b>{m_baixo["f2"]:.2f}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="micro-row"><span>Fração 4 (25%)</span> <b>{m_baixo["f4"]:.2f}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="micro-row"><span>Fração 6 (16%)</span> <b>{m_baixo["f6"]:.2f}</b></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption(f"EWZ VIVO: {data['at']:.2f} | Eixo Dólar: {e_dol:.2f}")



### Como ler o Terminal agora:
* **Fração 6 (Mínima Distância):** É o primeiro "degrau". Se o preço romper aqui, ele tende a buscar a Fração
