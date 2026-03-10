import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(page_title="K97 - VOLATILIDADE", layout="wide")

# --- MOTOR DE CÁLCULO K97 (SUA FÓRMULA) ---
def calcular_limites_k97(eixo_ewz, max_ewz, min_ewz, eixo_dol):
    try:
        # VAR - (Baseada na Máxima do EWZ)
        # (EIXO / MAX - 1) * 100 / 2
        var_negativa = ((eixo_ewz / max_ewz) - 1) * 100 / 2
        
        # VAR + (Baseada na Mínima do EWZ)
        # (EIXO / MIN - 1) * 100 / 2
        var_positiva = ((eixo_ewz / min_ewz) - 1) * 100 / 2
        
        # PROJEÇÕES DOLFUT
        alvo_baixo = eixo_dol * (1 + (var_negativa / 100))
        alvo_cima = eixo_dol * (1 + (var_positiva / 100))
        
        return alvo_cima, alvo_baixo, var_positiva, var_negativa
    except:
        return eixo_dol, eixo_dol, 0.0, 0.0

# --- CAPTURA DE DADOS EM TEMPO REAL ---
@st.cache_data(ttl=2)
def fetch_ewz_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        if not df.empty:
            return {
                "atual": df['Close'].iloc[-1],
                "max": df['High'].max(),
                "min": df['Low'].min()
            }
    except: return None

# --- ESTILO VISUAL ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .metric-val { font-size: 45px; font-family: 'Arial Black'; font-weight: 900; line-height: 1; }
    .frame-box { border: 2px solid #3d444d; padding: 20px; background: #161b22; border-radius: 4px; text-align: center; }
    .label-k97 { color: #00f2ff; font-weight: bold; font-size: 14px; margin-bottom: 10px; }
</style>""", unsafe_allow_html=True)

st.title("K97 - PROJEÇÃO DE MÁX/MÍN")

# --- ENTRADAS MANUAIS ---
with st.sidebar:
    st.header("⚙️ CALIBRAÇÃO")
    eixo_ewz_manual = st.number_input("EIXO EWZ (FIXO):", value=35.70, format="%.2f")
    eixo_dol_manual = st.number_input("EIXO DOLFUT:", value=5295.50, format="%.2f")

# Execução
data = fetch_ewz_data()

if data:
    cima, baixo, v_pos, v_neg = calcular_limites_k97(eixo_ewz_manual, data["max"], data["min"], eixo_dol_manual)
    
    # Painel EWZ (Referência)
    st.subheader("📊 MONITORAMENTO EWZ (REAL-TIME)")
    c1, c2, c3 = st.columns(3)
    c1.metric("MÍNIMA EWZ", f"{data['min']:.2f}")
    c2.metric("PREÇO ATUAL", f"{data['atual']:.2f}")
    c3.metric("MÁXIMA EWZ", f"{data['max']:.2f}")

    st.markdown("---")

    # Painel DOLFUT (Projeção baseada na sua fórmula)
    st.subheader("🎯 ALVOS SINTÉTICOS (DOLFUT)")
    res_col, sup_col = st.columns(2)

    with res_col:
        st.markdown('<div class="frame-box" style="border-top: 4px solid #ff4d4d;">', unsafe_allow_html=True)
        st.markdown('<div class="label-k97">DÓLAR NA MÍNIMA DO EWZ (RESISTÊNCIA)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val" style="color:#ff4d4d;">{cima:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:bold;">Var: {v_pos:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with sup_col:
        st.markdown('<div class="frame-box" style="border-top: 4px solid #00ff88;">', unsafe_allow_html=True)
        st.markdown('<div class="label-k97">DÓLAR NA MÁXIMA DO EWZ (SUPORTE)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-val" style="color:#00ff88;">{baixo:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:bold;">Var: {v_neg:+.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Preço Justo de Agora (Para comparar)
    var_agora = ((eixo_ewz_manual / data["atual"]) - 1) * 100 / 2
    justo_agora = eixo_dol_manual * (1 + (var_agora / 100))
    st.info(f"Dólar Sintético Atual: {justo_agora:.2f} (Variação: {var_agora:+.2f}%)")

else:
    st.error("Buscando dados do mercado...")

time.sleep(2)
st.rerun()
