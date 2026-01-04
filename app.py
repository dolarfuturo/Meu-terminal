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
    .c-value { font-family: 'Share Tech Mono', monospace; font-size: 21px; color: #ffffff; }
    .c-delta { font-size: 12px; margin-left: 5px; font-weight: bold; }
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
        # Tenta pegar 1m para o Spot (IB), senão usa diário simples
        df = t.history(period="2d", interval="1m" if is_spot else "1d")
        if df.empty:
            df = t.history(period="2d", interval="1d")
        
        if df.empty: return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        
        p = df['Close'].iloc[-1]
        h = df['High'].max()
        l = df['Low'].min()
        prev = df['Close'].iloc[-2] if len(df) > 1 else p
        v = ((p - prev) / prev) * 100
        
        open_d = df['Open'].iloc[0] if is_spot else 0
        df_1h = df.between_time('09:00', '10:00') if is_spot else None
        ib_h = df_1h['High'].max() if (is_spot and df_1h is not None and not df_1h.empty) else 0
        ib_l = df_1h['Low'].min() if (is_spot and df_1h is not None and not df_1h.empty) else 0
        
        return p, v, h, l, prev, open_d, ib_h, ib_l
    except:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

# Coleta SPOT
s, sv, sh, sl, s_prev, s_open, ib_h, ib_l = get_data("USDBRL=X", is_spot=True)

st.markdown("<div class='header-box'>🏛️ CÂMBIO</div>", unsafe_allow_html=True)

with st.expander("SET"):
    f_val = st.number_input("FRP", value=0.015, step=0.001, format="%.3f")
    # Correção definitiva do campo AJUSTE
    a_val = st.number_input("AJUSTE B3", value=float(s_prev if s_prev > 0 else 5.4223), format="%.4f")

st.markdown(f"<div class='frp-monitor'>FRP: {f_val:.3f} | AJU: {a_val:.4f}</div>", unsafe_allow_html=True)

def draw(lab, val, delt=None, cl=""):
    v_str = f"{val:.4f}" if (isinstance(val, float) and val > 0) else "---"
    d_h = f"<span class='c-delta {'pos' if delt >= 0 else 'neg'}'>{delt:+.2f}%</span>" if (delt is not None and val > 0) else ""
    st.markdown(f'<div class="custom-row"><div class="c-label">{lab}</div><div class="c-value {cl}">{v_str} {d_h}</div></div>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
with c1:
    draw("SPOT", s, sv)
    draw("FUT", (s + f_val) if s > 0 else 0, sv, "fut")
    draw("AJU", a_val)
with c2:
    draw("MÁX", (sh + f_val) if sh > 0 else 0, cl="max")
    draw("MÍN", (sl + f_val) if sl > 0 else 0, cl="min")
    draw("ABE", (s_open + f_val) if s_open > 0 else 0)

st.markdown("<div class='header-box'>⏱️ RANGE 1ª HORA (IB)</div>", unsafe_allow_html=True)
c3, c4 = st.columns([1, 1])
with c3:
    draw("IB MÁX", (ib_h + f_val) if ib_h > 0 else 0, cl="max")
with c4:
    draw("IB MÍN", (ib_l + f_val) if ib_l > 0 else 0, cl="min")

st.markdown("<div class='header-box'>🌍 EXTERNO / JURISTA</div>", unsafe_allow_html=True)
u, uv, _, _, _, _, _, _ = get_data("USDT-BRL")
dx, dxv, _, _, _, _, _, _ = get_data("DX-Y.NYB")
ew, ewv, _, _, _, _, _, _ = get_data("EWZ")
d27, d27v, _, _, _, _, _, _ = get_data("DI1F27.SA")
d29, d29v, _, _, _, _, _, _ = get_data("DI1F29.SA")
d31, d31v, _, _, _, _, _, _ = get_data("DI1F31.SA")

c5, c6 = st.columns([1, 1])
with c5:
    draw("DXY", dx, dxv)
    draw("USDT", u, uv)
with c6:
    draw("EWZ", ew, ewv)

def fdi(v, vr): return f"{v:.2f}%({vr:+.2f}%)" if v > 0 else "---"
led_html = f'<div class="ticker-wrap"><div class="ticker">DI27: {fdi(d27, d27v)} | DI29: {fdi(d29, d29v)} | DI31: {fdi(d31, d31v)} ● MONITOR OPERACIONAL</div></div>'
st.markdown(led_html, unsafe_allow_html=True)
