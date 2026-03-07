import streamlit as st
from datetime import datetime
import pytz
import time

# Força o layout wide e remove margens padrão do Streamlit
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS PARA FORÇAR IDENTIDADE VISUAL IDÊNTICA (DARK MODE & FONTES GRANDES)
st.markdown("""
    <style>
    /* Forçar Fundo Preto e tirar bordas do Streamlit */
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem;}

    /* Título BAIR em Ciano Neon */
    .bair-title { 
        color: #00f2ff; 
        font-family: 'Arial Black', sans-serif; 
        font-size: 34px; 
        text-shadow: 0 0 10px #00f2ff;
        margin-bottom: 20px;
    }
    
    /* Relógios com Fundo Escuro */
    .header-box { 
        text-align: center; 
        border: 1px solid #3d444d; 
        padding: 5px; 
        background: #161b22; 
        border-radius: 4px;
    }
    .clock-time { color: #ffffff; font-size: 24px; font-weight: bold; font-family: monospace; }
    .clock-label { color: #848e9c; font-size: 11px; text-transform: uppercase; }

    /* Estilo da Grade Principal */
    .grid-main { border: 1px solid #00f2ff; border-radius: 4px; padding: 10px; background: #0b0e11; }
    
    /* Tabela Customizada - Fontes Grandes */
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .custom-table th { 
        color: #00f2ff; 
        font-size: 14px; 
        text-align: left; 
        border-bottom: 1px solid #00f2ff; 
        padding: 8px; 
        text-transform: uppercase;
    }
    .custom-table td { 
        font-size: 22px; 
        font-family: 'Courier New', monospace; 
        font-weight: bold; 
        padding: 10px; 
        border-bottom: 1px solid #1f2329; 
    }
    /* Destaque para o nome do Ativo (Roxo/Azul) */
    .asset-name { color: #ffffff; background: #2d1b4d; padding: 4px 8px; border-radius: 2px; font-size: 18px; }

    /* Painel de Cálculos Lateral */
    .calc-panel { border: 1px solid #00f2ff; padding: 12px; background: #0b0e11; border-radius: 4px; }
    .calc-row { display: flex; justify-content: space-between; font-family: monospace; font-size: 18px; margin-bottom: 3px; }
    .perc-green { color: #00ff88; font-weight: bold; }
    .perc-red { color: #ff4d4d; font-weight: bold; }
    .formula-txt { color: #848e9c; font-size: 12px; margin-left: 5px; }

    /* Eixo Central */
    .eixo-box { 
        background: #00f2ff; 
        color: #000000; 
        font-weight: bold; 
        text-align: center; 
        padding: 6px; 
        margin: 10px 0; 
        font-size: 16px;
    }

    /* Ajuste de Inputs para Dark */
    input { background-color: #161b22 !important; color: #00f2ff !important; border: 1px solid #00f2ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

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

# --- CORPO ---
col_left, col_right = st.columns([3, 1.3])

with col_left:
    st.markdown('<div class="grid-main">', unsafe_allow_html=True)
    st.markdown('<p style="color:#848e9c; font-size:12px; font-weight:bold;">MONITORAMENTO DA GRADE PRINCIPAL</p>', unsafe_allow_html=True)
    
    # Tabela construída manualmente para fontes idênticas
    ativos = ["SPOT", "DOLFUT", "DXY", "EWZ", "EUR/USD", "XAU/USD", "PETROLEO BRENT"]
    table_html = """<table class="custom-table">
        <tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>MAX</th><th>MIN</th><th>VAR</th></tr>"""
    for a in ativos:
        table_html += f"""<tr>
            <td><span class="asset-name">{a}</span></td>
            <td>5.4000</td><td>5.0000</td><td>5.0000</td><td>5.0000</td><td>0.000</td><td>0.000</td>
        </tr>"""
    table_html += "</table></div>"
    st.markdown(table_html, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="calc-panel">', unsafe_allow_html=True)
    st.markdown('<p style="color:#00f2ff; font-weight:bold; font-size:14px; border-bottom: 1px solid #00f2ff; padding-bottom:5px;">PAINEL DE CONTROLE CÁLCULOS</p>', unsafe_allow_html=True)
    
    adm = st.text_input("PAINEL ADM:", "5,4000")
    close_val = st.number_input("CLOSE REF:", value=5.4223, format="%.4f")
    
    # Altas
    for p, m in [("3,00%", 1.030), ("2,34%", 1.0234), ("2,00%", 1.020), ("1,34%", 1.0134), ("1,00%", 1.010), ("0,34%", 1.0034)]:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span class="formula-txt">(=close x {m})</span><span>{close_val*m:.4f}</span></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="eixo-box">CLOSE CENTER DATA EIXO: {close_val:.4f}</div>', unsafe_allow_html=True)
    
    # Baixas
    for p, m in [("-0,66%", 0.9934), ("-1%", 0.9900), ("-1,66%", 0.9834), ("-2%", 0.9800), ("-2,66%", 0.9734), ("-3%", 0.9700)]:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span class="formula-txt">(=close x {m})</span><span>{close_val*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer Ticker
st.markdown('<div style="margin-top:20px; border-top:1px solid #00f2ff; color:#00f2ff; text-align:center; font-family:monospace; padding:10px;">↑ DXY 0,01% | EURUSD 0,01% | ↓ EWZ 0,0% | SPOT 0,0% | GBPUSD 1,00%</div>', unsafe_allow_html=True)

time.sleep(1)
st.rerun()
