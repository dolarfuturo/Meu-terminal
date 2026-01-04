import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Monitor Side Pro", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

# --- FUNÇÃO DE COLETA ---
def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="2d") # Pegamos 2 dias para ter o fechamento de ontem
        if not df.empty:
            p = df['Close'].iloc[-1]
            h = df['High'].iloc[-1]
            l = df['Low'].iloc[-1]
            prev = df['Close'].iloc[-2] if len(df) > 1 else p
            v = ((p - prev) / prev) * 100
            return p, v, h, l, prev
    except: return 0.0, 0.0, 0.0, 0.0, 0.0
    return 0.0, 0.0, 0.0, 0.0, 0.0

# Coleta inicial para o Ajuste Automático
s, sv, sh, sl, s_prev = get_data("USDBRL=X")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    .stApp { background-color: #000000 !important; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }
    .frp-monitor {
        font-family: 'JetBrains Mono', monospace; background-color: #1a1a1a;
        color: #00FF66; font-size: 11px; text-align: center;
        padding: 4px; border-radius: 4px; margin-bottom: 8px; border: 1px solid #333;
    }
    .custom-row {
        display: flex; justify-content: space-between; align-items: baseline;
        border-bottom: 1px solid #1a1a1a; padding: 4px 0; margin-bottom: 2px;
    }
    .c-label { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #ff9900; font-weight: bold; }
    .c-value { font-family: 'Share Tech Mono', monospace; font-size: 19px; color: #ffffff; }
    .c-delta { font-size: 11px; margin-left: 5px; font-weight: bold; }
    .fut { color: #FFFF00 !important; }
    .max { color: #00FF66 !important; }
    .min { color: #FF0033 !important; }
    .pos { color: #00FF66; }
    .neg { color: #FF0033; }
    .header-box { font-family: 'JetBrains Mono', monospace; color: #FFFFFF; font-size: 13px; text-align: center; border-bottom: 1px solid #333; padding: 4px 0; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; border-top: 2px solid #FFFFFF; position: fixed; bottom: 0; left: 0; padding: 10px 0; height: 50px; z-index: 999; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 15s linear infinite; font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #FFFFFF; font-weight: bold; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='header-box'>🏛️ CÂMBIO</div>", unsafe_allow_html=True)

# --- MENU SET ---
with st.expander("SET"):
    f_val = st.number_input("FRP", value=0.015, step=0.001, format="%.3f")
    # O valor padrão agora é o 's_prev' que veio do Yahoo
    a_val = st.number_input("AJU (Auto)", value=float(s_prev), step=0.0001, format="%.4f")

# Monitor FRP
st.markdown(f"<div class='frp-monitor'>FRP: {f_val:.3f} ({int(f_val*1000)} pts) | AJU AUTO: {a_val:.4f}</div>", unsafe_allow_html=True)

# Demais Dados
u, uv, _, _, _ = get_data("USDT-BRL")
dx, dxv, _, _, _ = get_data("DX-Y.NYB")
ew, ewv, _, _, _ = get_data("EWZ")
d27, d27v, _, _, _ = get_data("DI1F27.SA")
d29, d29v, _, _, _ = get_data("DI1F29.SA")
d31, d31v, _, _, _ = get_data("DI1F31.SA")

def draw(lab, val, delt=None, cl=""):
    d_h = f"<span class='c-delta {'pos' if delt >= 0 else 'neg'}'>{delt:+.2f}%</span>" if delt is not None else ""
    st.markdown(f'<div class="custom-row"><div class="c-label">{lab}</div><div class="c-value {cl}">{val} {d_h}</div></div>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
with c1:
    draw("SPOT", f"{s:.4f}", sv)
    draw("FUT", f"{s + f_val:.4f}", sv, "fut")
    draw("AJU", f"{a_val:.4f}")
    draw("USDT", f"{u:.3f}", uv)
with c2:
    draw("MÁX", f"{sh + f_val:.4f}", cl="max")
    draw("MÍN", f"{sl + f_val:.4f}", cl="min")
    draw("DXY", f"{dx:.2f}", dxv)
    draw("EWZ", f"{ew:.2f}", ewv)

# Rodapé
def fdi(v, vr): return f"{v:.2f}%({vr:+.2f}%)" if v > 0 else "---"
led_html = f'<div class="ticker-wrap"><div class="ticker">DI27: {fdi(d27, d27v)} | DI29: {fdi(d29, d29v)} | DI31: {fdi(d31, d31v)} ● MONITOR OPERACIONAL</div></div>'
st.markdown(led_html, unsafe_allow_html=True)
