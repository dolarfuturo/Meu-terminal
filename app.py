import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# Configuração de Tela Ultra-Slim
st.set_page_config(page_title="Monitor Side Pro", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    .stApp { background-color: #000000 !important; }
    .block-container { padding: 0.1rem !important; }
    .frp-monitor {
        font-family: 'JetBrains Mono', monospace; background-color: #1a1a1a;
        color: #00FF66; font-size: 11px; text-align: center;
        padding: 4px; border-radius: 4px; border: 1px solid #333; margin-bottom: 5px;
    }
    .custom-row { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid #1a1a1a; padding: 4px 0; }
    .c-label { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #ff9900; font-weight: bold; }
    .c-value { font-family: 'Share Tech Mono', monospace; font-size: 19px; color: #ffffff; }
    .c-delta { font-size: 11px; margin-left: 5px; font-weight: bold; }
    .fut { color: #FFFF00 !important; }
    .max { color: #00FF66 !important; }
    .min { color: #FF0033 !important; }
    .pos { color: #00FF66; }
    .neg { color: #FF0033; }
    .header-box { font-family: 'JetBrains Mono', monospace; color: #FFFFFF; font-size: 12px; text-align: center; border-bottom: 1px solid #333; padding: 3px 0; margin-top: 5px;}
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; border-top: 2px solid #FFFFFF; position: fixed; bottom: 0; left: 0; padding: 10px 0; height: 50px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 15s linear infinite; font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #FFFFFF; font-weight: bold; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
    """, unsafe_allow_html=True)

def get_data(ticker, is_spot=False):
    try:
        t = yf.Ticker(ticker)
        # Se for Spot, tenta pegar 1m para IB, senão pega diário simples para evitar erro
        df = t.history(period="2d", interval="1m" if is_spot else "1d")
        if df.empty:
            df = t.history(period="2d", interval="1d")
        
        p = df['Close'].iloc[-1]
        h = df['High'].max()
        l = df['Low'].min()
        prev = df['Close'].iloc[-2] if len(df) > 1 else p
        v = ((p - prev) / prev) * 100
        
        # Dados específicos para o Spot (Abertura e IB)
        open_d = df['Open'].iloc[0] if is_spot else 0
        df_1h = df.between_time('09:00', '10:00') if is_spot else None
        ib_h = df_1h['High'].max() if (is_spot and df_1h is not None and not df_1h.empty) else 0
        ib_l = df_1h['Low'].min() if (is_spot and df_1h is not None and not df_1h.empty) else 0
        
        return p, v, h, l, prev, open_d, ib_h, ib_l
    except:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

# Coleta Principal (SPOT)
s, sv, sh, sl, s_prev, s_open, ib_h, ib_l = get_data("USDBRL=X", is_spot=True)

st.markdown("<div class='header-box'>🏛️ CÂMBIO</div>", unsafe_allow_html=True)

with st.expander("SET"):
    f_val = st.number_input("FRP", value=0.015, step=0.001, format="%.3f")
    # Correção do parêntese que causou o erro na sua foto:
    a_val = st.number_input("AJUSTE B3", value=float(s_prev if s_prev > 0 else 5.4500), format="%.4f")

st.markdown(f"<div class='frp-monitor'>FRP: {f_val:.3f} | AJU: {a_val:.4f}</div>", unsafe_allow_html=True)

def draw(lab, val, delt=None, cl=""):
    v_str = f"{val:.4f}" if isinstance(val, float
