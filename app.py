import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. CONFIGURAÇÃO - Sidebar aberta e layout largo
st.set_page_config(
    page_title="TERMINAL", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. INICIALIZAÇÃO DE ESTADO
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - AJUSTE DE PROXIMIDADE E LAYOUT COMPACTO
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Esconde cabeçalho e lixo visual */
    header, [data-testid="stHeader"] { display: none !important; }
    
    /* BARRA LATERAL MAIS ESTREITA E PRÓXIMA */
    [data-testid="stSidebar"] { 
        background-color: #0A0A0A !important; 
        border-right: 1px solid #333; 
        width: 220px !important; /* Largura reduzida */
    }
    [data-testid="stSidebar"] button { display: none !important; } /* Esconde o X */

    /* AJUSTE DO CONTEÚDO PRINCIPAL PARA FICAR PRÓXIMO À BARRA */
    .block-container { 
        padding-top: 1rem !important; 
        max-width: 700px !important; 
        margin-left: 0px !important; /* Encosta na barra lateral */
        padding-left: 20px !important;
    }

    /* ESTILO DAS LINHAS */
    .terminal-header { font-size: 16px; font-weight: bold; color: #444; margin-bottom: 15px; border-bottom: 1px solid #222; }
    .asset-row { display: flex; gap: 15px; margin-bottom: 10px; align-items: center; }
    .name { width: 140px; font-size: 16px; color: #888; }
    .price { width: 100px; font-size: 17px; font-weight: bold; }
    .var { font-size: 16px; font-weight: bold; }
    
    .price-paridade { color: #FFB900 !important; }
    .price-ptax { color: #00FFFF !important; }

    /* PONTOS VERTICAIS COMPACTOS */
    .frp-box { margin-left: 155px; margin-top: -5px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 1px; }
    .frp-item { display: flex; gap: 20px; font-size: 12px; font-weight: 400 !important; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    .trava-orange { color: #FF8C00 !important; font-size: 16px; margin-top: 15px; font-weight: bold; border-top: 1px solid #222; padding-top: 5px; }
    
    /* Ajuste de inputs na sidebar para não quebrar layout */
    .stNumberInput label { font-size: 11px !important; color: #666 !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. PAINEL DE VARIÁVEIS (COLUNA ESQUERDA)
with st.sidebar:
    st.markdown("<p style='font-size:12px; color:#888;'>VARIÁVEIS DE CÁLCULO</p>", unsafe_allow_html=True)
    val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    val_ptax_manual = st.number_input("PTAX", value=5.3850, format="%.4f", step=0.0001)
    st.write("---")
    st.markdown("<p style='font-size:12px; color:#888;'>PONTOS (PTS)</p>", unsafe_allow_html=True)
    v_max = st.number_input("MAX", value=42.0)
    v_jus = st.number_input("JUS", value=31.0)
    v_min = st.number_input("MIN", value=22.0)
    if st.button("RESET TRAVA"):
        st.session_state.spot_ref_locked = None

# Interface
st.markdown('<div class="terminal-header">MARKET TERMINAL</div>', unsafe_allow_html=True)

def fetch_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False)
        return data if not data.empty else None
    except: return None

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

            # Dados DXY e EWZ
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
            st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_at:.2f}</div><div class="var {"pos" if v_ewz >= 0 else "neg"}">{v_ewz:+.2f}%</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="trava-orange">TRAVA 16H: {trava_val:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
