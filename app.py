import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Terminal", layout="wide")

st.title("🏦 MONITOR DE TESTE")

# Função de busca ultra-rápida
@st.cache_data(ttl=60)
def carregar_dados(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        return df['Close'].iloc[-1]
    except:
        return None

# Execução
spot = carregar_dados("USDBRL=X")

if spot:
    c1, c2, c3 = st.columns(3)
    c1.metric("DÓLAR SPOT", f"{spot:.4f}")
    c2.metric("FUTURO (EST)", f"{spot + 0.0150:.4f}")
    c3.metric("DI 27", "12.80%") # Valor manual para teste
    
    st.success("Sistema conectado com sucesso!")
else:
    st.warning("Buscando dados no servidor... Se demorar, clique em Reboot.")

