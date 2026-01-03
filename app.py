import streamlit as st
import yfinance as yf

st.title("🏦 MONITOR DE CÂMBIO")

# Lista simplificada
ativos = ["USDBRL=X", "EWZ", "DX-Y.NYB", "DI1F27.SA"]

# Botão de atualizar manual
if st.button('ATUALIZAR DADOS'):
    data = yf.download(ativos, period="2d", interval="1d")['Close']
    st.write("### Cotações Atuais")
    st.dataframe(data.iloc[-1])
    
    spot = data["USDBRL=X"].iloc[-1]
    st.metric("DÓLAR JUSTO", f"{spot * 1.0003:.4f}")
else:
    st.write("Clique no botão acima para carregar.")
