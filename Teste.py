import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet - Ocupar a tela inteira
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS PARA COPIAR O ESTILO DA FOTO (BAIR CIANO / TERMINAL DOLAR AMARELO)
st.markdown("""
    <style>
    /* Fundo Total Escuro */
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    
    /* Título Identico à Imagem */
    .bair-text { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 36px; text-shadow: 0 0 8px #00f2ff; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 36px; text-shadow: 0 0 8px #ffcc00; }
    
    /* Relógios no Estilo da Foto */
    .header-box { text-align: center; border: 1px solid #1f2329; padding: 10px; background: #161b22; border-radius: 4px; }
    .clock-time { color: #ffffff; font-size: 26px; font-weight: bold; font-family: monospace; }
    .clock-label { color: #848e9c; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }

    /* Estilo das Grades com Borda Ciano Glow */
    .grid-container { border: 1px solid #00f2ff; padding: 15px; border-radius: 4px; background: #0b0e11; box-shadow: 0 0 5px #00f2ff; }
    
    /* Tabela - Fontes Grandes e Claras */
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th { color: #00f2ff !important; font-size: 15px !important; text-align: left !important; border-bottom: 2px solid #00f2ff !important; padding: 10px !important; }
    td { font-size: 20px !important; font-family: 'Courier New', monospace !important; font-weight: bold !important; padding: 12px !important; border-bottom: 1px solid #1f2329 !important; }
    
    /* Destaque do Ativo */
    .asset-tag { color: #ffffff; background: #1e1e2d; padding: 4px 10px; border-radius: 3px; border-left: 3px solid #00f2ff; }

    /* Painel Lateral Compacto */
    .calc-row { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 18px; font-family: monospace; }
    .perc-green { color: #00ff88; font-weight: bold; }
    .perc-red { color: #ff4d4d; font-weight: bold; }
    
    /* Eixo Central */
    .eixo-data { background: #00f2ff; color: #000000; font-weight: bold; text-align: center; padding: 8px; margin: 12px 0; font-size: 18px; }

    /* Inputs para Tablet */
    input { background-color: #161b22 !important; color: #00f2ff !important; border: 1px solid #00f2ff !important; font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER: BAIR (CIANO) - TERMINAL DOLAR (AMARELO) ---
col_logo, col_br, col_ny, col_ldn = st.columns([2.5, 1, 1, 1])

with col_logo:
    st.markdown('<span class="bair-text">BAIR</span> <span class="terminal-text">- TERMINAL DOLAR</span>', unsafe_allow_html=True)

def get_tz_time(tz_name):
    return datetime.now(pytz.timezone(tz_name)).strftime("%H:%M:%S")

with col_br:
    st.markdown(f'<div class="header-box"><div class="clock-label">BRASÍLIA</div><div class="clock-time">{get_tz_time("America/Sao_Paulo")}</div></div>', unsafe_allow_html=True)
with col_ny:
    st.markdown(f'<div class="header-box"><div class="clock-label">NEW YORK</div><div class="clock-time">{get_tz_time("America/New_York")}</div></div>', unsafe_allow_html=True)
with col_ldn:
    st.markdown(f'<div class="header-box"><div class="clock-label">LONDRES</div><div class="clock-time">{get_tz_time("Europe/London")}</div></div>', unsafe_allow_html=True)

st.write("")

# --- CORPO PRINCIPAL ---
main_c, side_c = st.columns([3, 1.4])

with main_c:
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#848e9c; font-size:13px; font-weight:bold;">MONITORAMENTO DA GRADE PRINCIPAL</p>', unsafe_allow_html=True)
    
    ativos = ["SPOT", "DOLFUT", "DXY", "EWZ", "EUR/USD", "XAU/USD", "PETROLEO BRENT"]
    table_html = "<table><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>MAX</th><th>MIN</th><th>VAR</th></tr>"
    for a in ativos:
        table_html += f"<tr><td><span class=\"asset-tag\">{a}</span></td><td>5.4000</td><td>5.0000</td><td>5.0000</td><td>5.0000</td><td>0.000</td><td>0.000</td></tr>"
    table_html += "</table></div>"
    st.markdown(table_html, unsafe_allow_html=True)

with side_c:
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#ffcc00; font-weight:bold; font-size:16px;">PAINEL DE CONTROLE CÁLCULOS</p>', unsafe_allow_html=True)
    
    st.text_input("PAINEL ADM:", "5,4000")
    val_close = st.number_input("CLOSE REF:", value=5.4223, format="%.4f")
    
    # Cálculos Superiores
    cals_up = [("3,00%", 1.030), ("2,34%", 1.0234), ("2,00%", 1.020), ("1,34%", 1.0134), ("1,00%", 1.010), ("0,34%", 1.0034)]
    for p, m in cals_up:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span style="color:#848e9c; font-size:12px;">(=cl x {m})</span><span>{val_close*m:.4f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-data">CLOSE CENTER DATA EIXO: {val_close:.4f}</div>', unsafe_allow_html=True)

    # Cálculos Inferiores
    cals_down = [("-0,66%", 0.9934), ("-1%", 0.9900), ("-1,66%", 0.9834), ("-2%", 0.9800), ("-2,66%", 0.9734), ("-3%", 0.9700)]
    for p, m in cals_down:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span style="color:#848e9c; font-size:12px;">(=cl x {m})</span><span>{val_close*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# RODAPÉ
st.markdown('<div style="margin-top:20px; border-top:1px solid #00f2ff; padding:10px; color:#00f2ff; text-align:center; font-family:monospace; font-size:16px;">DXY 0,01% | EURUSD 0,01% | EWZ 0,0% | SPOT 0,0% | GBPUSD 1,00%</div>', unsafe_allow_html=True)

time.sleep(1)
st.rerun()
