import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Terminal de Câmbio High-Low", layout="wide")

# Customização de CSS para visual de terminal (fundo escuro e fontes claras)
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

def get_market_data(ticker):
    t = yf.Ticker(ticker)
    # Buscamos 2 dias com intervalo de 1h para garantir o dado das 16h/Fechamento
    df = t.history(period="2d", interval="1h")
    return df

st.title("📟 Terminal de Monitoramento Macro")

try:
    # --- Coleta de Dados ---
    dolar_spot = get_market_data("BRL=X")
    dxy = get_market_data("DX-Y.NYB")
    ewz = get_market_data("EWZ")
    dolar_fut = get_market_data("BZ=F") # Dólar Futuro Contínuo

    # --- Processamento ---
    def calc_metrics(df):
        atual = df['Close'].iloc[-1]
        fechamento = df['Close'].iloc[0] # Referência do início do período (ajuste)
        variacao = ((atual - fechamento) / fechamento) * 100
        return atual, fechamento, variacao

    # --- LAYOUT DE COLUNAS ---
    col1, col2, col3, col4 = st.columns(4)

    # Dólar Spot
    val_spot, fech_spot, var_spot = calc_metrics(dolar_spot)
    with col1:
        st.subheader("Dólar Spot")
        st.metric("Atual", f"{val_spot:.4f}", f"{var_spot:.2f}%")
        st.caption(f"Ref. 16h: {fech_spot:.4f}")

    # DXY
    val_dxy, fech_dxy, var_dxy = calc_metrics(dxy)
    with col2:
        st.subheader("DXY Index")
        st.metric("Atual", f"{val_dxy:.2f}", f"{var_dxy:.2f}%")
        st.caption(f"Ref. 16h: {fech_dxy:.2f}")

    # EWZ (MSCI Brazil)
    val_ewz, fech_ewz, var_ewz = calc_metrics(ewz)
    with col3:
        st.subheader("EWZ (ETF)")
        st.metric("Atual", f"US$ {val_ewz:.2f}", f"{var_ewz:.2f}%")
        st.caption(f"Ant: {fech_ewz:.2f}")

    # Dólar Futuro
    val_fut, fech_fut, var_fut = calc_metrics(dolar_fut)
    with col4:
        st.subheader("Dólar Futuro")
        st.metric("Atual", f"{val_fut:.2f}", f"{var_fut:.2f}%")
        st.caption(f"Ref: {fech_fut:.2f}")

    st.divider()

    # --- SET DE VARIÁVEIS FIXAS ---
    st.write("### 📌 Níveis de Referência (Fixos)")
    v_col1, v_col2, v_col3, v_empty = st.columns([1, 1, 1, 3])
    
    v_col1.metric("Variável A", "22")
    v_col2.metric("Variável B", "31")
    v_col3.metric("Variável C", "42")

except Exception as e:
    st.error(f"Erro na atualização: {e}")

st.divider()
if st.button('🔄 Recarregar Dados'):
    st.rerun()
