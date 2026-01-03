import streamlit as st
import yfinance as yf

# 1. Configuração de Estilo Profissional
st.set_page_config(page_title="Terminal Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #ffffff; }
    div[data-testid="stMetricDelta"] { font-size: 18px; }
    .stDivider { border-bottom: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# Barra Lateral para Ajustes
with st.sidebar:
    st.title("⚙️ Painel de Controle")
    frp_ajuste = st.number_input("Ajuste FRP", value=0.0150, format="%.4f", step=0.0001)
    st.info("O FRP é somado ao Dólar Spot para calcular o Futuro.")

st.title("🏦 TERMINAL DE MERCADO")

# 2. BLOCO DE CÂMBIO (SPOT E FUTURO)
try:
    dolar_raw = yf.download("USDBRL=X", period="5d", interval="1m", progress=False)
    if not dolar_raw.empty:
        spot = float(dolar_raw['Close'].iloc[-1])
        futuro = spot + frp_ajuste
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("DÓLAR SPOT", f"R$ {spot:.4f}")
        with c2:
            st.metric("FRP ATUAL", f"{frp_ajuste:.4f}")
        with c3:
            st.metric("DÓLAR FUTURO", f"R$ {futuro:.4f}")
except:
    st.error("Erro ao carregar dados de câmbio.")

st.divider()

# 3. FUNÇÃO DE VARIAÇÃO ROBUSTA
def card_ativo(coluna, titulo, ticker, is_percent=False):
    try:
        # Puxamos 7 dias para garantir dados de sexta/quinta no fim de semana
        df = yf.download(ticker, period="7d", interval="1d", progress=False)
        if len(df) >= 2:
            atual = df['Close'].iloc[-1]
            anterior = df['Close'].iloc[-2]
            variacao = ((atual - anterior) / anterior) * 100
            
            simbolo = "%" if is_percent else ""
            coluna.metric(titulo, f"{atual:.2f}{simbolo}", f"{variacao:+.2f}%")
        else:
            coluna.info(f"{titulo}: Sem sinal")
    except:
        coluna.error(f"{titulo}: Offline")

st.subheader("📊 Ativos Globais e Juros")
col_ewz, col_dxy, col_spx = st.columns(3)
col_di27, col_di29, col_di31 = st.columns(3)

# Linha 1: Mercado Global
card_ativo(col_ewz, "EWZ (Bolsa BR)", "EWZ")
card_ativo(col_dxy, "DXY (Dólar Global)", "DX-Y.NYB")
card_ativo(col_spx, "S&P 500", "^GSPC")

st.write("") # Espaçamento

# Linha 2: Juros (DIs)
card_ativo(col_di27, "DI 2027", "DI1F27.SA", is_percent=True)
card_ativo(col_di29, "DI 2029", "DI1F29.SA", is_percent=True)
card_ativo(col_di31, "DI 2031", "DI1F31.SA", is_percent=True)

st.caption("⚠️ Dados de variação baseados no último fechamento disponível.")

