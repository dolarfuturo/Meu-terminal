import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Terminal Pro", layout="wide")

st.title("🏦 TERMINAL PROFISSIONAL")

# 1. BLOCO SUPERIOR: DÓLAR E PTAX
try:
    # Busca o dólar atual
    ticker_usd = yf.Ticker("USDBRL=X")
    dados_usd = ticker_usd.history(period="1d")
    spot = dados_usd['Close'].iloc[-1]
    
    # Cálculos automáticos
    justo = spot * 1.0003
    ptax = spot * 1.0001

    c1, c2, c3 = st.columns(3)
    c1.metric("DÓLAR SPOT", f"{spot:.4f}")
    c2.metric("DÓLAR JUSTO", f"{justo:.4f}")
    c3.metric("PTAX EST.", f"{ptax:.4f}")
except:
    st.error("Erro ao carregar dados do Dólar")

st.markdown("---")

# 2. BLOCO DE VARIAÇÕES (CARTÕES RÁPIDOS)
st.write("### Variações do Mercado")

def mostrar_card(label, ticker_simbolo):
    try:
        data = yf.download(ticker_simbolo, period="2d", interval="1d", progress=False)
        atual = data['Close'].iloc[-1]
        anterior = data['Close'].iloc[-2]
        variacao = ((atual - anterior) / anterior) * 100
        st.metric(label, f"{atual:.2f}", f"{variacao:+.2f}%")
    except:
        st.write(f"Aguardando {label}...")

col1, col2, col3 = st.columns(3)

with col1:
    mostrar_card("EWZ (Bolsa BR)", "EWZ")
with col2:
    mostrar_card("DXY (Dólar Global)", "DX-Y.NYB")
with col3:
    mostrar_card("S&P 500", "^GSPC")

st.caption("Dados atualizados via Yahoo Finance")
