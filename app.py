import streamlit as st
from datetime import datetime

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="TERMINAL DOLAR", layout="centered")

# Estilização CSS para o Look Termux / Bloomberg
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Fundo Preto Total */
    .stApp {
        background-color: #000000;
    }
    
    /* Fonte Estilo Termux */
    * {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Cabeçalho */
    .header-terminal {
        font-size: 28px;
        font-weight: bold;
        color: #FFFFFF;
        text-align: center;
        padding: 20px;
    }

    /* Preços e Labels */
    .label-bold { font-weight: bold; color: #FFFFFF; font-size: 20px; }
    .price-spot { font-size: 45px; font-weight: bold; color: #FFFFFF; }
    .price-orange { color: #FFA500; font-size: 24px; font-weight: bold; }
    .price-green-light { color: #90EE90; font-size: 24px; font-weight: bold; }
    .price-blue { color: #00BFFF; font-size: 24px; font-weight: bold; }
    .price-red { color: #FF4B4B; font-size: 24px; font-weight: bold; }
    .price-yellow { color: #FFFF00; font-size: 14px; }
    .price-fuchsia { color: #FF00FF; font-size: 14px; }
    
    /* Rodapé Ticker */
    .ticker-container {
        border-top: 1px solid #333;
        margin-top: 50px;
        padding-top: 10px;
        color: white;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ÁREA DO ADMINISTRADOR (OCULTA) ---
with st.expander("⚙️ CONFIGURAÇÕES ADM (INPUTS)"):
    col1, col2 = st.columns(2)
    with col1:
        ptax_base = st.number_input("PTAX Atual", value=5340.00, format="%.3f")
        fech_anterior = st.number_input("Fechamento Anterior", value=5360.00, format="%.3f")
    with col2:
        price_trava = st.number_input("PRICE (Trava Azul)", value=5335.00, format="%.3f")
        spot_live = st.number_input("Cotação Spot Atual", value=5362.50, format="%.3f")

# --- LÓGICA DE CÁLCULOS ---
# Variação Spot
variacao = ((spot_live / fech_anterior) - 1) * 100

# Cálculo de Equilíbrio: (PTAX * 1.004) - (PRICE * 1.004)
calc_equilibrio = (ptax_base * 1.004) - (price_trava * 1.004)

# Paridade (Exemplo de ajuste dinâmico)
paridade_val = spot_live + 1.250

# Preço Justo
preco_justo_val = (ptax_base + price_trava) / 2

# Referências Institucionais (Vermelho, Azul, Verde Claro)
ref_vermelho = ptax_base * 1.002
ref_azul = ptax_base * 1.006
ref_verde = ptax_base * 1.010

# --- RENDERIZAÇÃO DO TERMINAL ---

# 1. Título
st.markdown('<div class="header-terminal">TERMINAL DOLAR</div>', unsafe_allow_html=True)

# 2. Bloco SPOT e Variação
color_var = "#00FF00" if variacao >= 0 else "#FF0000"
st.markdown(f"""
    <div style="line-height: 1.2;">
        <span class="price-spot">{spot_live:.3f}</span> 
        <span style="color: {color_var}; font-size: 22px;">{variacao:+.2f}%</span><br>
        <span class="price-yellow">FECH. ANT: {fech_anterior:.3f}</span><br>
        <span class="price-blue" style="font-size: 14px;">PRICE: {price_trava:.3f}</span>
    </div>
    <br>
""", unsafe_allow_html=True)

# 3. Lista de Dados Vertical
st.markdown(f"""
    <div style="line-height: 2.0;">
        <span class="label-bold">PARIDADE:</span> <span class="price-orange">{paridade_val:.3f}</span><br>
        <span class="label-bold">EQUILÍBRIO:</span> <span class="price-green-light">{calc_equilibrio:.3f}</span><br>
        <span class="label-bold">PREÇO JUSTO:</span> <span class="price-blue">{preco_justo_val:.3f}</span><br>
        <span class="label-bold">REF INSTITUCIONAL:</span> 
        <span class="price-red">{ref_vermelho:.3f}</span> &nbsp;
        <span class="price-blue">{ref_azul:.3f}</span> &nbsp;
        <span class="price-green-light">{ref_verde:.3f}</span>
    </div>
""", unsafe_allow_html=True)

# 4. Rodapé Ticker
st.markdown(f"""
    <div class="ticker-container">
        DXY: 103.450 <span style="color:#00FF00;">+0.12%</span> | 
        EWZ: 32.112 <span style="color:#FF0000;">-0.85%</span> | 
        SPREAD: <span style="color:#FFFF00;">-4.50 pts</span> | 
        ATUALIZADO: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)
