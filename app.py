import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Terminal Trading", layout="wide")

# Barra lateral para o ajuste do FRP
with st.sidebar:
    st.header("⚙️ Ajustes")
    frp_manual = st.number_input("Ajuste FRP", value=0.0150, format="%.4f", step=0.0001)

st.title("🏦 MONITOR DE MERCADO")

# 1. CÂMBIO (SPOT E FUTURO)
try:
    # Busca 3 dias para garantir dados de fechamento no fim de semana
    df_dolar = yf.download("USDBRL=X", period="3d", interval="1m", progress=False)
    if not df_dolar.empty:
        spot = float(df_dolar['Close'].iloc[-1])
        futuro = spot + frp_manual
        c1, c2, c3 = st.columns(3)
        c1.metric("DÓLAR SPOT", f"{spot:.4f}")
        c2.metric("FRP (ATUAL)", f"{frp_manual:.4f}")
        c3.metric("DÓLAR FUTURO", f"{futuro:.4f}")
except:
    st.error("Erro ao carregar Câmbio")

st.divider()

# 2. FUNÇÃO PARA BUSCAR ÚLTIMO FECHAMENTO E VARIAÇÃO
def mostrar_mercado(label, ticker, sufixo=""):
    try:
        # Puxamos 7 dias para garantir que pegamos sexta e quinta-feira
        df = yf.download(ticker, period="7d", interval="1d", progress=False)
        if len(df) >= 2:
            fechamento_atual = df['Close'].iloc[-1]
            fechamento_anterior = df['Close'].iloc[-2]
            variacao = ((fechamento_atual - fechamento_anterior) / fechamento_anterior) * 100
            st.metric(label, f"{fechamento_atual:.2f}{sufixo}", f"{variacao:+.2f}%")
        else:
            st.write(f"⏳ {label}: Sem dados")
    except:
        st.write(f"❌ {label}: Indisponível")

st.subheader("📊 Juros e Ativos (Último Fechamento)")
col1, col2, col3 = st.columns(3)

with col1:
    mostrar_mercado("DI 2027", "DI1F27.SA", "%")
    mostrar_mercado("EWZ (Bolsa BR)", "EWZ")
with col2:
    mostrar_mercado("DI 2029", "DI1F29.SA", "%")
    mostrar_mercado("DXY (Dólar Global)", "DX-Y.NYB")
with col3:
    mostrar_mercado("DI 2031", "DI1F31.SA", "%")
    mostrar_mercado("S&P 500", "^GSPC")

st.caption("Nota: Dados baseados no último fechamento útil disponível.")

