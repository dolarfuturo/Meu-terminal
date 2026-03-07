import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS PARA FONTES ROBUSTAS, BORDAS E RODAPÉ DINÂMICO
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    
    /* Título Robusto */
    .bair-text { color: #00f2ff; font-family: 'Segoe UI Black', sans-serif; font-size: 38px; text-shadow: 0 0 10px #00f2ff; }
    .terminal-text { color: #ffcc00; font-family: 'Segoe UI Black', sans-serif; font-size: 38px; text-shadow: 0 0 10px #ffcc00; }
    
    /* Relógios */
    .header-box { text-align: center; border: 1px solid #1f2329; padding: 10px; background: #161b22; border-radius: 4px; }
    .clock-time { color: #ffffff; font-size: 26px; font-weight: bold; font-family: 'Courier New', monospace; }
    .clock-label { color: #848e9c; font-size: 11px; text-transform: uppercase; }

    /* Grades com Borda Ciano Glow */
    .grid-container { 
        border: 2px solid #00f2ff; 
        padding: 15px; 
        border-radius: 8px; 
        background: #0b0e11; 
        box-shadow: inset 0 0 10px #00f2ff55;
        height: 100%;
    }
    
    /* Tabelas Robustas */
    table { width: 100%; border-collapse: collapse; }
    th { color: #00f2ff !important; font-size: 16px !important; border-bottom: 2px solid #00f2ff !important; padding: 12px !important; }
    td { font-size: 22px !important; font-family: 'Arial Black', sans-serif !important; padding: 12px !important; border-bottom: 1px solid #1f2329 !important; }
    .asset-tag { color: #ffffff; background: #1e1e2d; padding: 5px 12px; border-radius: 4px; border-left: 4px solid #00f2ff; font-weight: bold; }

    /* Cálculos */
    .calc-row { display: flex; justify-content: space-between; font-size: 20px; font-family: 'Arial Black', sans-serif; margin-bottom: 5px; }
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    .eixo-data { background: #00f2ff; color: #000; font-weight: bold; text-align: center; padding: 10px; margin: 15px 0; font-size: 20px; border-radius: 4px; }

    /* Rodapé Passante (Marquee Style) */
    .footer-ticker {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #161b22;
        color: #00f2ff;
        padding: 10px;
        font-family: monospace;
        font-size: 18px;
        white-space: nowrap;
        overflow: hidden;
        border-top: 2px solid #00f2ff;
    }
    .ticker-content { display: inline-block; padding-left: 100%; animation: ticker 20s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    /* Esconder o Adm (Botão Estilizado) */
    .stExpander { border: 1px solid #3d444d !important; background: #161b22 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_br, col_ny, col_ldn = st.columns([2.5, 1, 1, 1])
with col_logo:
    st.markdown('<span class="bair-text">BAIR</span> <span class="terminal-text">- TERMINAL DOLAR</span>', unsafe_allow_html=True)

def get_now(tz): return datetime.now(pytz.timezone(tz)).strftime("%H:%M:%S")

with col_br: st.markdown(f'<div class="header-box"><div class="clock-label">BRASÍLIA</div><div class="clock-time">{get_now("America/Sao_Paulo")}</div></div>', unsafe_allow_html=True)
with col_ny: st.markdown(f'<div class="header-box"><div class="clock-label">NEW YORK</div><div class="clock-time">{get_now("America/New_York")}</div></div>', unsafe_allow_html=True)
with col_ldn: st.markdown(f'<div class="header-box"><div class="clock-label">LONDRES</div><div class="clock-time">{get_now("Europe/London")}</div></div>', unsafe_allow_html=True)

st.write("")

# --- CORPO ---
main_c, side_c = st.columns([3, 1.4])

with main_c:
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#848e9c; font-size:14px; font-weight:bold;">MONITORAMENTO DA GRADE PRINCIPAL</p>', unsafe_allow_html=True)
    ativos = ["SPOT", "DOLFUT", "DXY", "EWZ", "EUR/USD", "XAU/USD", "PETROLEO BRENT"]
    table_html = "<table><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>MAX</th><th>MIN</th><th>VAR</th></tr>"
    for a in ativos:
        table_html += f"<tr><td><span class='asset-tag'>{a}</span></td><td>5.4000</td><td>5.0000</td><td>5.0000</td><td>5.0000</td><td>0.000</td><td>0.000</td></tr>"
    st.markdown(table_html + "</table></div>", unsafe_allow_html=True)

with side_c:
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#ffcc00; font-weight:bold; font-size:18px; text-align:center;">CÁLCULOS OPERACIONAIS</p>', unsafe_allow_html=True)
    
    # BOTÃO PARA ESCONDER ADM
    with st.expander("⚙️ CONFIGURAÇÃO ADM"):
        st.text_input("PAINEL ADM:", "5,4000")
        val_close = st.number_input("CLOSE REF:", value=5.4200, format="%.4f")
    else:
        # Se o expander estiver fechado, usamos um valor padrão ou o que foi digitado
        val_close = 5.4200 

    # Altas
    for p, m in [("3,00%", 1.03), ("2,34%", 1.0234), ("2,00%", 1.02), ("1,34%", 1.0134), ("1,00%", 1.01)]:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span>{val_close*m:.4f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-data">CLOSE EIXO: {val_close:.4f}</div>', unsafe_allow_html=True)

    # Baixas
    for p, m in [("-0,66%", 0.9934), ("-1,00%", 0.99), ("-1,66%", 0.9834), ("-2,00%", 0.98), ("-3,00%", 0.97)]:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span>{val_close*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# RODAPÉ DINÂMICO
st.markdown("""
    <div class="footer-ticker">
        <div class="ticker-content">
            <span style="color:#00ff88;">▲ DXY 0,01%</span> | 
            <span style="color:#00ff88;">▲ EURUSD 0,05%</span> | 
            <span style="color:#ff4d4d;">▼ EWZ -0,12%</span> | 
            <span style="color:#ffffff;">● SPOT 0,00%</span> | 
            <span style="color:#00ff88;">▲ GBPUSD 1,02%</span> |
            <span style="color:#ff4d4d;">▼ XAUUSD -0,05%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(1)
st.rerun()
