import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. CONFIGURAÇÃO - Layout largo e Sidebar escondida (variáveis agora estão no corpo)
st.set_page_config(
    page_title="TERMINAL", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. INICIALIZAÇÃO DE ESTADO
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - TERMINAL LIMPO COM VARIÁVEIS NO TOPO
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Remove cabeçalhos nativos */
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    
    /* Margens do container */
    .block-container { padding-top: 0rem !important; max-width: 800px !important; margin: auto; }

    /* TÍTULO NO TOPO */
    .main-title { 
        font-size: 22px; 
        font-weight: bold; 
        color: #FFFFFF; 
        text-align: center; 
        padding: 20px 0;
        border-bottom: 2px solid #333;
        margin-bottom: 20px;
    }

    /* ÁREA DE VARIÁVEIS (INPUTS) */
    .vars-container {
        background-color: #111;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 25px;
        border: 1px solid #222;
    }

    /* ESTILO DAS LINHAS DE ATIVOS */
    .asset-row { display: flex; gap: 20px; margin-bottom: 12px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 110px; font-size: 18px; font-weight: bold; }
    .var { font-size: 18px; font-weight: bold; }
    
    .price-paridade { color: #FFB900 !important; }
    .price-ptax { color: #00FFFF !important; }

    /* PONTOS VERTICAIS */
    .frp-box { margin-left: 180px; margin-top: -5px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 2px; }
    .frp-item { display: flex; gap: 25px; font-size: 13px; font-weight: 400 !important; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 20px; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; }
    
    /* Ajuste visual dos inputs para modo terminal */
    div[data-baseweb="input"] { background-color: #000 !important; border: 1px solid #444 !important; }
    input { color: #00FF00 !important; }
    label { color: #AAA !important; font-size: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. INTERFACE NO TOPO
st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

# Bloco de Variáveis Centralizado
with st.container():
    st.markdown('<div class="vars-container">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    with col2: val_ptax_manual = st.number_input("PTAX", value=5.3850, format="%.4f", step=0.0001)
    with col3: v_max = st.number_input("PTS MAX", value=42.0)
    with col4: v_jus = st.number_input("PTS JUS", value=31.0)
    with col5: v_min = st.number_input("PTS MIN", value=22.0)
    st.markdown('</div>', unsafe_allow_html=True)

def fetch_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False)
        return data if not data.empty else None
    except: return None

# 5. LOOP DE ATUALIZAÇÃO
placeholder = st.empty()

while True:
    with placeholder.container():
        s_df = fetch_data("BRL=X")
        d_df = fetch_data("DX-Y.NYB")
        e_df = fetch_data("EWZ")

        if s_df is not None:
            spot_at = float(s_df['Close'].iloc[-1])
            
            # Trava 16h
            try:
                lock = s_df.between_time('15:58', '16:02')
                if not lock.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock['Close'].iloc[-1])
            except: pass
            trava_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

            d_at = float(d_df['Close'].iloc[-1]) if d_df is not None else 0
            v_dxy = ((d_at - float(d_df['Open'].iloc[0])) / float(d_df['Open'].iloc[0]) * 100) if d_df is not None else 0
            e_at = float(e_df['Close'].iloc[-1]) if e_df is not None else 0
            v_ewz = ((e_at - float(e_df['Open'].iloc[0])) / float(e_df['Open'].iloc[0]) * 100) if e_df is not None else 0

            spread = v_dxy - v_ewz
            paridade = val_aj_manual * (1 + (spread/100))
            v_s = ((spot_at - val_aj_manual) / val_aj_manual * 100)
            v_p = ((spot_at - val_ptax_manual) / val_ptax_manual * 100)

            # --- EXIBIÇÃO ---
            st.markdown(f'<div class="asset-row"><div class="name">PARIDADE</div><div class="price price-paridade">{paridade:.4f}</div><div class="var {"pos" if spread >= 0 else "neg"}">{spread:+.2f}%</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="asset-row"><div class="name">USD/BRL SPOT</div><div class="price">{spot_at:.4f}</div><div class="var {"pos" if v_s >= 0 else "neg"}">{v_s:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(spot_at+(v_max/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(spot_at+(v_jus/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(spot_at+(v_min/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="asset-row"><div class="name">PTAX</div><div class="price price-ptax">{val_ptax_manual:.4f}</div><div class="var {"pos" if v_p >= 0 else "neg"}">{v_p:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(val_ptax_manual+(v_max/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(val_ptax_manual+(v_jus/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(val_ptax_manual+(v_min/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="asset-row"><div class="name">DXY INDEX</div><div class="price">{d_at:.2f}</div><div class="var {"pos" if v_dxy >= 0 else "neg"}">{v_dxy:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_at:.2f}</div><div class="var {"
