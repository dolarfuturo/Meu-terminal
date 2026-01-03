
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Mesa de Câmbio", layout="wide")
st.title("🏦 TERMINAL PROFISSIONAL")

# Ativos
tickers = {"DÓLAR": "USDBRL=X", "EWZ": "EWZ", "DXY": "DX-Y.NYB", "DI 27": "DI1F27.SA", "DI 31": "DI1F31.SA"}

try:
    data = yf.download(list(tickers.values()), period="2d", interval="1d", progress=False)['Close']
    spot = data["USDBRL=X"].iloc[-1]
    
    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("DÓLAR SPOT", f"{spot:.4f}")
    c2.metric("DÓLAR JUSTO", f"{spot * 1.0003:.4f}") # Cálculo Simples
    c3.metric("PTAX EST.", f"{spot * 1.0002:.4f}")

    # Tabela
    st.table(data.T.iloc[:, -1:])
except:
    st.write("Conectando aos dados...")
