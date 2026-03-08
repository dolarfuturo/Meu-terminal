import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS: GRID TÉCNICO, TÍTULOS INTERNOS E PONTO PISCANDO
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    
    /* Títulos e Animação do Ponto Verde */
    .bair-text { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 28px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 28px; font-weight: 900; }
    
    .live-dot {
        height: 12px; width: 12px; background-color: #00ff88;
        border-radius: 50%; display: inline-block; margin-left: 8px;
        box-shadow: 0 0 8px #00ff88;
        animation: blink-animation 1s steps(2, start) infinite;
    }
    @keyframes blink-animation { to { visibility: hidden; } }
    
    /* Relógios Digitais */
    .city-name { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 10px; text-align: center; margin-bottom: 2px; }
    .clock-container { background: #161b22; border: 1px solid #3d444d; padding: 5px; text-align: center; }
    .digital-time { color: #ffffff; font-size: 16px; font-weight: bold; font-family: monospace; }

    /* MOLDURA COM TÍTULO INTERNO */
    .frame-box { 
        border: 2px solid #ffffff !important; 
        padding: 0px; 
        background: #0b0e11; 
        margin-bottom: 15px;
    }
    .frame-header {
        background: #161b22;
        border-bottom: 2px solid #ffffff;
        padding: 5px 10px;
        color: #ffcc00;
        font-family: 'Arial Black', sans-serif;
        font-size: 14px;
        font-weight: 900;
        text-transform: uppercase;
    }
    .frame-content { padding: 10px; }
    
    /* TABELA TÉCNICA */
    table { width: 100%; border-collapse: collapse; border: none; }
    th { 
        color: #00f2ff !important; font-size: 10px !important; 
        border: 1px solid #ffffff !important; 
        text-align: left; padding: 6px !important; background: #1c2127;
    }
    td { 
        font-size: 17px !important; font-family: 'Arial Black', sans-serif !important; 
        border: 1px solid #ffffff !important; 
        padding: 6px !important; 
    }
    
    .asset-tag { color: #00f2ff; font-weight: 900; }

    /* CÁLCULOS (FONTE REDUZIDA) */
    .calc-row { 
        display: flex; justify-content: space-between; 
        font-size: 16px; /* Fonte reduzida para caber no tablet */
        font-family: 'Arial Black', sans-serif; font-weight: 900; 
        padding: 3px 5px; border-bottom: 1px solid #ffffff; 
    }
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    .eixo-frame { border: 2px dashed #00f2ff; color: #000; background: #ffcc00; font-weight: 900; text-align: center; padding: 5px; margin: 8px 0; font-size: 16px; }

    /* Rodapé */
    .footer-ticker {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000; padding: 8px; border-top: 2px solid #ffffff;
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
c_logo, c_br, c_ny, c_ldn = st.columns([2.8, 1, 1, 1])
with c_logo:
    st.markdown('<span class="bair-text">BAIR</span> <span class="terminal-text">- TERMINAL DOLAR</span><div class="live-dot"></div>', unsafe_allow_html=True)

def clock_simple(city, tz):
    t = datetime.now(pytz.timezone(tz)).strftime("%H:%M:%S")
    return f'<div class="city-name">{city}</div><div class="clock-container"><div class="digital-time">{t}</div></div>'

with c_br: st.markdown(clock_simple("BRASÍLIA", "America/Sao_Paulo"), unsafe_allow_html=True)
with c_ny: st.markdown(clock_simple("NEW YORK", "America/New_York"), unsafe_allow_html=True)
with c_ldn: st.markdown(clock_simple("LONDRES", "Europe/London"), unsafe_allow_html=True)

# --- PAINEL ADM ---
with st.expander("⚙️ PAINEL ADM"):
    c1, c2 = st.columns(2)
    with c1: adm_val = st.text_input("VALOR ATUAL:", "5,4000")
    with c2: close_ref = st.number_input("CLOSE REF:", value=5.4200, format="%.4f")

# --- CORPO DO TERMINAL ---
m_col, s_col = st.columns([3.2, 1.2])

with m_col:
    # Grade de Monitoramento com Título Interno
    st.markdown(f"""
    <div class="frame-box">
        <div class="frame-header">SYSTEM GRADE MONITORING</div>
        <div class="frame-content">
    """, unsafe_allow_html=True)
    
    ativos_data = [
        ("SPOT", "5.4000", "5.4200", "5.4100", "0,00%"),
        ("DOLFUT", "5.4120", "5.4300", "5.4200", "0,05%"),
        ("DXY", "104.20", "104.10", "104.15", "0,10%"),
        ("EWZ", "32.10", "32.20", "32.15", "-0,12%"),
        ("EUR/USD", "1.0850", "1.0840", "1.0845", "0,09%"),
        ("XAU/USD", "2030.5", "2028.0", "2029.0", "0,12%"),
        ("PETRO BRENT", "82.40", "81.90", "82.00", "0,61%")
    ]
    
    t_html = "<table><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>VAR%</th></tr>"
    for name, p, c, o, v in ativos_data:
        color = "perc-green" if "-" not in v else "perc-red"
        t_html += f"<tr><td><span class='asset-tag'>{name}</span></td><td>{p}</td><td>{c}</td><td>{o}</td><td class='{color}'>{v}</td></tr>"
    st.markdown(t_html + "</table></div></div>", unsafe_allow_html=True)

with s_col:
    # Cálculos Operacionais com Título Interno e Fonte Reduzida
    st.markdown(f"""
    <div class="frame-box">
        <div class="frame-header" style="text-align:center;">CÁLCULOS</div>
        <div class="frame-content">
    """, unsafe_allow_html=True)
    
    # Altas
    for p, m in [("3,00%", 1.03), ("2,34%", 1.0234), ("2,00%", 1.02), ("1,34%", 1.0134), ("1,00%", 1.01), ("0,34%", 1.0034)]:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span>{close_ref*m:.4f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-frame">EIXO: {close_ref:.4f}</div>', unsafe_allow_html=True)

    # Baixas
    for p, m in [("-0,66%", 0.9934), ("-1,00%", 0.99), ("-1,66%", 0.9834), ("-2,00%", 0.98), ("-2,66%", 0.9734), ("-3,00%", 0.97)]:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span>{close_ref*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# --- RODAPÉ ---
st.markdown('<div class="footer-ticker"><p style="text-align:center; margin:0; font-size:12px; font-weight:bold;">DXY 0,10% | EWZ -0,12% | SPOT 0,00% | DOLFUT 0,05%</p></div>', unsafe_allow_html=True)

time.sleep(1)
st.rerun()
