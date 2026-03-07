import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet - Ocupar 100% da largura e remover margens
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide", initial_sidebar_state="collapsed")

# CSS AVANÇADO PARA IDENTIDADE VISUAL IDÊNTICA À IMAGEM
st.markdown("""
    <style>
    /* Fundo Total Escuro */
    .stApp { background-color: #0b0e11; color: #ffffff; }
    
    /* Título BAIR com Glow */
    .bair-title { 
        color: #00f2ff; 
        font-family: 'Arial Black', sans-serif; 
        font-size: 36px; 
        text-shadow: 0 0 10px #00f2ff;
        margin-top: -20px;
    }
    
    /* Relógios Analógico/Digital Style */
    .header-box { 
        text-align: center; 
        border: 1px solid #1f2329; 
        padding: 8px; 
        background: #161b22; 
        border-radius: 2px;
    }
    .clock-time { color: #ffffff; font-size: 26px; font-weight: bold; font-family: monospace; }
    .clock-label { color: #848e9c; font-size: 12px; text-transform: uppercase; }

    /* Grades com Borda Ciano Fina */
    .grid-border { 
        border: 1px solid #00f2ff; 
        padding: 15px; 
        background: #0b0e11; 
        border-radius: 4px;
    }

    /* Tabelas - Fontes Grandes e Alinhadas */
    table { width: 100%; border-collapse: collapse; }
    th { color: #00f2ff !important; font-size: 14px !important; text-align: left !important; border-bottom: 2px solid #00f2ff !important; padding: 10px !important; }
    td { font-size: 20px !important; font-family: 'Courier New', monospace !important; font-weight: bold !important; padding: 12px !important; border-bottom: 1px solid #1f2329 !important; }

    /* Painel de Cálculos - Compacto e Idêntico */
    .calc-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; font-family: 'Courier New', monospace; font-size: 17px; }
    .perc-green { color: #00ff88; font-weight: bold; width: 60px; }
    .perc-red { color: #ff4d4d; font-weight: bold; width: 60px; }
    .formula-desc { color: #848e9c; font-size: 13px; flex-grow: 1; margin-left: 10px; }
    .calc-value { color: #ffffff; font-weight: bold; }
    
    /* Eixo Central */
    .eixo-data { 
        background: #00f2ff; 
        color: #000000; 
        font-weight: bold; 
        text-align: center; 
        padding: 8px; 
        margin: 12px 0; 
        font-size: 18px;
        text-transform: uppercase;
    }

    /* Inputs Customizados */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #161b22 !important;
        color: #00f2ff !important;
        border: 1px solid #3d444d !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
c1, c2, c3, c4 = st.columns([2.5, 1, 1, 1])

with c1:
    st.markdown('<p class="bair-title">BAIR - TERMINAL DOLAR</p>', unsafe_allow_html=True)

def get_time(tz):
    return datetime.now(pytz.timezone(tz)).strftime("%H:%M:%S")

with c2:
    st.markdown(f'<div class="header-box"><div class="clock-label">BRASÍLIA</div><div class="clock-time">{get_time("America/Sao_Paulo")}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="header-box"><div class="clock-label">NEW YORK</div><div class="clock-time">{get_time("America/New_York")}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="header-box"><div class="clock-label">LONDRES</div><div class="clock-time">{get_time("Europe/London")}</div></div>', unsafe_allow_html=True)

st.write("")

# --- CORPO PRINCIPAL ---
main_col, side_col = st.columns([3, 1.4])

with main_col:
    st.markdown('<div class="grid-border">', unsafe_allow_html=True)
    st.markdown('<p style="color:#848e9c; font-size:13px; font-weight:bold;">MONITORAMENTO DA GRADE PRINCIPAL</p>', unsafe_allow_html=True)
    
    # Dados da Grade
    ativos = ["SPOT", "DOLFUT", "DXY", "EWZ", "EUR/USD", "XAU/USD", "PETROLEO BRENT"]
    # Criando HTML manual para controle total das fontes
    html_table = "<table><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>MAX</th><th>MIN</th><th>VAR</th></tr>"
    for a in ativos:
        html_table += f"<tr><td>{a}</td><td>5.4000</td><td>5.0000</td><td>5.0000</td><td>5.0000</td><td>0.000</td><td>0.000</td></tr>"
    html_table += "</table>"
    st.markdown(html_table, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with side_col:
    st.markdown('<div class="grid-border">', unsafe_allow_html=True)
    st.markdown('<p style="color:#00f2ff; font-weight:bold; font-size:15px; border-bottom:1px solid #00f2ff;">PANEL DE CONTROLE CÁLCULOS</p>', unsafe_allow_html=True)
    
    adm_val = st.text_input("PAINEL ADM:", "5,4000")
    st.markdown('<p style="font-size:12px; color:#848e9c; margin-top:-10px;">[1,0020] [1,0070] [1,0080]</p>', unsafe_allow_html=True)
    
    val_close = st.number_input("CLOSE REF:", value=5.4223, format="%.4f")
    
    # Cálculos Superiores (Verdes)
    cals_up = [("3,00%", 1.030), ("2,34%", 1.0234), ("2,00%", 1.020), ("1,34%", 1.0134), ("1,00%", 1.010), ("0,34%", 1.0034)]
    for p, m in cals_up:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span class="formula-desc">(=close x {m})</span><span class="calc-value">{val_close*m:.4f}</span></div>', unsafe_allow_html=True)

    # EIXO CENTRAL
    st.markdown(f'<div class="eixo-data">CLOSE CENTER DATA EIXO: {val_close:.4f}</div>', unsafe_allow_html=True)

    # Cálculos Inferiores (Vermelhos)
    cals_down = [("-0,66%", 0.9934), ("-1%", 0.9900), ("-1,66%", 0.9834), ("-2%", 0.9800), ("-2,66%", 0.9734), ("-3%", 0.9700)]
    for p, m in cals_down:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span class="formula-desc">(=close x {m})</span><span class="calc-value">{val_close*m:.4f}</span></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# RODAPÉ TICKER
st.markdown('<div style="margin-top:20px; border-top:1px solid #00f2ff; padding:10px; color:#00f2ff; text-align:center; font-family:monospace; font-size:16px;">↑ DXY 0,01% | EURUSD 0,01% | ↓ EWZ 0,0% | SPOT 0,0% | GBPUSD 1,00%</div>', unsafe_allow_html=True)

# Auto-refresh
time.sleep(1)
st.rerun()
