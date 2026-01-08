import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Terminal Spot/Futuro", layout="wide")

st.title("📟 Terminal Macro: Projeção de Futuros")

# --- SIDEBAR: ENTRADA DE VARIÁVEIS (PONTOS) ---
st.sidebar.header("⚙️ Ajustes de Pontos")
st.sidebar.write("Defina os pontos para somar ao Spot:")

# Campos de entrada editáveis (Padrão: 22, 31, 42)
v1 = st.sidebar.number_input("Variável A (Pontos)", value=22.0, step=0.5)
v2 = st.sidebar.number_input("Variável B (Pontos)", value=31.0, step=0.5)
v3 = st.sidebar.number_input("Variável C (Pontos)", value=42.0, step=0.5)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        # 2 dias para garantir o fechamento e o preço atual
        df = t.history(period="2d", interval="1m")
        return df
    except:
        return pd.DataFrame()

# --- COLETA DE DADOS ---
spot_df = get_data("BRL=X")
dxy_df = get_data("DX-Y.NYB")
ewz_df = get_data("EWZ")

if not spot_df.empty:
    # 1. Dados Dólar Spot
    spot_atual = spot_df['Close'].iloc[-1]
    # No yfinance, o primeiro dado de um período de 2 dias representa o fechamento anterior (referência 16h)
    spot_fech_16h = spot_df['Close'].iloc[0] 
    var_spot = ((spot_atual - spot_fech_16h) / spot_fech_16h) * 100

    # --- LINHA 1: DASHBOARD DE COTAÇÕES ---
    col_spot, col_dxy, col_ewz = st.columns(3)

    with col_spot:
        st.subheader("📍 Dólar Spot")
        st.metric("Preço Atual", f"R$ {spot_atual:.4f}", f"{var_spot:.2f}%")
        st.caption(f"Fechamento 16h: {spot_fech_16h:.4f}")

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
            st.caption(f"Fechamento Ant: {ewz_f:.2f}")

    st.divider()

    # --- LINHA 2: PROJEÇÕES DE FUTURO (SPOT + VARIÁVEIS) ---
    st.subheader("🔮 Projeções de Dólar Futuro")
    f1, f2, f3 = st.columns(3)

    # Cálculo: Preço do Spot + (Pontos / 1000)
    # Exemplo: Se Spot é 5.0000 e Var é 22.0, o futuro é 5.0220
    fut1 = spot_atual + (v1 / 1000)
    fut2 = spot_atual + (v2 / 1000)
    fut3 = spot_atual + (v3 / 1000)

    with f1:
        st.info(f"**Futuro (Spot + {v1})**")
        st.markdown(f"## R$ {fut1:.4f}")
    
    with f2:
        st.info(f"**Futuro (Spot + {v2})**")
        st.markdown(f"## R$ {fut2:.4f}")

    with f3:
        st.info(f"**Futuro (Spot + {v3})**")
        st.markdown(f"## R$ {fut3:.4f}")

else:
    st.error("Não foi possível carregar os dados do Spot.")

# Botão de atualização
if st.sidebar.button('🔄 Atualizar Terminal'):
    st.rerun()
