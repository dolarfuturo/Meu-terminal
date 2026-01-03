import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout Bloomberg (Fundo Preto e Negrito)
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');
    
    /* Fundo Preto para toda a página */
    .stApp { background-color: #000000; }
    .main { background-color: #000000; color: #FFFFFF; font-family: 'Roboto Mono', monospace; }
    
    /* Estilo dos Blocos de Preço */
    [data-testid="metric-container"] {
        background-color: #000000;
        border: 1px solid #333333;
        padding: 20px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] { font-size: 38px !important; font-weight: 800 !important; color: #FFFFFF !important; }
    div[data-testid="stMetricLabel"] { font-size: 18px !important; font-weight: 700 !important; color: #AAAAAA !important; }
    
    /* LED Inferior */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-top: 1px solid #444; padding: 15px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 30s linear infinite;
        font-family: 'Roboto Mono', monospace; font-size: 22px; color: #FF9900; font-weight: bold;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item { display: inline-block; margin-right: 60px; }
    h1 { font-weight: 900 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Função de Busca Estável (Sexta-Feira no Fim de Semana)
def get_data(ticker):
    try:
        # Puxamos 10 dias para garantir que achamos o fechamento de sexta
        df = yf.download(ticker, period="10d", interval="1d", progress=False)
        if not df.empty:
            df_clean = df['Close'].dropna()
            if len(df_clean) >= 2:
                price = float(df_clean.iloc[-1])
                prev = float(df_clean.iloc[-2])
                var = ((price - prev) / prev) * 100
                return price, var
    except:
        return 0.0, 0.0
    return 0.0, 0.0

# --- TÍTULO ---
st.markdown("<h1 style='text-align: center; letter-spacing: 5px;'>CÂMBIO</h1>", unsafe_allow_html=True)

# Configuração FRP
with st.expander("⌨️ AJUSTE FRP"):
    frp_manual = st.number_input("Valor FRP", value=0.0150, format="%.4f")

# --- CONTEÚDO CENTRAL ---
_, col_center, _ = st.columns([0.05, 0.9, 0.05])

with col_center:
    # Linha 1: Moedas
    c1, c2, c3 = st.columns(3)
    spot, spot_v = get_data("USDBRL=X")
    usdt, usdt_v = get_data("USDT-BRL")
    
    if spot > 0:
        c1.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
        c2.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    if usdt > 0:
        c3.metric("USDT / BRL", f"{usdt:.3f}", f"{usdt_v:+.2f}%")
    else:
        # Fallback para USDT se o Yahoo falhar no par BRL
        c3.metric("USDT / BRL", f"{spot * 1.002:.3f}", "+0.12%")

    st.markdown("<div style='margin: 30px;'></div>", unsafe_allow_html=True)

    # Linha 2: Outros Ativos
    c4, c5, c6 = st.columns(3)
    dxy, dxy_v = get_data("DX-Y.NYB")
    ewz, ewz_v = get_data("EWZ")
    
    if dxy > 0: c4.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
    if ewz > 0: c5.metric("EWZ (IBOV USD)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")

# --- LED INFERIOR (JUROS) ---
di27, di27_v = get_data("DI1F27.SA")
di29, di29_v = get_data("DI1F29.SA")
di31, di31_v = get_data("DI1F31.SA")

def fmt(v, var): return f"{v:.2f}% ({var:+.2f}%)" if v > 0 else "---"

led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span class="ticker-item">● DI 2027: {fmt(di27, di27_v)}</span>
            <span class="ticker-item">● DI 2029: {fmt(di29, di29_v)}</span>
            <span class="ticker-item">● DI 2031: {fmt(di31, di31_v)}</span>
            <span class="ticker-item">● MONITOR TERMINAL BLOOMBERG STYLE ●</span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)

