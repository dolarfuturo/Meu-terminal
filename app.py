import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Terminal Trading", layout="wide")
st.title("🏦 MONITOR DE MERCADO")

# 1. CÂMBIO (SPOT E FUTURO)
try:
    # Busca dólar com histórico de 1 dia para garantir que venha algo
    df_dolar = yf.download("USDBRL=X", period="1d", interval="1m", progress=False)
    
    if not df_dolar.empty:
        spot = float(df_dolar['Close'].iloc[-1])
        frp = 0.0150 
        futuro = spot + frp

        c1, c2, c3 = st.columns(3)
        c1.metric("DÓLAR SPOT", f"{spot:.4f}")
        c2.metric("FRP (AJUSTE)", f"{frp:.4f}")
        c3.metric("DÓLAR FUTURO", f"{futuro:.4f}")
except:
    st.error("Erro na conexão de câmbio")

st.markdown("---")

# 2. JUROS E VARIÇÕES (Ajustado para Sábado)
st.subheader("📊 Juros e Mercado")

def buscar_estavel(label, ticker, sufixo=""):
    try:
        # Aumentamos para 7 dias para garantir o fechamento de sexta
        df = yf.download(ticker, period="7d", interval="1d", progress=False)
        if not df.empty and len(df) >= 2:
            atual = df['Close'].iloc[-1]
            anterior = df['Close'].iloc[-2]
            variacao = ((atual - anterior) / anterior) * 100
            st.metric(label, f"{atual:.2f}{sufixo}", f"{variacao:+.2f}%")
        else:
            st.write(f"OFFLINE: {label}")
    except:
        st.write(f"Erro: {label}")

col1, col2, col3 = st.columns(3)
with col1:
    buscar_estavel("DI 2027", "DI1F27.SA", "%")
    buscar_estavel("EWZ (Bolsa)", "EWZ")
with col2:
    buscar_estavel("DI 2029", "DI1F29.SA", "%")
    buscar_estavel("DXY (Dólar)", "DX-Y.NYB")
with col3:
    buscar_estavel("DI 2031", "DI1F31.SA", "%")
    buscar_estavel("S&P 500", "^GSPC")

