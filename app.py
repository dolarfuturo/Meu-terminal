import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. CONFIGURAÇÃO - Sidebar aberta por padrão e layout largo
st.set_page_config(
    page_title="TERMINAL", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. INICIALIZAÇÃO DE ESTADO
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - ESTILO TERMINAL (REMOVIDO BOTÃO DE ENGRENAGEM E LIMPEZA TOTAL)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    
    /* Reset geral para modo Terminal */
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Esconde elementos nativos do Streamlit */
    header { visibility: hidden; display: none !important; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    
    /* Ajuste de margens */
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin-left: 10px; }
    
    /* Barra Lateral de Variáveis */
    [data-testid="stSidebar"] { 
        background-color: #111111 !important; 
        border-right: 1px solid #333; 
        min-width: 280px !important;
    }

    /* Estilização das Linhas de Preço */
    .terminal-header { font-size: 18px; font-weight: bold; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 5px; }
    .asset-row { display: flex; gap: 20px; margin-bottom: 12px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 110px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    
    .price-paridade { color: #FFB900 !important; }
    .price-ptax { color: #00FFFF !important; }

    /* Bloco de Pontos (Máxima, Justo, Mínima) - Sem Negrito e Menor */
    .frp-box { margin-left: 180px; margin-top: -5px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 2px; }
    .frp-item { display: flex; gap: 25px; font-size: 13px; font-weight: 400 !important; }

    /* Cores de Variação */
    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 15px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. PAINEL DE VARIÁVEIS (SIDEBAR À ESQUERDA)
with st.sidebar:
    st.markdown("### ⚙️ SET DE VARIÁVEIS")
    st.write("---")
    val_aj_manual = st.number_input("AJUSTE MANUAL", value=5.3900, format="%.4f", step=0.0001)
    val_ptax_manual = st.number_input("VALOR PTAX", value=5.3850, format="%.4f", step=0.0001)
    st.write("---")
    st.markdown("### 📊 PONTOS (PTS)")
    v_max = st.number_input("MAXIMA", value=42.0)
    v_jus = st.number_input("JUSTO", value=31.0)
    v_min = st.number_input("MINIMA", value=22.0)
    st.write("---")
    if st.button("LIMPAR TRAVA 16H"):
        st.session_state.spot_ref_locked = None

# Cabeçalho Principal
st.markdown('<div class="terminal-header">TERMINAL DE CAMBIO</div>', unsafe_allow_html=True)

def fetch_data(ticker):
    try:
        # Busca dados e garante que pegamos apenas o último valor escalar
        data = yf.download(ticker, period="2d", interval="1m", progress=False)
        return data if not data.empty else None
    except: return None

# 5. LOOP DE ATUALIZAÇÃO (A CADA 2 SEGUNDOS)
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = fetch_data("BRL=X")
        dxy_df = fetch_data("DX-Y.NYB")
        ewz_df = fetch_data("EWZ")

        if spot_df is not None:
            # Garantia de valor escalar para evitar TypeError
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Lógica da Trava 16h
            try:
                lock = spot_df.between_time('15:58', '16:02')
                if not lock.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock['Close'].iloc[-1])
            except: pass
            trava_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

            # Cálculos de Paridade e Variações
            d_at = float(dxy_df['Close'].iloc[-1]) if dxy_df is not None else 0
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0]) * 100) if dxy_df is not None else 0
            e_at = float(ewz_df['Close'].iloc[-1]) if ewz_df is not None else 0
            v_ewz = ((e_at - float(ewz_df['Open'].iloc[0])) / float(ewz_df['Open'].iloc[0]) * 100) if ewz_df is not None else 0

            spread = v_dxy - v_ewz
            paridade = val_aj_manual * (1 + (spread/100))
            v_s = ((spot_at - val_aj_manual) / val_aj_manual * 100)
            v_ptax_var = ((spot_at - val_ptax_manual) / val_ptax_manual * 100)

            # --- RENDERIZAÇÃO DO TERMINAL ---
            
            # PARIDADE
            st.markdown(f'<div class="asset-row"><div class="name">PARIDADE</div><div class="price price-paridade">{paridade:.4f}</div><div class="var {"pos" if spread >= 0 else "neg"}">{spread:+.2f}%</div></div>', unsafe_allow_html=True)
            
            # USD/BRL SPOT + PONTOS (MENORES E SEM NEGRITO)
            st.markdown(f'<div class="asset-row"><div class="name">USD/BRL SPOT</div><div class="price">{spot_at:.4f}</div><div class="var {"pos" if v_s >= 0 else "neg"}">{v_s:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(spot_at + (v_max/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(spot_at + (v_jus/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(spot_at + (v_min/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            # PTAX + PONTOS (BASEADOS NO VALOR SETADO)
            st.markdown(f'<div class="asset-row"><div class="name">PTAX</div><div class="price price-ptax">{val_ptax_manual:.4f}</div><div class="var {"pos" if v_ptax_var >= 0 else "neg"}">{v_ptax_var:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(val_ptax_manual + (v_max/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(val_ptax_manual + (v_jus/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(val_ptax_manual + (v_min/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            # DXY E EWZ
            st.markdown(f'<div class="asset-row"><div class="name">DXY INDEX</div><div class="price">{d_at:.2f}</div><div class="var {"pos" if v_dxy >= 0 else "neg"}">{v_dxy:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_at:.2f}</div><div class="var {"pos" if v_ewz >= 0 else "neg"}">{v_ewz:+.2f}%</div></div>', unsafe_allow_html=True)

            # TRAVA 16H (LARANJA)
            st.markdown(f'<div class="trava-orange">TRAVA 16H: {trava_val:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
