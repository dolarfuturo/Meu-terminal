import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS PARA CORES LARANJA E RODAPÉ DINÂMICO ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2px solid #1c3d4d; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #1c3d4d; padding: 10px; text-align: center; font-size: 13px; }
    .terminal-table td { border: 1px solid #1c3d4d; padding: 12px; text-align: center; font-size: 15px; }
    
    /* Título e Destaques em Laranja/Dourado */
    .orange-text { color: #d4a017 !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; color: #00f2ff; font-size: 26px; font-weight: bold; }
    
    /* Estilo dos Relógios */
    .clock-container { display: flex; gap: 20px; color: #888; font-family: 'monospace'; font-size: 12px; }
    .clock-box { text-align: center; }
    .clock-time { color: #fff; font-size: 16px; display: block; }

    /* Efeito de Rodapé Passando (Marquee) */
    .ticker-wrapper {
        background: #000;
        border: 1px solid #1c3d4d;
        color: #d4a017;
        padding: 5px;
        overflow: hidden;
        white-space: nowrap;
        margin-top: 15px;
    }
    .ticker-text {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 20s linear infinite;
        font-family: 'monospace';
        font-size: 12px;
    }
    @keyframes marquee {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE HORÁRIOS MUNDIAIS ---
def get_world_times():
    fmt = '%H:%M'
    br = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime(fmt)
    ny = datetime.now(pytz.timezone('America/New_York')).strftime(fmt)
    ld = datetime.now(pytz.timezone('Europe/London')).strftime(fmt)
    return br, ny, ld

br_time, ny_time, ld_time = get_world_times()

# --- HEADER COM RELÓGIOS ---
st.markdown(f"""
<div class="header-bair">
    <div style="color: #00f2ff;">BAIR - <span style="color: #d4a017;">TERMINAL DOLAR</span></div>
    <div class="clock-container">
        <div class="clock-box">BRASÍLIA<span class="clock-time">{br_time}</span></div>
        <div class="clock-box">NEW YORK<span class="clock-time">{ny_time}</span></div>
        <div class="clock-box">LONDRES<span class="clock-time">{ld_time}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- BUSCA DE DADOS (Motor K97) ---
@st.cache_data(ttl=600)
def get_eixo():
    t = yf.Ticker("USDBRL=X")
    df = t.history(period="2d")
    return (df['High'].iloc[-1] + df['Low'].iloc[-1]) / 2

def fetch(s):
    try:
        d = yf.Ticker(s).history(period="1d", interval="1m")
        return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
    except: return None

eixo = get_eixo()
tickers = {"SPOT": "USDBRL=X", "DOLFUT": "BRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO": "BZ=F"}

# --- TABELA PRINCIPAL ---
html_grid = """<div class="main-grid"><table class="terminal-table"><thead><tr>
<th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>MAX</th><th>MIN</th><th>VAR</th>
</tr></thead><tbody>"""

ticker_items = ""
for label, sym in tickers.items():
    data = fetch(sym)
    if data:
        var = ((data['at']/data['cl'])-1)*100
        cor = "#00f2ff" if var >= 0 else "#ff4d4d"
        html_grid += f"""<tr>
            <td style='color:#fff; text-align:left; font-weight:bold; padding-left:15px;'>{label}</td>
            <td style='color:#d4a017;'>{data['at']:.4f}</td>
            <td>{data['cl']:.4f}</td><td>{data['cl']:.4f}</td>
            <td>{data['mx']:.4f}</td><td>{data['mn']:.4f}</td>
            <td style='color:{cor}; font-weight:bold;'>{var:+.2f}%</td>
        </tr>"""
        ticker_items += f" • {label}: {var:+.2f}% "

html_grid += "</tbody></table></div>"

col_main, col_side = st.columns([3, 1])
with col_main:
    st.markdown(html_grid, unsafe_allow_html=True)
    # Rodapé Passando (Marquee)
    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{ticker_items * 3}</div></div>', unsafe_allow_html=True)

with col_side:
    st.markdown(f"""
    <div style="border: 2px solid #1c3d4d; border-radius: 8px; padding: 15px; background: #0a141a; font-family: monospace;">
        <div style="color: #d4a017; text-align: center; font-size: 14px; font-weight: bold;">PAINEL ADM: {eixo:.4f}</div>
        <hr style="border: 0.5px solid #1c3d4d;">
        <div style="color: #00ff88; font-size: 13px; margin-top: 10px;">3,00% (={eixo*1.03:.4f})</div>
        <div style="color: #00ff88; font-size: 13px;">2,34% (={eixo*1.0234:.4f})</div>
        <div style="color: #ff4d4d; font-size: 13px; margin-top: 10px;">-0,66% (={eixo*0.9934:.4f})</div>
        <div style="color: #ff4d4d; font-size: 13px;">-2,66% (={eixo*0.9734:.4f})</div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(2)
st.rerun()
