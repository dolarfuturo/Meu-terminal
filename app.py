import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Terminal Trading", layout="wide", initial_sidebar_state="collapsed")

# Título e Controle de Ajuste Manual
st.title("🏦 MONITOR DE MERCADO")

# Criamos uma barra lateral para você ajustar o FRP sem mexer no código
with st.sidebar:
    st.header("⚙️ Ajustes")
    frp_manual = st.number_input("Ajuste FRP", value=0.0150, format="%.4f", step=0.0001)

# 1. CÂMBIO (SPOT E FUTURO)
try:
    # Busca o dólar (periodo de 3 dias para garantir dados de sexta-feira)
    df_dolar = yf.download("USDBRL=X", period="3d", interval="1m", progress=False)
    
    if not df_dolar.empty:
        spot = float(df_dolar['Close'].iloc[-1])
        futuro = spot + frp_manual

        c1, c2, c3 = st.columns(3)
        c1.metric("DÓLAR SPOT", f"{spot:.4f}")
        c2.metric("FRP (ATUAL)", f"{frp_manual:.4f}")
        c3.metric("DÓLAR FUTURO", f"{futuro:.4f}")
except:
    st.error("Conexão com Câmbio instável no fim de semana.")

st.markdown("---")

# 2. JUROS E VARIÇÕES (Lógica para buscar sempre o último fechamento útil)
st.subheader("📊 Juros e Mercado (Último Fechamento)")

def buscar_dados(label, ticker, sufixo=""):
    try:
        # Puxamos 7 dias para pular o fim de semana com segurança
        data = yf.download(ticker, period="7d", interval="1d", progress=False)
        if not data.empty:
            fechamento = data['Close'].iloc[-1]
            # Se for sábado/domingo, o Yahoo pode repetir o último dia ou dar erro
            st.metric(label, f"{fechamento:.2f}{sufixo}")
        else:
            st.write(f"⏳ {label}: Aguardando abertura")
    except:
        st.write(f"❌ {label}: Indisponível")

col1, col2, col3 = st.columns(3)
with col1:
    buscar_dados("DI 2027", "DI1F27.SA", "%")
    buscar_dados("EWZ (Bolsa)", "EWZ")
with col2:
    buscar_dados("DI 2029", "DI1F29.SA", "%")
    buscar_dados("DXY (Dólar)", "DX-Y.NYB")
with col3:
    buscar_dados("DI 2031", "DI1F31.SA", "%")
    buscar_dados("S&P 500", "^GSPC")

st.caption("Nota: Aos fins de semana, os dados refletem o fechamento de sexta-feira.")

