import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Tela e Estilo Bloomberg Vertical
st.set_page_config(page_title="Câmbio Pro", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    /* Fundo Preto Absoluto */
    .stApp { background-color: #000000 !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* Cabeçalho com Banco ao Lado */
    .header-box {
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF;
        font-size: 18px;
        text-align: center;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
        margin-bottom: 15px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
    }

    /* Blocos Verticais Compactos */
    [data-testid="stMetric"] {
        background-color: #000000;
        border-bottom: 1px solid #1a1a1a;
        padding: 4px 0 !important;
        margin-bottom: -25px !important;
    }

    /* Nomes dos Ativos (Laranja Bloomberg) */
    [data-testid="stMetricLabel"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        text-transform: uppercase;
        color: #ff9900 !important; 
        font-weight: 900 !important;
    }

    /* Números Digitais Quadrados */
    div[data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        color: #ffffff !important;
        font-size: 28px !important;
    }

    /* Cores de Variação */
    [data-testid="stMetricDelta"] { font-size: 14px !important; }

    /* Estilo do menu de ajuste */
    .st-expanderHeader { background-color: #000 !important; color: #444 !important; font-size: 9px !important; border: none !important; }

    /* LED Inferior Slim */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-top: 1px solid #333; padding: 6px 0;
        position: fixed; bottom: 0; left: 0; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #00FFCC;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    </style>
    """, unsafe_allow_html=True)

def get_market_data(ticker):
    try:
        t = yf.Ticker(ticker)
        # Puxa dados do dia atual
        df = t.history(period="1d")
        if not df.empty:
            price = df['Close'].iloc[-1]
            high = df['High'].iloc[-1]
            low = df['Low'].iloc[-1]
            prev = t.info.get('previousClose', price)
            var = ((price - prev) / prev) * 100
            return price, var, high, low
    except:
        return 0.0, 0.0, 0.0, 0.0
    return 0.0, 0.0, 0.0, 0.0

# --- TOPO: ÍCONE + TÍTULO ---
st.markdown("<div class='header-box'><span>🏛️</span><span>CÂMBIO</span></div>", unsafe_allow_html=True)

# CONFIGURAÇÕES (FRP e AJUSTE B3)
with st.expander("SET"):
    frp_manual = st.number_input("FRP", value=0.0150, format="%.4f")
    ajuste_fixo = st.number_input("AJUSTE", value=5.4500, format="%.4f")

# --- GRID VERTICAL ---
spot, spot_v, s_high, s_low = get_market_data("USDBRL=X")
usdt, usdt_v, _, _ = get_market_data("USDT-BRL")
dxy, dxy_v, _, _ = get_market_data("DX-Y.NYB")
ewz, ewz_v, _, _ = get_market_data("EWZ")

if spot > 0:
    # 1. Dólar Spot
    st.metric("DÓLAR SPOT", f"{spot:.4f}", f"{spot_v:+.2f}%")
    
    # 2. Dólar Futuro (Cálculo FRP)
    st.metric("DÓLAR FUTURO", f"{spot + frp_manual:.4f}", f"FRP {frp_manual:.4f}", delta_color="off")
    
    # 3. Máxima e Mínima (Baseadas no pregão do dia + FRP)
    st.metric("MÁXIMA FUT (DIA)", f"{s_high + frp_manual:.4f}", "HIGH", delta_color="normal")
    st.metric("MÍNIMA FUT (DIA)", f"{s_low + frp_manual:.4f}", "LOW", delta_color="inverse")
    
    # 4. Ajuste B3
    st.metric("PREÇO DE AJUSTE", f"{ajuste_fixo:.4f}", "B3", delta_color="off")
    
    # 5. Outros Ativos
    st.metric("USDT / BRL", f"{usdt if usdt > 0 else spot*1.002:.3f}", f"{usdt_v:+.2f}%")
    st.metric("DXY INDEX", f"{dxy:.2f}", f"{dxy_v:+.2f}%")
    st.metric("EWZ (BRL)", f"{ewz:.2f}", f"{ewz_v:+.2f}%")

# Espaçamento para o LED não cobrir o último item
st.markdown("<br><br>", unsafe_allow_html=True)

# --- LED INFERIOR ---
led_html = f"""
    <div class="ticker-wrap">
        <div class="ticker">
            <span>● MERCADO ATIVO ● MÁX/MÍN AJUSTADAS AO PREGÃO ● AGUARDANDO VOLATILIDADE ● TERMINAL OPERACIONAL ●</span>
        </div>
    </div>
"""
st.markdown(led_html, unsafe_allow_html=True)

