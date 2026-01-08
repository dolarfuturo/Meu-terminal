import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Terminal Dólar Justo", layout="wide")

st.title("📊 Terminal Macro: Cálculo de Dólar Justo")

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("⚙️ Parâmetros do Justo")
st.sidebar.write("Ajuste os níveis para o cálculo:")

# Campos de entrada para as variáveis (Padrão: 22, 31, 42)
v1 = st.sidebar.number_input("Variável 1", value=22.0, step=1.0)
v2 = st.sidebar.number_input("Variável 2", value=31.0, step=1.0)
v3 = st.sidebar.number_input("Variável 3", value=42.0, step=1.0)

# Cálculo do Dólar Justo (Exemplo: Média das variáveis)
# Se suas variáveis forem 'pontos', somamos à base do preço ou tiramos a média
preco_justo_base = (v1 + v2 + v3) / 3

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="2d", interval="1m")
        return df
    except:
        return pd.DataFrame()

# --- BUSCA DE DADOS ---
spot_df = get_data("BRL=X")
dxy_df = get_data("DX-Y.NYB")
ewz_df = get_data("EWZ")

if not spot_df.empty:
    # 1. Dados Dólar Spot
    spot_atual = spot_df['Close'].iloc[-1]
    spot_fech_16h = spot_df['Close'].iloc[0] # Referência de fechamento anterior
    var_spot = ((spot_atual - spot_fech_16h) / spot_fech_16h) * 100

    # --- LINHA 1: DESTAQUE DÓLAR JUSTO VS SPOT ---
    col_justo, col_spot = st.columns(2)

    with col_justo:
        st.markdown(f"""
            <div style="background-color:#1E2630; padding:20px; border-radius:10px; border-left: 8px solid #00FFAA;">
                <h3 style="margin:0;">🎯 Dólar Justo (Calculado)</h3>
                <h1 style="color:#00FFAA; margin:0;">{preco_justo_base:.2f}</h1>
                <p style="margin:0; opacity:0.8;">Média das variáveis: {v1}, {v2}, {v3}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_spot:
        st.subheader("📍 Dólar Spot")
        st.metric("Preço Atual", f"R$ {spot_atual:.4f}", f"{var_spot:.2f}%")
        st.caption(f"Fechamento Ref. 16h: {spot_fech_16h:.4f}")

    st.divider()

    # --- LINHA 2: DXY E EWZ ---
    col_dxy, col_ewz, col_vars = st.columns([1, 1, 1])

    with col_dxy:
        if not dxy_df.empty:
            dxy_at = dxy_df['Close'].iloc[-1]
            dxy_f = dxy_df['Close'].iloc[0]
            var_dxy = ((dxy_at - dxy_f) / dxy_f) * 100
            st.metric("DXY Index", f"{dxy_at:.2f}", f"{var_dxy:.2f}%")
            st.caption(f"Ref. 16h: {dxy_f:.2f}")

    with col_ewz:
        if not ewz_df.empty:
            ewz_at = ewz_df['Close'].iloc[-1]
            ewz_f = ewz_df['Close'].iloc[0] # Fechamento anterior
            var_ewz = ((ewz_at - ewz_f) / ewz_f) * 100
            st.metric("EWZ ETF", f"US$ {ewz_at:.2f}", f"{var_ewz:.2f}%")
            st.caption(f"Fechamento Anterior: {ewz_f:.2f}")
            
    with col_vars:
        st.write("**Variáveis Ativas:**")
        st.code(f"V1: {v1} | V2: {v2} | V3: {v3}")

else:
    st.error("Erro ao conectar com Yahoo Finance. Verifique a conexão.")

# Botão de refresh
if st.sidebar.button('🔄 Atualizar Agora'):
    st.rerun()
