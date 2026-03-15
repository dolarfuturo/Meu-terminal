import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS DE ALTA PERFORMANCE (VISUAL NEON DA IMAGEM) ---
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

# --- MOTOR DE DADOS K97 ---
@st.cache_data(ttl=600)
def get_eixo_ref():
    try:
        t = yf.Ticker("USDBRL=X")
        df = t.history(period="5d", interval="1d")
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        # Se for antes das 18h, olha para o dia anterior. Depois das 18h, olha para hoje.
        idx = -2 if agora.hour < 18 else -1
        mx, mn = df['High'].iloc[idx], df['Low'].iloc[idx]
        return (mx + mn) / 2
    except: return 5.4000

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
eixo_base = get_eixo_ref()
agora_sp = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M:%S')

# Cabeçalho Estilizado
st.markdown(f"""
<div class="header-bair">
    <div>BAIR - TERMINAL DOLAR</div>
    <div style="font-size: 14px; color: #888; font-family: monospace;">SÃO PAULO: {agora_sp} | EIXO: {eixo_base:.4f}</div>
</div>
""", unsafe_allow_html=True)

# Lista completa de ativos da imagem para dar volume
tickers = {
    "SPOT": "USDBRL=X",
    "DOLFUT": "BRL=X", # Representativo para o futuro
    "DXY": "DX-Y.NYB",
    "EWZ": "EWZ",
    "EUR/USD": "EURUSD=X",
    "XAU/USD": "GC=F", # Ouro (Gold)
    "PETROLEO BRENT": "BZ=F"
}

dados_display = []
for label, sym in tickers.items():
    d = fetch_live_data(sym)
    if d:
        cor = "var-pos" if d['var'] >= 0 else "var-neg"
        dados_display.append([label, f"{d['at']:.4f}", f"{d['cl']:.4f}", f"{d['cl']:.4f}", f"{d['mx']:.4f}", f"{d['mn']:.4f}", f"{d['var']:+.2f}", cor])

# --- RENDERIZAÇÃO DO GRID PRINCIPAL ---
html_grid = """
<div class="main-grid">
    <div style="background: #0a141a; color: #5ba6b5; text-align: center; padding: 8px; border-bottom: 1px solid #1c3d4d; font-size: 12px; letter-spacing: 2px;">
        MONITORAMENTO DA GRADE PRINCIPAL
    </div>
    <table class="terminal-table">
        <thead>
            <tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr>
        </thead>
        <tbody>"""

for a in dados_display:
    html_grid += f"""
        <tr>
            <td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>{a[0]}</td>
            <td style='color:#00f2ff;'>{a[1]}</td>
            <td>{a[2]}</td>
            <td>{a[3]}</td>
            <td>{a[4]}</td>
            <td>{a[5]}</td>
            <td class='{a[7]}'>{a[6]}%</td>
        </tr>"""

html_grid += "</tbody></table></div>"

# Layout de Colunas
col_main, col_side = st.columns([3, 1])

with col_main:
    st.markdown(html_grid, unsafe_allow_html=True)
    # Ticker Tape (Rodapé)
    st.markdown("""
    <div style="background: #000; color: #00f2ff; padding: 8px; margin-top: 15px; border: 1px solid #1c3d4d; font-size: 11px; text-align: center;">
        ↑ DXY 0,01% | EURUSD 0,01% | ↓ EWZ 0,0% | ↑ SPOT 0,0% | GBPUSD 1,00% | JPY/USD 0,00%
    </div>
    """, unsafe_allow_html=True)

with col_side:
    st.markdown(f"""
    <div style="border: 1px solid #1c3d4d; border-radius: 8px; padding: 15px; background: #0a141a; font-family: monospace; min-height: 440px;">
        <div style="color: #5ba6b5; text-align: center; font-size: 12px; margin-bottom: 15px;">PAINEL DE CONTROLE</div>
        <div style="color: #ffcc00; font-size: 20px; text-align: center; font-weight: bold;">EIXO: {eixo_base:.4f}</div>
        
        <div style="margin-top: 25px;">
            <div style="color: #00ff88; font-size: 13px; margin-bottom: 8px;">3,00% (= {eixo_base * 1.03:.4f})</div>
            <div style="color: #00ff88; font-size: 13px; margin-bottom: 8px;">2,34% (= {eixo_base * 1.0234:.4f})</div>
            <div style="color: #00ff88; font-size: 13px; margin-bottom: 8px;">1,34% (= {eixo_base * 1.0134:.4f})</div>
        </div>
        
        <div style="margin-top: 20px; border-top: 1px dashed #1c3d4d; padding-top: 15px;">
             <div style="color: #ff4d4d; font-size: 13px; margin-bottom: 8px;">-0,66% (= {eixo_base * 0.9934:.4f})</div>
             <div style="color: #ff4d4d; font-size: 13px; margin-bottom: 8px;">-1,66% (= {eixo_base * 0.9834:.4f})</div>
             <div style="color: #ff4d4d; font-size: 13px; margin-bottom: 8px;">-2,66% (= {eixo_base * 0.9734:.4f})</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Loop de atualização
time.sleep(2)
st.rerun()
