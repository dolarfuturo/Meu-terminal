import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Terminal Spot Macro", layout="wide")

st.title("📟 Terminal de Monitoramento: Foco Spot")

# --- SIDEBAR: AJUSTE DE VARIÁVEIS ---
st.sidebar.header("Configurações de Níveis")
st.sidebar.write("Ajuste as variáveis fixas do Spot:")

# Campos de entrada com os valores padrão 22, 31, 42
var_a = st.sidebar.number_input("Variável A", value=22)
var_b = st.sidebar.number_input("Variável B", value=31)
var_c = st.sidebar.number_input("Variável C", value=42)

def get_data(ticker, interval="1m"):
    try:
        t = yf.Ticker(ticker)
        # 2 dias para garantir o fechamento anterior e o preço atual
        df = t.history(period="2d", interval=interval)
        return df
    except:
        return pd.DataFrame()

# --- PROCESSAMENTO DOS DADOS ---
dolar_spot_df = get_data("BRL=X")
dxy_df = get_data("DX-Y.NYB")
ewz_df = get_data("EWZ")
dolar_fut_df = get_data("BZ=F", interval="1d") # Futuro diário para variação

if not dolar_spot_df.empty:
    # Lógica Dólar Spot
    spot_atual = dolar_spot_df['Close'].iloc[-1]
    # Referência de fechamento (último valor do dia anterior ou primeiro do dia)
    spot_fech_16h = dolar_spot_df['Close'].iloc[0] 
    var_spot = ((spot_atual - spot_fech_16h) / spot_fech_16h) * 100

    # --- LINHA 1: BLOCO PRINCIPAL (SPOT E VARIÁVEIS) ---
    col_main, col_vars = st.columns([2, 2])

    with col_main:
        st.subheader("📍 Dólar Spot")
        c1, c2 = st.columns(2)
        c1.metric("Preço Atual", f"{spot_atual:.4f}", f"{var_spot:.2f}%")
        c2.metric("Ref. Fechamento", f"{spot_fech_16h:.4f}")

    with col_vars:
        st.subheader("🎯 Níveis de Referência (Editáveis)")
