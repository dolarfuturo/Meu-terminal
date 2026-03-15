import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração da página para ocupar a tela toda do Tablet
st.set_page_config(layout="wide", page_title="BAIR TERMINAL")

# --- CSS PARA REPLICAR OS BLOCOS E LINHAS DA IMAGEM ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    
    /* Container Principal do Grid */
    .main-grid {
        border: 2px solid #1c3d4d;
        border-radius: 8px;
        padding: 0px;
        overflow: hidden;
        font-family: 'monospace';
    }

    /* Tabela de Monitoramento */
    .terminal-table {
        width: 100%;
        border-collapse: collapse;
        color: #e0e0e0;
    }

    .terminal-table th {
        background-color: #0a141a;
        color: #5ba6b5;
        border: 1px solid #1c3d4d;
        padding: 10px;
        text-align: center;
        font-size: 14px;
    }

    .terminal-table td {
        background-color: #0d1b22;
        border: 1px solid #1c3d4d;
        padding: 12px;
        text-align: center;
        font-size: 16px;
    }

    /* Cores das variações */
    .var-pos { color: #00f2ff; font-weight: bold; }
    .var-neg { color: #ff4d4d; font-weight: bold; }
    
    /* Header Estilizado */
    .header-bair {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        color: #00f2ff;
        font-size: 24px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("""
<div class="header-bair">
    <div>BAIR - TERMINAL DOLAR</div>
    <div style="font-size: 14px; color: #888;">BRASÍLIA: 21:03 | NY: 19:03 | LONDRES: 00:03</div>
</div>
""", unsafe_allow_html=True)

# --- CONSTRUÇÃO DA GRADE (GRID) ---
# Aqui simulamos os dados que virão do yfinance futuramente
ativos = [
    ["SPOT", "5,4000", "5,0000", "5,0000", "5,0000", "0,000", "0,000", "var-pos"],
    ["DOLFUT", "5,4000", "5,0000", "5,0000", "5,0000", "0,000", "0,000", "var-pos"],
    ["DXY", "5,4000", "5,0000", "5,0000", "5,0000", "0,000", "0,000", "var-neg"],
    ["EWZ", "5,4000", "5,0000", "5,0000", "5,0000", "0,000", "0,000", "var-neg"],
    ["EUR/USD", "5,0000", "5,0000", "5,0000", "5,0000", "0,000", "0,000", "var-pos"],
    ["XAU/USD", "5,0000", "5,0000", "5,0000", "5,0000", "0,000", "0,000", "var-pos"],
    ["PETROLEO BRENT", "5,0000", "5,0000", "5,0000", "5,0000", "0,000", "0,000", "var-pos"]
]

html_table = """
<div class="main-grid">
    <div style="background: #0a141a; color: #5ba6b5; text-align: center; padding: 5px; border-bottom: 1px solid #1c3d4d;">
        MONITORAMENTO DA GRADE PRINCIPAL
    </div>
    <table class="terminal-table">
        <tr>
            <th>ATIVO</th>
            <th>PRICE</th>
            <th>CLOSE</th>
            <th>OPEN</th>
            <th>MAX</th>
            <th>MIN</th>
            <th>VAR</th>
        </tr>
"""

for a in ativos:
    html_table += f"""
        <tr>
            <td style="color: #ffffff; text-align: left; font-weight: bold;">{a[0]}</td>
            <td style="color: #00f2ff;">{a[1]}</td>
            <td>{a[2]}</td>
            <td>{a[3]}</td>
            <td>{a[4]}</td>
            <td>{a[5]}</td>
            <td class="{a[7]}">{a[6]}</td>
        </tr>
    """

html_table += "</table></div>"

# Colunas para separar o Grid do Painel Lateral
col_main, col_side = st.columns([3, 1])

with col_main:
    st.markdown(html_table, unsafe_allow_html=True)
    # Ticker Tape (Rodapé)
    st.markdown("""
    <div style="background: #000; color: #00f2ff; padding: 5px; margin-top: 10px; border: 1px solid #1c3d4d; font-size: 12px;">
        ↑ DXY 0,01% | EURUSD 0,01% | ↓ EWZ 0,0% | ↑ SPOT 0,0% | GBPUSD 1,00%
    </div>
    """, unsafe_allow_html=True)

with col_side:
    st.markdown("""
    <div style="border: 1px solid #1c3d4d; border-radius: 8px; padding: 10px; background: #0a141a;">
        <div style="color: #5ba6b5; text-align: center; font-size: 12px;">PAINEL DE CONTROLE CÁLCULOS</div>
        <hr style="border: 0.5px solid #1c3d4d;">
        <div style="color: #ffcc00; font-size: 18px; text-align: center;">PAINEL ADM: 5,4000</div>
        <div style="color: #00ff88; font-size: 12px; margin-top: 10px;">3,00% (=close x 1,030)</div>
        <div style="color: #00ff88; font-size: 12px;">2,34% (=close x 1,0234)</div>
        <div style="color: #ff4d4d; font-size: 12px; margin-top: 10px;">-0,66% (=close x 0,9934)</div>
    </div>
    """, unsafe_allow_html=True)
