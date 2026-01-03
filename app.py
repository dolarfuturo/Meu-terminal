import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Terminal Trading", layout="wide")

st.title("🏦 TERMINAL DE TESTE: SPOT & FUTURO")

# 1. BUSCA DE DADOS (SPOT)
try:
    # Dólar Spot
    dolar_data = yf.download("USDBRL=X", period="2d", interval="1m", progress=False)
    spot = dolar_data['Close'].iloc[-1]
    
    # Cálculo Dólar Futuro (Exemplo com FRP de 15 pontos)
    # Ajuste o valor do frp conforme o mercado
    frp = 0.0150 
    futuro = spot + frp

    st.subheader("💵 Câmbio")
    c1, c2, c3 = st.columns(3)
    c1.metric("DÓLAR SPOT", f"{spot:.4f}")
    c2.metric("FRP (AJUSTE)", f"{frp:.4f}")
    c3.metric("DÓLAR FUTURO", f"{futuro:.4f}")
except:
    st.error("Erro ao carregar dados de Câmbio")

st.divider()

# 2. JUROS E MERCADO (DIs e Variações)
st.subheader("📊 Juros (DI) e Variações")

def card_mercado(coluna, titulo, ticker, is_di=False):
    try:
        df = yf.download(ticker, period="5d", progress=False)
        atual = df['Close'].iloc[-1]
        anterior = df['Close'].iloc[-2]
        variacao = ((atual - anterior) / anterior) * 100
        
        if is_di:
            coluna.metric(titulo, f"{atual:.2f}%", f"{variacao:+.2f}%")
        else:
            coluna.metric(titulo, f"{atual:.2f}", f"{variacao:+.2f}%")
    except:
        coluna.write(f"Carregando {titulo}...")

col_di27, col_di29, col_di31 = st.columns(3)
col_ewz, col_dxy, col_spx = st.columns(3)

# Linha de Juros
card_mercado(col_di27, "DI 2027", "DI1F27.SA", is_di=True)
card_mercado(col_di29, "DI 2029", "DI1F29.SA", is_di=True)
card_mercado(col_di31, "DI 2031", "DI1F31.SA", is_di=True)

st.write("") # Espaçamento

# Linha de Mercado
card_mercado(col_ewz, "EWZ (Ibov USD)", "EWZ")
card_mercado(col_dxy, "DXY (Dólar Global)", "DX-Y.NYB")
card_mercado(col_spx, "S&P 500", "^GSPC")

