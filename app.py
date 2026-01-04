import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

st.set_page_config(page_title="Monitor Side Pro", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

# --- FUNÇÃO DE COLETA ---
def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="2d", interval="1m") # Dados de 1 min para precisão
        if not df.empty:
            current_p = df['Close'].iloc[-1]
            high_d = df['High'].max()
            low_d = df['Low'].min()
            open_d = df['Open'].iloc[0] # Preço de Abertura do dia
            
            # Filtro para Primeira Hora (09:00 - 10:00)
            df_1h = df.between_time('09:00', '10:00')
            ib_high = df_1h['High'].max() if not df_1h.empty else 0.0
            ib_low = df_1h['Low'].min() if not df_1h.empty else 0.0
            
            # Fechamento anterior para o Ajuste
            df_daily = t.history(period="2d")
            prev_c = df_daily['Close'].iloc[-2] if len(df_daily) > 1 else current_p
            
            v = ((current_p - prev_c) / prev_c) * 100
            return current_p, v, high_d, low_d, prev_c, open_d, ib_high, ib_low
    except: return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

# Coleta
s, sv, sh, sl, s_prev, s_open, ib_h, ib_l = get_data("USDBRL=X")

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
    .custom-row {
        display: flex; justify-content: space-between; align-items: baseline;
        border-bottom: 1px solid #1a1a1a; padding: 4px 0;
    }
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

# --- MENU SET ---
with st.expander("SET"):
    f_val = st.number_input("FRP", value=0.015, step=0.001, format="%.3f")
    a_val = st.number_input("AJU (Auto)", value=float(s_prev), step=0.0001, format="%.4f")

# Monitor FRP
st.markdown(f"<div class='frp-monitor'>FRP: {f_val:.3f} | AJU: {a_val:.4f}</div>", unsafe_allow_html=True)

def draw(lab, val, delt=None, cl=""):
    d_h = f"<span class='c-delta {'pos' if delt >= 0 else 'neg'}'>{delt:+.2f}%</span>" if delt is not None else ""
    st.markdown(f'<div class="custom-row"><div class="c-label">{lab}</div><div class="c-value {cl}">{val} {d_h}</div></div>', unsafe_allow_html=True)

# Colunas Principais
c1, c2 = st.columns([1, 1])
with c1:
    draw("SPOT", f"{s:.4f}", sv)
    draw("FUT", f"{s + f_val:.4f}", sv, "fut")
    draw("AJU", f"{a_val:.4f}")
with c2:
    draw("MÁX", f"{sh + f_val:.4f}", cl="max")
    draw("MÍN", f"{sl + f_val:.4f}", cl="min")
    draw("ABE", f"{s_open + f_val:.4f}")

st.markdown("<div class='header-box'>⏱️ RANGE 1ª HORA (IB)</div>", unsafe_allow_html=True)
c3, c4 = st.columns([1, 1])
with c3:
    draw("IB MÁX", f"{ib_h + f_val:.4f}" if ib_h > 0 else "---", cl="max")
with c4:
    draw("IB MÍN", f"{ib_l + f_val:.4f}" if ib_l > 0 else "---", cl="min")

# Outros Ativos
st.markdown("<div class='header-box'>🌍 EXTERNO / JURISTA</div>", unsafe_allow_html=True)
u, uv, _, _, _ = get_data("USDT-BRL")
dx, dxv, _, _, _ = get_data("DX-Y.NYB")
ew, ewv, _, _, _ = get_data("EWZ")
d27, d27v, _, _, _ = get_data("DI1F27.SA")
d29, d29v, _, _, _ = get_data("DI1F29.SA")
d31, d31v, _, _, _ = get_data("DI1F31.SA")

c5, c6 = st.columns([1, 1])
with c5:
    draw("DXY", f"{dx:.2f}", dxv)
    draw("USDT", f"{u:.3f}", uv)
with c6:
    draw("EWZ", f"{ew:.2f}", ewv)

# Rodapé
def fdi(v, vr): return f"{v:.2f}%({vr:+.2f}%)" if v > 0 else "---"
led_html = f'<div class="ticker-wrap"><div class="ticker">DI27: {fdi(d27, d27v)} | DI29: {fdi(d29, d29v)} | DI31: {fdi(d31, d31v)} ● MONITOR OPERACIONAL</div></div>'
st.markdown(led_html, unsafe_allow_html=True)
