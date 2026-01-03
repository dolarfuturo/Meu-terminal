import streamlit as st
import yfinance as yf
import pandas as pd

# Função robusta que tenta buscar dados de duas formas
def busca_segura(ticker):
    try:
        # Tenta a busca padrão
        df = yf.download(ticker, period="5d", interval="1d", progress=False)
        if not df.empty:
            return df
    except:
        try:
            # Tenta uma busca via Ticker object (servidor secundário)
            t = yf.Ticker(ticker)
            df = t.history(period="5d")
            return df
        except:
            return None

st.write("### Painel de Variações (Multifonte)")
c1, c2, c3 = st.columns(3)

# Lista para processar
ativos = [("EWZ", "EWZ"), ("DXY", "DX-Y.NYB"), ("S&P 500", "^GSPC")]
cols = [c1, c2, c3]

for i, (nome, simbolo) in enumerate(ativos):
    dados = busca_segura(simbolo)
    if dados is not None and len(dados) >= 2:
        atual = dados['Close'].iloc[-1]
        anterior = dados['Close'].iloc[-2]
        var = ((atual - anterior) / anterior) * 100
        cols[i].metric(nome, f"{atual:.2f}", f"{var:+.2f}%")
    else:
        cols[i].error(f"{nome} indisponível")
