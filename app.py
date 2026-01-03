import streamlit as st
import yfinance as yf

# Configuração básica
st.set_page_config(page_title="Terminal Pro", layout="wide")
st.title("🏦 TERMINAL DE CÂMBIO")

# 1. DADOS DO DÓLAR (O que já estava funcionando)
try:
    # Busca o preço atual do Dólar
    dolar = yf.download("USDBRL=X", period="1d", interval="1m", progress=False)
    preco_atual = dolar['Close'].iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("DÓLAR SPOT", f"R$ {preco_atual:.4f}")
    col2.metric("DÓLAR JUSTO", f"R$ {preco_atual * 1.0003:.4f}")
    col3.metric("PTAX EST.", f"R$ {preco_atual * 1.0001:.4f}")
except:
    st.error("Erro ao carregar Dólar")

st.divider()

# 2. VARIAÇÕES DO MERCADO (Simples e direto)
st.subheader("📊 Variações (Fechamento)")

def buscar_ativo(label, ticker):
    try:
        # Busca 5 dias para garantir dados de fim de semana
        dados = yf.download(ticker, period="5d", progress=False)
        fechamento_hoje = dados['Close'].iloc[-1]
        fechamento_ontem = dados['Close'].iloc[-2]
        variacao = ((fechamento_hoje - fechamento_ontem) / fechamento_ontem) * 100
        st.metric(label, f"{fechamento_hoje:.2f}", f"{variacao:+.2f}%")
    except:
        st.write(f"Aguardando {label}...")

c1, c2, c3 = st.columns(3)
with c1:
    buscar_ativo("EWZ (Bolsa BR)", "EWZ")
with c2:
    buscar_ativo("DXY (Dólar Global)", "DX-Y.NYB")
with c3:
    buscar_ativo("S&P 500", "^GSPC")
