import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Terminal Trading", layout="wide")
st.title("🏦 MONITOR DE MERCADO")

# 1. BUSCA DE DADOS (Dólar e Futuro)
try:
    # Busca o dólar spot
    df_dolar = yf.download("USDBRL=X", period="1d", interval="1m", progress=False)
    
    # Verifica se o dado chegou corretamente
    if not df_dolar.empty:
        spot = float(df_dolar['Close'].iloc[-1])
        
        # Cálculo Dólar Futuro (ajuste manual de FRP para teste)
        frp = 0.0150 
        futuro = spot + frp

        c1, c2, c3 = st.columns(3)
        c1.metric("DÓLAR SPOT", f"{spot:.4f}")
        c2.metric("FRP (AJUSTE)", f"{frp:.4f}")
        c3.metric("DÓLAR FUTURO", f"{futuro:.4f}")
    else:
        st.warning("Aguardando cotação do dólar...")
except:
    st.error("Erro na conexão com o câmbio.")

st.divider()

# 2. JUROS (DIs) E VARIAÇÕES
st.subheader("📊 Juros e Mercado")

def buscar_ativo(label, ticker, sufixo=""):
    try:
        dados = yf.download(ticker, period="5d", progress=False)
        if not dados.empty:
            atual = dados['Close'].iloc[-1]
            anterior = dados['Close'].iloc[-2]
            variacao = ((atual - anterior) / anterior) * 100
            st.metric(label, f"{atual:.2f}{sufixo}", f"{variacao:+.2f}%")
        else:
            st.write(f"Buscando {label}...")
    except:
        st.write(f"Indisponível: {label}")

# Colunas para DIs e Varições
col1, col2, col3 = st.columns(3)
with col1:
    buscar_ativo("DI 2027", "DI1F27.SA", "%")
    buscar_ativo("EWZ (Bolsa)", "EWZ")
with col2:
    buscar_ativo("DI 2029", "DI1F29.SA", "%")
    buscar_ativo("DXY (Dólar Global)", "DX-Y.NYB")
with col3:
    buscar_ativo("DI 2031", "DI1F31.SA", "%")
    buscar_ativo("S&P 500", "^GSPC")

