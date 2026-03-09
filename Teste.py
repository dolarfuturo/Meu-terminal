import streamlit as st
from datetime import datetime
import pytz
import time

# 1. MOTOR DE CÁLCULOS (LÓGICA PURA)
def get_eixo(max_val, min_val):
    return (max_val + min_val) / 2

def get_variacao_eixo(preco_atual, eixo_ref):
    if eixo_ref == 0: return "0,00%"
    var = ((preco_atual / eixo_ref) - 1) * 100
    return f"{var:+.2f}%".replace(".", ",")

def get_fair_price_dolar(eixo_dol, eixo_ewz, price_ewz_atual):
    try:
        desvio_ewz = (eixo_ewz / price_ewz_atual) - 1
        return eixo_dol * desvio_ewz * 100 / 2
    except: return eixo_dol

# 2. CONFIGURAÇÃO DE TELA (TABLET)
st.set_page_config(page_title="K97 - TERMINAL", layout="wide")

# 3. LAYOUT E CSS (FRONT-END)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .block-container { 
        border: 2px solid #3d444d; border-top: 4px solid #00f2ff; 
        padding: 15px; background: #0b0e11; border-radius: 4px; margin-bottom: 20px;
    }
    table { width: 100%; border-collapse: collapse; }
    th { color: #848e9c; font-size: 11px; text-align: left; padding: 10px; border-bottom: 2px solid #3d444d; }
    td { font-size: 20px !important; font-family: 'Arial Black'; font-weight: 900; padding: 18px 10px; border-bottom: 1px solid #1c2127; }
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    .eixo-box { border: 2px dashed #00f2ff; color: #ffcc00; text-align: center; padding: 12px; font-size: 18px; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# 4. ENTRADA DE DADOS (PAINEL ADM)
with st.expander("⚙️ CONFIGURAR EIXOS (REF: 11:30 - 18:00)"):
    col1, col2 = st.columns(2)
    with col1:
        eixo_spot = st.number_input("Eixo SPOT (Ontem)", value=5.4200, format="%.4f")
        eixo_ewz = st.number_input("Eixo EWZ (Ontem)", value=32.20, format="%.2f")
    with col2:
        price_ewz_hoje = st.number_input("EWZ Atual (6h+)", value=32.10, format="%.2f")

# 5. EXECUÇÃO DO MOTOR (CÁLCULOS ANTES DO VISUAL)
price_justo_dol = get_fair_price_dolar(eixo_spot, eixo_ewz, price_ewz_hoje)
var_spot = get_variacao_eixo(price_justo_dol, eixo_spot)

# 6. RENDERIZAÇÃO DA GRADE (LAYOUT FINAL)
st.markdown(f'<h2 style="color:#00f2ff;">BAIR <span style="color:#ffcc00;">- TERMINAL K97</span></h2>', unsafe_allow_html=True)

col_main, col_side = st.columns([3.2, 1.2])

with col_main:
    st.markdown('<div class="block-container">', unsafe_allow_html=True)
    # A coluna CLOSE exibe o Eixo conforme solicitado
    st.markdown(f"""
        <table>
            <tr><th>ATIVO</th><th>PRICE</th><th>CLOSE (EIXO)</th><th>VAR% (EIXO)</th></tr>
            <tr>
                <td><span style="color:#00f2ff;">SPOT</span></td>
                <td>{price_justo_dol:.4f}</td>
                <td>{eixo_spot:.4f}</td>
                <td class="perc-green">{var_spot}</td>
            </tr>
        </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    st.markdown('<div class="block-container">', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-size:12px; color:#ffcc00;">ALVOS OPERACIONAIS</p>', unsafe_allow_html=True)
    
    # Alvos partindo do Eixo
    for p, m in [("1,00%", 1.01), ("0,34%", 1.0034)]:
        st.markdown(f'<div style="display:flex; justify-content:space-between; padding:5px 0;">'
                    f'<span class="perc-green">{p}</span><span>{eixo_spot*m:.4f}</span></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="eixo-box">EIXO: {eixo_spot:.4f}</div>', unsafe_allow_html=True)
    
    for p, m in [("-0,66%", 0.9934), ("-1,00%", 0.99)]:
        st.markdown(f'<div style="display:flex; justify-content:space-between; padding:8px 0;">'
                    f'<span class="perc-red">{p}</span><span>{eixo_spot*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

time.sleep(1)
st.rerun()
