import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Terminal", layout="wide")
st.title("🏦 TERMINAL PROFISSIONAL")

# Bloco do Dólar (O que já funciona)
try:
    dolar_data = yf.download("USDBRL=X", period="1d", interval="1m", progress=False)
    spot = dolar_data['Close'].iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("DÓLAR SPOT", f"{spot:.4f}")
    c2.metric("DÓLAR JUSTO", f"{spot * 1.0003:.4f}")
    c3.metric("PTAX EST.", f"{spot * 1.0001:.4f}")
except:
    st.write("Carregando Dólar...")

st.markdown("---")

# Bloco das Variações (O que estava travado)
st.write("### Variações do Mercado")
col1, col2, col3 = st.columns(3)

def buscar_v(label, ticker, coluna):
    try:
        # Busca 5 dias para garantir dados de fechamento no fim de semana
        df = yf.download(ticker, period="5d", interval="1d", progress=False)
        atual = df['Close'].iloc[-1]
        anterior = df['Close'].iloc[-2]
        var = ((atual - anterior) / anterior) * 100
        coluna.metric(label, f"{atual:.2f}", f"{var:+.2f}%")
    except:
        coluna.write(f"Erro em {label}")

buscar_v("EWZ (Bolsa BR)", "EWZ", col1)
buscar_v("DXY (Dólar Global)", "DX-Y.NYB", col2)
buscar_v("S&P 500", "^GSPC", col3)
