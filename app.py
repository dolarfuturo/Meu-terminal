import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. CONFIGURAÇÃO - Fixa a Sidebar à esquerda
st.set_page_config(
    page_title="TERMINAL", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. ESTADO DA SESSÃO
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - REFINAMENTO DE LAYOUT (COMPACTO)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Remove todo o lixo do topo e engrenagens */
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    
    /* Estilização da Sidebar (Painel de Variáveis) */
    [data-testid="stSidebar"] { 
        background-color: #0A0A0A !important; 
        border-right: 1px solid #222; 
        min-width: 220px !important;
    }
    /* Esconde o botão de fechar (X) da sidebar */
    button[kind="headerNoPadding"] { display: none !important; }

    /* Ajuste do container principal */
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0px !important; margin-left: 5px; }

    .terminal-header { 
        font-size: 16px; 
        color: #555; 
        border-bottom: 1px solid #222; 
        padding-bottom: 5px; 
        margin-bottom: 15px; 
    }

    /* Linhas de ativos mais compactas */
    .asset-row { display: flex; gap: 15px; margin-bottom: 2px; align-items: center; }
    .name { width: 140px; font-size: 16px; color: #AAA; }
    .price { width: 100px; font-size: 17px; font-weight: bold; }
    .var { font-size: 16px; font-weight: bold; }
    
    .price-paridade { color: #FFB900 !important; }
    .price-ptax { color: #00E5FF !important; }

    /* Bloco de Pontos - Muito próximo do preço e menor */
    .frp-box { 
        margin-left: 155px; 
        margin-top: -2px; 
        margin-bottom: 12px; 
        display: flex; 
        flex-direction: column; 
        gap: 0px; 
        border-left: 1px solid #222;
        padding-left: 10px;
    }
    .frp-item { display: flex; gap: 20px; font-size: 12px; font-weight: 400 !important; line-height: 1.4; }

    /* Cores de sinal */
    .pos { color: #00FF41 !important; } /* Verde Matrix */
    .neg { color: #FF3131 !important; } /* Vermelho Alerta */
    .blu { color: #00A3FF !important; }
    
    .trava-orange { color: #FF8C00 !important; font-size: 16px; margin-top: 10px; border-top: 1px solid #222; padding-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 4. PAINEL DE VARIÁVEIS (ESQUERDA)
with st.sidebar:
    st.markdown("<h3 style='font-size:14px; color:#555;'>CONFIGURAR SET</h3>", unsafe_allow_html=True)
    val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    val_ptax_manual = st.number_input("PTAX DIA", value=5.3850, format="%.4f", step=0.0001)
    st.write("---")
    v_max = st.number_input("PTS MAX", value=42.0)
    v_jus = st.number_input("PTS JUS", value=31.0)
    v_min = st.number_input("PTS MIN", value=22.0)
    if st.button("RESET TRAVA"):
        st.session_state.spot_ref_locked = None

# Interface
st.markdown('<div class="terminal-header">MARKET TERMINAL / BRL-SPOT</div>', unsafe_allow_html=True)

def fetch_data(ticker):
    try:
        return yf.download(ticker, period="2d", interval="1m", progress=False)
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

            # Cálculos
            d_at = float(d_df['Close'].iloc[-1]) if d_df is not None else 0
            v_dxy = ((d_at - float(d_df['Open'].iloc[0])) / float(d_df['Open'].iloc[0]) * 100) if d_df is not None else 0
            e_at = float(e_df['Close'].iloc[-1]) if e_df is not None else 0
            v_ewz = ((e_at - float(e_df['Open'].iloc[0])) / float(e_df['Open'].iloc[0]) * 100) if e_df is not None else 0

            spread = v_dxy - v_ewz
            paridade = val_aj_manual * (1 + (spread/100))
            v_s = ((spot_at - val_aj_manual) / val_aj_manual * 100)
            v_p = ((spot_at - val_ptax_manual) / val_ptax_manual * 100)

            # RENDERIZAÇÃO COMPACTA
            st.markdown(f'<div class="asset-row"><div class="name">PARIDADE</div><div class="price price-paridade">{paridade:.4f}</div><div class="var {"pos" if spread >= 0 else "neg"}">{spread:+.2f}%</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="asset-row"><div class="name">USD/BRL SPOT</div><div class="price">{spot_at:.4f}</div><div class="var {"pos" if v_s >= 0 else "neg"}">{v_s:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAX</span><span class="pos">{(spot_at+(v_max/1000)):.4f}</span><span>JUS</span><span class="blu">{(spot_at+(v_jus/1000)):.4f}</span><span>MIN</span><span class="neg">{(spot_at+(v_min/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="asset-row"><div class="name">PTAX</div><div class="price price-ptax">{val_ptax_manual:.4f}</div><div class="var {"pos" if v_p >= 0 else "neg"}">{v_p:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAX</span><span class="pos">{(val_ptax_manual+(v_max/1000)):.4f}</span><span>JUS</span><span class="blu">{(val_ptax_manual+(v_jus/1000)):.4f}</span><span>MIN</span><span class="neg">{(val_ptax_manual+(v_min/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="asset-row"><div class="name">DXY INDEX</div><div class="price">{d_at:.2f}</div><div class="var {"pos" if v_dxy >= 0 else "neg"}">{v_dxy:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_at:.2f}</div><div class="var {"pos" if v_ewz >= 0 else "neg"}">{v_ewz:+.2f}%</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="trava-orange">TRAVA 16H: {trava_val:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
