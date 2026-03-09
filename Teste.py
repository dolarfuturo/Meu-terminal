import streamlit as st
from datetime import datetime
import pytz
import time

# --- CONFIGURAÇÃO DO DISPOSITIVO (TABLET) ---
st.set_page_config(page_title="K97 - TERMINAL", layout="wide")

# --- MOTOR DE CÁLCULOS (BACK-END) ---
def calcular_variacao_eixo(atual, eixo):
    if eixo == 0: return "0,00%"
    var = ((atual / eixo) - 1) * 100
    return f"{var:+.2f}%".replace(".", ",")

def calcular_preco_dolar(eixo_dol, eixo_ewz, price_ewz):
    """Fórmula: eixo * (eixo_EWZ / price_ewz - 1) * 100 / 2"""
    try:
        desvio = (eixo_ewz / price_ewz) - 1
        return eixo_dol * desvio * 100 / 2
    except: return eixo_dol

# --- LAYOUT E CSS (FRONT-END) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black'; font-size: 32px; font-weight: 900; }
    
    /* Blocos Separados conforme desenho */
    .block-container { 
        border: 2px solid #3d444d; border-top: 4px solid #00f2ff; 
        padding: 15px; background: #0b0e11; border-radius: 4px; margin-bottom: 20px;
    }
    
    /* Grade de Ativos - Linhas Destacadas */
    table { width: 100%; border-collapse: collapse; }
    th { color: #848e9c; font-size: 11px; text-align: left; padding: 10px; border-bottom: 2px solid #3d444d; }
    td { font-size: 20px !important; font-family: 'Arial Black'; font-weight: 900; padding: 18px 10px; border-bottom: 1px solid #1c2127; }
    tr:nth-child(even) { background-color: rgba(255,255,255,0.02); }
    
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    .eixo-box { border: 2px dashed #00f2ff; color: #ffcc00; text-align: center; padding: 12px; font-size: 18px; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- PAINEL ADM (INPUTS PARA O MOTOR) ---
with st.expander("⚙️ CONFIGURAR EIXOS (11:30 - 18:00)"):
    col_adm1, col_adm2 = st.columns(2)
    with col_adm1:
        eixo_spot = st.number_input("EIXO SPOT (Dólar)", value=5.4200, format="%.4f")
        eixo_ewz = st.number_input("EIXO EWZ", value=32.20, format="%.2f")
    with col_adm2:
        price_ewz_atual = st.number_input("PRICE EWZ ATUAL (6h+)", value=32.10, format="%.2f")

# --- PROCESSAMENTO DOS DADOS ---
# O 'CLOSE' na tela é o Eixo calculado
# A variação parte sempre do Eixo
price_spot_calc = calcular_preco_dolar(eixo_spot, eixo_ewz, price_ewz_atual)

# --- INTERFACE VISUAL ---
st.markdown(f'<span class="bair-text">BAIR</span> <span class="terminal-text">- TERMINAL K97</span>', unsafe_allow_html=True)

col_main, col_side = st.columns([3.2, 1.2])

with col_main:
    st.markdown('<div class="block-container">', unsafe_allow_html=True)
    # Grade conforme solicitado: PRICE, CLOSE (Eixo), OPEN, MAX, MIN, VAR
    st.markdown("""
        <table>
            <tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>MAX</th><th>MIN</th><th>VAR%</th></tr>
            <tr>
                <td><span style="color:#00f2ff;">SPOT</span></td>
                <td>5,4000</td>
                <td>{:.4f}</td>
                <td>5,4100</td>
                <td>5,4350</td>
                <td>5,3910</td>
                <td class="perc-green">{}</td>
            </tr>
        </table>
    """.format(eixo_spot, calcular_variacao_eixo(5.4000, eixo_spot)), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    st.markdown('<div class="block-container">', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-size:12px; color:#ffcc00;">CÁLCULOS OPERACIONAIS</p>', unsafe_allow_html=True)
    
    # Exemplo de Alvos partindo do Eixo
    for p, m in [("1,00%", 1.01), ("0,34%", 1.0034)]:
        st.markdown(f'<div style="display:flex; justify-content:space-between; padding:8px 0;">'
                    f'<span class="perc-green">{p}</span><span>{eixo_spot*m:.4f}</span></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="eixo-box">EIXO: {eixo_spot:.4f}</div>', unsafe_allow_html=True)
    
    for p, m in [("-0,66%", 0.9934), ("-1,00%", 0.99)]:
        st.markdown(f'<div style="display:flex; justify-content:space-between; padding:8px 0;">'
                    f'<span class="perc-red">{p}</span><span>{eixo_spot*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

time.sleep(1)
st.rerun()
