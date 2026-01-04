import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Terminal Slim", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    .stApp { background-color: #000000 !important; }
    .block-container { padding: 0.1rem !important; max-width: 100% !important; }
    
    /* Linha de Ativo Customizada */
    .row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        border-bottom: 1px solid #1a1a1a;
        padding: 2px 0;
        margin-bottom: 2px;
    }
    .label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        color: #ff9900;
        text-transform: uppercase;
    }
    .value {
        font-family: 'Share Tech Mono', monospace;
        font-size: 19px;
        color: #ffffff;
    }
    .delta {
        font-size: 10px;
        margin-left: 5px;
    }
    
    /* Cores Específicas */
    .futuro { color: #FFFF00 !important; }
    .max { color: #00FF66 !important; }
    .min { color: #FF0033 !important; }
    .pos { color: #00FF66; }
    .neg { color: #FF0033; }

    .header-box {
        font-family: 'JetBrains Mono', monospace; color: #FFFFFF; font-size: 12px;
        text-align: center; border-bottom: 1px solid #333; padding: 2px 0; margin-bottom: 10px;
    }

    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; border-top: 2px solid #ff9900;
        position: fixed; bottom: 0; left: 0; padding: 10px 0; height: 50px; z-index: 999;
    }
    .ticker {
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite;
        font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #ffb400; font-weight: bold;
    }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
    """, unsafe_allow_html=True)

def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d")
        if not df.empty:
            p = df['Close'].iloc[-1]
            h = df['High'].iloc[-1]
            l = df['Low'].iloc[-1]
            prev = t.info.get('previousClose', p)
            v = ((p - prev) / prev) * 100
            return p, v, h, l
    except: return 0.0, 0.0, 0.0, 0.0
    return 0.0, 0.0, 0.0, 0.0

# --- DADOS ---
s, sv, sh, sl = get_data("USDBRL=X")
u, uv, _, _ = get_data("USDT-BRL")
dx, dxv, _, _ = get_data("DX-Y.NYB")
ew, ewv, _, _ = get_data("EWZ")
d27, d27v, _, _ = get_data("DI1F27.SA")
d29, d29v, _, _ = get_data("DI1F29.SA")
d31, d31v, _, _ = get_data("DI1F31.SA")

st.markdown("<div class='header-box'>🏛️ CÂMBIO</div>", unsafe_allow_html=True)

with st.expander("SET"):
    frp = st.number_input("FRP", value=0.0150, format="%.4f")
    aju = st.number_input("AJU", value=5.4500, format="%.4f")

# Função para desenhar a linha sem sumir com o nome
def draw_row(label, value, delta=None, class_val=""):
    d_html = ""
    if delta is not None:
        color_class = "pos" if delta >= 0 else "neg"
        d_html = f"<span class='delta {color_class}'>{delta:+.2f}%</span>"
    
    st.markdown(f"""
        <div class="row">
            <div class="label">{label}</div>
            <div class="value {class_val}">{value} {d_html}</div>
        </div>
    """, unsafe_allow_html=True)

# Layout 2 Colunas
c1, c2 = st.columns([1, 1])

with c1:
    draw_row("SPOT", f"{s:.4f}", sv)
    draw_row("FUTURO", f"{s + frp:.4f}", sv, "futuro")
    draw_row("AJUSTE", f"{aju:.4f}")
    draw_row("USDT", f"{u:.3f}", uv)

with c2:
    draw_row("MÁXIMA", f"{sh + frp:.4f}", class_val="max")
    draw_row("MÍNIMA", f"{sl + frp:.4f}", class_val="min")
    draw_row("DXY", f"{dx:.2f}", dxv)
    draw_row("EWZ", f"{ew:.2f}", ewv)

# Rodapé
def fdi(v, vr): return f"{v:.2f}%({vr:+.2f}%)" if v > 0 else "---"
led = f"""
    <div class="ticker-wrap"><div class="ticker">
        DI27: {fdi(d27, d27v)} | DI29: {fdi(d29, d29v)} | DI31: {fdi(d31, d31v)} ● MONITOR OPERACIONAL
    </div></div>
"""
st.markdown(led, unsafe_allow_html=True)
