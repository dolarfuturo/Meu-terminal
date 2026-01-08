import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Terminal Spot to Future", layout="wide")

st.title("📟 Terminal: Projeção de Dólar Futuro")

# --- SIDEBAR: ENTRADA DE VARIÁVEIS (SPREADS) ---
st.sidebar.header("⚙️ Ajustes (Spread)")
st.sidebar.write("Defina os pontos para somar ao Spot:")

# Campos de entrada editáveis
v1 = st.sidebar.number_input("Variável A (Pontos)", value=22.0)
v2 = st.sidebar.number_input("Variável B (Pontos)", value=31.0)
v3 = st.sidebar.number_input("Variável C (Pontos)", value=42.0)

def get_data(ticker):
    try:
        # Puxa dados de 2 dias com intervalo de 1 minuto para precisão
        t = yf.Ticker(ticker)
        df = t.history(period="2d", interval="1m")
        return df
    except:
        return pd.DataFrame()

# --- COLETA DE DADOS ---
spot_df = get_data("BRL=X")
dxy_df = get_data("DX-Y.NYB")
ewz_df = get_data("EWZ")

if not spot_df.empty:
    # 1. Cálculos do Dólar Spot
    spot_atual = spot_df['Close'].iloc[-1]
    spot_fech_16h = spot_df['Close'].iloc[0] # Ref fechamento anterior
    var_spot = ((spot_atual - spot_fech_16h) / spot_fech_16h) * 100

    # 2. CÁLCULO DO FUTURO (Spot + Variáveis)
    # Aqui somamos as variáveis ao preço atual do Spot
    futuro_projetado = spot_atual + ((v1 + v2 + v3) / 1000) # Exemplo: 22 pontos = 0.022

    # --- LINHA 1: SPOT VS FUTURO PROJETADO ---
    col_spot, col_futuro = st.columns(2)

    with col_spot:
        st.subheader("📍 Dólar Spot (Base)")
        st.metric("Preço Atual", f"R$ {spot_atual:.4f}", f"{var_spot:.2f}%")
        st.caption(f"Fechamento 16h: {spot_fech_16h:.4f}")

    with col_futuro:
        st.markdown(f"""
            <div style="background-color:#1E2630; padding:20px; border-radius:10px; border-left: 8px solid #FFC107;">
                <h3 style="margin:0; color:#FFC107;">🔮 Futuro Projetado</h3>
                <h1 style="margin:0;">R$ {futuro_projetado:.4f}</h1>
                <p style="margin:0; opacity:0.8;">Spot + Ajuste Médio ({v1}, {v2}, {v3})</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- LINHA 2: MACRO (DXY E EWZ) ---
    c1, c2, c3 = st.columns(3)

    with c1:
        if not dxy_df.empty:
            dxy_at = dxy_df['Close'].iloc[-1]
            dxy_f = dxy_df['Close'].iloc[0]
            var_dxy = ((dxy_at - dxy_f) / dxy_f) * 100
            st.metric("DXY Index", f"{dxy_at:.2f}", f"{var_dxy:.2f}%")
            st.caption("Ref. 16h")

    with c2:
        if not ewz_df.empty:
            ewz_at = ewz_df['Close'].iloc[-1]
            ewz_f = ewz_df['Close'].iloc[0] # Fechamento anterior
            var_ewz = ((ewz_at - ewz_f) / ewz_f) * 100
            st.metric("EWZ ETF", f"US$ {ewz_at:.2f}", f"{var_ewz:.2f}%")
            st.caption("Fechamento Anterior NY")
            
    with c3:
        st.write("**Resumo dos Ajustes:**")
        st.write(f"Soma Total: `{(v1+v2+v3):.1f}` pontos")

else:
    st.error("Dados do Spot indisponíveis no momento.")

# Refresh
if st.sidebar.button('🔄 Atualizar Terminal'):
    st.rerun()
