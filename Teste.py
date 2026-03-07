import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS AJUSTADO: RELÓGIOS MENORES E FONTES ROBUSTAS
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    
    /* Título Robusto */
    .bair-text { color: #00f2ff; font-family: 'Segoe UI Black', sans-serif; font-size: 34px; text-shadow: 0 0 8px #00f2ff; }
    .terminal-text { color: #ffcc00; font-family: 'Segoe UI Black', sans-serif; font-size: 34px; text-shadow: 0 0 8px #ffcc00; }
    
    /* Relógios Reduzidos */
    .header-box { text-align: center; border: 1px solid #1f2329; padding: 5px; background: #161b22; border-radius: 4px; }
    .clock-time { color: #ffffff; font-size: 20px; font-weight: bold; font-family: 'Courier New', monospace; }
    .clock-label { color: #848e9c; font-size: 9px; text-transform: uppercase; letter-spacing: 1px; }

    /* Grades com Borda Ciano Glow */
    .grid-container { 
        border: 2px solid #00f2ff; 
        padding: 12px; 
        border-radius: 8px; 
        background: #0b0e11; 
        box-shadow: inset 0 0 8px #00f2ff44;
    }
    
    /* Tabelas Robustas */
    table { width: 100%; border-collapse: collapse; }
    th { color: #00f2ff !important; font-size: 14px !important; border-bottom: 2px solid #00f2ff !important; padding: 8px !important; }
    td { font-size: 20px !important; font-family: 'Arial Black', sans-serif !important; padding: 10px !important; border-bottom: 1px solid #1f2329 !important; }
    .asset-tag { color: #ffffff; background: #1e1e2d; padding: 4px 10px; border-radius: 4px; border-left: 4px solid #00f2ff; font-weight: bold; }

    /* Cálculos */
    .calc-row { display: flex; justify-content: space-between; font-size: 19px; font-family: 'Arial Black', sans-serif; margin-bottom: 4px; }
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    .eixo-data { background: #00f2ff; color: #000; font-weight: bold; text-align: center; padding: 8px; margin: 10px 0; font-size: 19px; border-radius: 4px; }

    /* Rodapé Passante */
    .footer-ticker {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #161b22;
        color: #00f2ff;
        padding: 8px;
        font-family: monospace;
        font-size: 16px;
        white-space: nowrap;
        overflow: hidden;
        border-top: 2px solid #00f2ff;
        z-index: 1000;
    }
    .ticker-content { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    /* Ajuste do Expander Adm */
    .stExpander { border: 1px solid #3d444d !important; background: #161b22 !important; margin-bottom: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_br, col_ny, col_ldn = st.columns([2.8, 0.8, 0.8, 0.8])
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
    st.markdown('<p style="color:#848e9c; font-size:13px; font-weight:bold; margin-bottom:5px;">MONITORAMENTO DA GRADE PRINCIPAL</p>', unsafe_allow_html=True)
    ativos = ["SPOT", "DOLFUT", "DXY", "EWZ", "EUR/USD", "XAU/USD", "PETROLEO BRENT"]
    table_html = "<table><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>MAX</th><th>MIN</th><th>VAR</th></tr>"
    for a in ativos:
        table_html += f"<tr><td><span class='asset-tag'>{a}</span></td><td>5.4000</td><td>5.0000</td><td>5.0000</td><td>5.0000</td><td>0.000</td><td>0.000</td></tr>"
    st.markdown(table_html + "</table></div>", unsafe_allow_html=True)

with side_c:
    # Botão ADM agora fica fora da borda principal para economizar espaço
    with st.expander("⚙️ ADM"):
        st.text_input("PAINEL ADM:", "5,4000")
        val_close = st.number_input("CLOSE REF:", value=5.4200, format="%.4f")
    
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#ffcc00; font-weight:bold; font-size:16px; text-align:center; margin-bottom:10px;">CÁLCULOS OPERACIONAIS</p>', unsafe_allow_html=True)
    
    v_close = val_close if 'val_close' in locals() else 5.4200

    # Altas
    for p, m in [("3,00%", 1.03), ("2,34%", 1.0234), ("2,00%", 1.02), ("1,34%", 1.0134), ("1,00%", 1.01)]:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span>{v_close*m:.4f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-data">EIXO: {v_close:.4f}</div>', unsafe_allow_html=True)

    # Baixas
    for p, m in [("-0,66%", 0.9934), ("-1,00%", 0.99), ("-1,66%", 0.9834), ("-2,00%", 0.98), ("-3,00%", 0.97)]:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span>{v_close*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# RODAPÉ DINÂMICO
st.markdown("""
    <div class="footer-ticker">
        <div class="ticker-content">
            <span style="color:#00ff88;">▲ DXY 0,01%</span> | <span style="color:#00ff88;">▲ EURUSD 0,05%</span> | 
            <span style="color:#ff4d4d;">▼ EWZ -0,12%</span> | <span style="color:#ffffff;">● SPOT 0,00%</span> | 
            <span style="color:#00ff88;">▲ GBPUSD 1,02%</span> | <span style="color:#ff4d4d;">▼ XAUUSD -0,05%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(1)
st.rerun()
