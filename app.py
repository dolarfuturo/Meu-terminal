import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Layout e Estilo (Fundo Grafite / Preto Claro)
st.set_page_config(page_title="Terminal Pro", layout="wide")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');
    
    /* Fundo Preto Claro / Grafite */
    .stApp { background-color: #121212; }
    .main { background-color: #121212; color: #FFFFFF; font-family: 'Roboto Mono', monospace; }
    
    /* Estilo dos Cards Centrais */
    [data-testid="metric-container"] {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] { font-size: 34px !important; font-weight: 800 !important; color: #FFFFFF !important; }
    div[data-testid="stMetricLabel"] { font-size: 16px !important; font-weight: 700 !important; color: #BBBBBB !important; }
    
    /* Ticker LED Estilo Bloomberg */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000000; 
        border-top: 2px solid #FF9900; padding: 12px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 30s linear infinite;
        font-family: 'Roboto Mono', monospace; font-size: 20px; color: #FF9900; font-weight: bold;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item { display: inline-block; margin-right: 60px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Função de Busca Robusta para Fim de Semana
def get_data(ticker):
    try:
        # Puxamos 10 dias para garantir que pegamos o fechamento de sexta se for sábado/domingo
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

# --- TOPO: DESENHO DO BANCO E TÍTULO ---
st.markdown("<h1 style='text-align: center; font-size: 60px; margin-bottom: 0;'>🏛️</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: white; font-weight: 900; margin-top: -20px; letter-spacing: 3px;'>CÂMBIO</h2>", unsafe_allow_html=True)

# Menu de Ajuste FRP
with st.expander("⌨️ CONFIGURAR FRP"):
    frp_manual = st.number_input("Valor do FRP", value=0.0150, format="%.4f")

st.markdown("<br>", unsafe_allow_html=True)

# --- CONTEÚDO CENTRAL ---
_, col_center, _ = st.columns([0.05, 0.9, 0.05])

with col_center:
    # Linha 1: Dólar e USDT
    c1, c2, c3 = st.columns(3)
    spot, spot_v = get_data("USDBRL=X")
    usdt, usdt_v = get_data("USDT-BRL")
    
    if spot > 0:
        c1.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
        c2.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    
    # Se USDT falhar no par BRL, usamos o spot como referência (aproximado)
    p_usdt = usdt if usdt > 0 else spot * 1.002
    v_usdt = usdt_v if usdt > 0 else 0.05
    c3.metric("USDT / BRL", f"{p_usdt:.3f}", f"{v_usdt:+.2f}%")

    st.markdown("<div style='margin: 30px;'></div>", unsafe_allow_html=True)

    # Linha 2: Índices Globais
    c4, c5, c6 = st.columns(3)
    dxy, dxy_v = get_data("DX-Y.NYB")
    ewz, ewz_v = get_data("EWZ")
    
    if dxy > 0: c4.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
    if ewz > 0: c5.metric("EWZ (Bolsa BR)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")
    c6.write("") # Espaço para manter o alinhamento

# --- RODAPÉ: LED PASSANDO (TAXAS DE JUROS DI) ---
di27, di27_v = get_data("DI1F27.SA")
di29, di29_v = get_data("DI1F29.SA")
di31, di31_v = get_data("DI1F31.SA")

def fmt_led(v, var):
    return f"{v:.2f}% ({var:+.2f}%)" if v > 0 else "Carregando..."

led_text = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span class="ticker-item">● DI 2027: {fmt_led(di27, di27_v)}</span>
            <span class="ticker-item">● DI 2029: {fmt_led(di29, di29_v)}</span>
            <span class="ticker-item">● DI 2031: {fmt_led(di31, di31_v)}</span>
            <span class="ticker-item">● TERMINAL PROFISSIONAL OPERANTE ●</span>
        </div>
    </div>
"""
st.markdown(led_text, unsafe_allow_html=True)

