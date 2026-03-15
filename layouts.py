import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="K97 - BAIR TERMINAL")

# --- CSS DE ALTA PERFORMANCE (VISUAL DA IMAGEM) ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2px solid #1c3d4d; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #5ba6b5; border: 1px solid #1c3d4d; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #1c3d4d; padding: 12px; text-align: center; font-size: 15px; }
    .var-pos { color: #00f2ff !important; font-weight: bold; }
    .var-neg { color: #ff4d4d !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; color: #00f2ff; font-size: 22px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DADOS (RESET 18H) ---
@st.cache_data(ttl=600)
def get_eixo_dolar():
    try:
        t = yf.Ticker("USDBRL=X")
        df = t.history(period="7d", interval="1d")
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        idx = -2 if agora.hour < 18 else -1
        mx, mn = df['High'].iloc[idx], df['Low'].iloc[idx]
        return (mx + mn) / 2, mx, mn
    except: return 5.40, 5.45, 5.35

def fetch_live_data(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1d", interval="1m", prepost=True)
        if df.empty: return None
        at = df['Close'].iloc[-1]
        cl = df['Close'].iloc[0]
        var = ((at / cl) - 1) * 100
        return {"at": at, "cl": cl, "mx": df['High'].max(), "mn": df['Low'].min(), "var": var}
    except: return None

# --- PROCESSAMENTO ---
eixo_sug, mx_ontem, mn_ontem = get_eixo_dolar()
agora_sp = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M:%S')

# Cabeçalho
st.markdown(f"""
<div class="header-bair">
    <div>BAIR - TERMINAL DOLAR</div>
    <div style="font-size: 14px; color: #888; font-family: monospace;">SÃO PAULO: {agora_sp} | EIXO REF: {eixo_sug:.4f}</div>
</div>
""", unsafe_allow_html=True)

# Busca de dados reais
tickers = {"SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "EUR/USD": "EURUSD=X"}
dados_display = []

for label, sym in tickers.items():
    d = fetch_live_data(sym)
    if d:
        cor = "var-pos" if d['var'] >= 0 else "var-neg"
        dados_display.append([label, f"{d['at']:.4f}", f"{d['cl']:.4f}", f"{d['cl']:.4f}", f"{d['mx']:.4f}", f"{d['mn']:.4f}", f"{d['var']:+.2f}", cor])

# --- RENDERIZAÇÃO DA GRADE ---
html_grid = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
for a in dados_display:
    html_grid += f"""<tr><td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>{a[0]}</td><td style='color:#00f2ff;'>{a[1]}</td><td>{a[2]}</td><td>{a[3]}</td><td>{a[4]}</td><td>{a[5]}</td><td class='{a[7]}'>{a[6]}%</td></tr>"""
html_grid += "</tbody></table></div>"

col_main, col_side = st.columns([3, 1])
with col_main:
    st.markdown(html_grid, unsafe_allow_html=True)
with col_side:
    st.markdown(f"""
    <div style="border: 1px solid #1c3d4d; border-radius: 8px; padding: 15px; background: #0a141a; font-family: monospace;">
        <div style="color: #5ba6b5; text-align: center; font-size: 12px;">PAINEL K97</div>
        <div style="color: #ffcc00; font-size: 18px; text-align: center; margin-top:10px;">EIXO: {eixo_sug:.4f}</div>
        <div style="color: #00ff88; font-size: 12px; margin-top: 15px;">MAX PROJETADA: {eixo_sug * 1.0122:.4f}</div>
        <div style="color: #ff4d4d; font-size: 12px; margin-top: 5px;">MIN PROJETADA: {eixo_sug * 0.9878:.4f}</div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(2)
st.rerun()
