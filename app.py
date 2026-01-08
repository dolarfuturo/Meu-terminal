import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página - Estilo Terminal
st.set_page_config(page_title="TERMINAL BLOOMBERG", layout="wide")

# CSS Bloomberg Style - Fundo Preto Total e Nomes em Branco Forte
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] { background-color: #000000; }
    
    /* Nome dos Ativos - Branco Forte */
    [data-testid="stMetricLabel"] { 
        color: #FFFFFF !important; 
        font-size: 16px !important; 
        font-weight: 800 !important; 
        text-transform: uppercase;
    }
    
    /* Valores das Métricas - Amarelo Âmbar */
    [data-testid="stMetricValue"] { 
        color: #FFB900 !important; 
        font-family: 'Courier New', monospace; 
        font-size: 30px !important; 
    }
    
    .frp-box {
        border: 1px solid #333333;
        padding: 15px;
        background-color: #000000;
        border-radius: 5px;
        text-align: center;
    }
    .price-text { font-size: 28px; font-family: 'Courier New'; font-weight: bold; margin-top: 5px; }
    
    /* Tira o padding do topo */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURAÇÕES ---
st.sidebar.title("⌨️ PARÂMETROS")
v_min = st.sidebar.number_input("Mínima FRP (Pts)", value=22.0)
v_justo = st.sidebar.number_input("Justo FRP (Pts)", value=31.0)
v_max = st.sidebar.number_input("Máxima FRP (Pts)", value=42.0)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="2d", interval="1m")
        return df
    except: return pd.DataFrame()

# --- COLETA DE DADOS ---
spot_df = get_data("BRL=X")
dxy_df = get_data("DX-Y.NYB")
ewz_df = get_data("EWZ")

if not spot_df.empty:
    # Spot 16h (Trava) e Spot Atual
    spot_16h = spot_df['Close'].iloc[0] 
    spot_atual = spot_df['Close'].iloc[-1]
    
    # --- LINHA 1: MERCADO GLOBAL ---
    st.markdown("### 📊 DASHBOARD PRINCIPAL")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric("DOLAR SPOT 16H", f"{spot_16h:.4f}")
    
    with c2:
        st.metric("DOLAR SPOT ATUAL", f"{spot_atual:.4f}")

    with c3:
        if not dxy_df.empty:
            dxy_at = dxy_df['Close'].iloc[-1]
            dxy_ref = dxy_df['Close'].iloc[0]
            var_dxy = ((dxy_at - dxy_ref) / dxy_ref) * 100
            st.metric("DXY INDEX", f"{dxy_at:.2f}", f"{var_dxy:.2f}%")

    with c4:
        if not ewz_df.empty:
            ewz_at = ewz_df['Close'].iloc[-1]
            ewz_ref = ewz_df['Close'].iloc[0]
            var_ewz = ((ewz_at - ewz_ref) / ewz_ref) * 100
            st.metric("EWZ (MSCI BRAZIL)", f"{ewz_at:.2f}", f"{var_ewz:.2f}%")

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # --- LINHA 2: PROJEÇÕES FRP (Cores específicas) ---
    st.markdown("### 🔮 PROJEÇÕES DE FUTURO (FRP)")
    
    # Cálculos baseados no Spot Atual
    f_min = spot_atual + (v_min / 1000)
    f_justo = spot_atual + (v_justo / 1000)
    f_max = spot_atual + (v_max / 1000)

    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown(f"""
            <div class="frp-box">
                <span style="color:#FF0000; font-weight:bold; font-size:14px;">MÍNIMA FRP (+{v_min})</span>
                <p class="price-text" style="color:#FF0000;">{f_min:.4f}</p>
            </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown(f"""
            <div class="frp-box">
                <span style="color:#0080FF; font-weight:bold; font-size:14px;">PREÇO JUSTO FRP (+{v_justo})</span>
                <p class="price-text" style="color:#0080FF;">{f_justo:.4f}</p>
            </div>
        """, unsafe_allow_html=True)

    with p3:
        st.markdown(f"""
            <div class="frp-box">
                <span style="color:#00FF00; font-weight:bold; font-size:14px;">MÁXIMA FRP (+{v_max})</span>
                <p class="price-text" style="color:#00FF00;">{f_max:.4f}</p>
            </div>
        """, unsafe_allow_html=True)

# Botão de refresh na lateral
if st.sidebar.button('🔄 REFRESH DATA'):
    st.rerun()
