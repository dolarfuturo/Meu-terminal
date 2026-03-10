import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - FRAÇÕES MÉDIAS", layout="wide")

# --- MOTOR DE CÁLCULO K97 (PONTOS MÉDIOS) ---
def calcular_pontos_medios(eixo_ewz, max_ewz, min_ewz, eixo_dol):
    try:
        # 1. Alvos de Exaustão (Sua fórmula base)
        var_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2
        var_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2
        
        alvo_max = eixo_dol * (1 + (var_pos / 100))
        alvo_min = eixo_dol * (1 + (var_neg / 100))
        
        # 2. Divisões para CIMA (Eixo até Máxima)
        p50_up = (eixo_dol + alvo_max) / 2
        p25_up = (eixo_dol + p50_up) / 2
        p75_up = (p50_up + alvo_max) / 2
        
        # 3. Divisões para BAIXO (Eixo até Mínima)
        p50_down = (eixo_dol + alvo_min) / 2
        p25_down = (eixo_dol + p50_down) / 2
        p75_down = (p50_down + alvo_min) / 2
        
        return {
            "max": alvo_max, "p75_up": p75_up, "p50_up": p50_up, "p25_up": p25_up,
            "min": alvo_min, "p75_down": p75_down, "p50_down": p50_down, "p25_down": p25_down
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
    .price-row { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 20px; font-weight: bold; }
    .eixo-box { background: #1e2226; border: 2px solid #00f2ff; padding: 12px; text-align: center; margin: 5px 0; border-radius: 4px; }
    .label-k97 { color: #00f2ff; font-size: 13px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

st.title("K97 - ESCADA DE PONTOS MÉDIOS")

with st.sidebar:
    st.header("⚙️ AJUSTE")
    e_ewz = st.number_input("EIXO EWZ:", value=35.70, format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")

data = fetch_data()

if data:
    res = calcular_pontos_medios(e_ewz, data["mx"], data["mn"], e_dol)
    
    if res:
        # --- ZONA DE RESISTÊNCIA (PARA CIMA) ---
        st.markdown(f'<div class="price-row" style="color:#ff4d4d; border-top: 3px solid #ff4d4d;"><span>MÁXIMA SINTÉTICA</span> <span>{res["max"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#ff7675;"><span>NÍVEL 75% (Média 50/Max)</span> <span>{res["p75_up"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#fab1a0;"><span>NÍVEL 50% (Média Eixo/Max)</span> <span>{res["p50_up"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#ffeaa7;"><span>NÍVEL 25% (Média Eixo/50)</span> <span>{res["p25_up"]:.2f}</span></div>', unsafe_allow_html=True)

        # --- CENTRO (EIXO) ---
        st.markdown(f'<div class="eixo-box"><div class="label-k97">EIXO DOLFUT</div><div style="font-size:32px; font-weight:900;">{e_dol:.2f}</div></div>', unsafe_allow_html=True)

        # --- ZONA DE SUPORTE (PARA BAIXO) ---
        st.markdown(f'<div class="price-row" style="color:#ffeaa7;"><span>NÍVEL 25% (Média Eixo/50)</span> <span>{res["p25_down"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#81ecec;"><span>NÍVEL 50% (Média Eixo/Min)</span> <span>{res["p50_down"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#55efc4;"><span>NÍVEL 75% (Média 50/Min)</span> <span>{res["p75_down"]:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-row" style="color:#00ff88; border-bottom: 3px solid #00ff88;"><span>MÍNIMA SINTÉTICA</span> <span>{res["min"]:.2f}</span></div>', unsafe_allow_html=True)

        st.info(f"EWZ: {data['at']:.2f} | MÁX: {data['mx']:.2f} | MÍN: {data['mn']:.2f}")



### Por que essa divisão é poderosa:
* **Nível 25%:** É o primeiro sinal de força. Se o dólar ganhar o 25%, ele tende a buscar o 50% rápido.
* **Nível 50%:** É o seu "Justo Intermediário". O preço costuma respeitar muito esse ponto antes de ir para a exaustão.
* **Nível 75%:** É a "Zona de Venda/Compra" final. Se chegar aqui, a probabilidade de um repique (correção) para voltar ao 50% é enorme.

**Deseja que eu coloque um botão para você travar a Máxima e Mínima do EWZ em um valor específico, caso o mercado faça um "pico" falso e você queira manter a referência anterior?**
