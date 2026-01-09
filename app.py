import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. CONFIGURAÇÃO - Layout largo
st.set_page_config(page_title="TERMINAL", layout="wide")

if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 2. CSS - ESTILO TERMINAL DARK (TOPO LIMPO E BOTÃO DISCRETO)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Esconde cabeçalho nativo */
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin: auto; }

    /* TÍTULO */
    .main-title { font-size: 20px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 10px; }

    /* ESTILO DAS LINHAS DE ATIVOS */
    .asset-row { display: flex; gap: 20px; margin-bottom: 8px; align-items: center; }
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
    
    /* Estilo do botão de Parâmetros */
    .stPopover button { 
        background-color: #111 !important; 
        color: #555 !important; 
        border: 1px solid #222 !important;
        font-size: 10px !important;
        height: 25px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFACE DE TOPO
st.markdown('<div class="main-title">TERMINAL DE CÂMBIO</div>', unsafe_allow_html=True)

# BOTÃO QUE ABRE AS VARIÁVEIS EM UM POPUP FLUTUANTE
with st.popover("⚙️ AJUSTAR PARÂMETROS"):
    st.markdown("### CONFIGURAÇÕES")
    val_aj_manual = st.number_input("AJUSTE MANUAL", value=5.3900, format="%.4f", step=0.0001)
    val_ptax_manual = st.number_input("VALOR PTAX", value=5.3850, format="%.4f", step=0.0001)
    st.divider()
    v_max = st.number_input("PTS MÁXIMA", value=42.0)
    v_jus = st.number_input("PTS JUSTO", value=31.0)
    v_min = st.number_input("PTS MÍNIMA", value=22.0)
    if st.button("LIMPAR TRAVA 16H"):
        st.session_state.spot_ref_locked = None

def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1m", progress=False)
        return df if (df is not None and not df.empty) else None
    except: return None

# 4. LOOP DE ATUALIZAÇÃO
placeholder = st.empty()

while True:
    with placeholder.container():
        s_df = fetch_data("BRL=X")
        d_df = fetch_data("DX-Y.NYB")
        e_df = fetch_data("EWZ")

        if s_df is not None:
            spot_at = float(s_df['Close'].iloc[-1])
            
            try:
                lock_data = s_df.between_time('15:58', '16:02')
                if not lock_data.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
            except: pass
            trava_exibir = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

            d_at = float(d_df['Close'].iloc[-1]) if d_df is not None else 0
            v_dxy = ((d_at - float(d_df['Open'].iloc[0])) / float(d_df['Open'].iloc[0]) * 100) if d_df is not None else 0
            e_at = float(e_df['Close'].iloc[-1]) if e_df is not None else 0
            v_ewz = ((e_at - float(e_df['Open'].iloc[0])) / float(e_df['Open'].iloc[0]) * 100) if e_df is not None else 0

            spread_calc = v_dxy - v_ewz
            paridade_val = val_aj_manual * (1 + (spread_calc/100))
            var_spot = ((spot_at - val_aj_manual) / val_aj_manual * 100)

            # --- EXIBIÇÃO ---
            # PARIDADE
            st.markdown(f'<div class="asset-row"><div class="name">PARIDADE</div><div class="price price-paridade">{paridade_val:.4f}</div><div class="var {"pos" if spread_calc >= 0 else "neg"}">{spread_calc:+.2f}%</div></div>', unsafe_allow_html=True)
            
            # SPOT + PONTOS
            st.markdown(f'<div class="asset-row"><div class="name">USD/BRL SPOT</div><div class="price">{spot_at:.4f}</div><div class="var {"pos" if var_spot >= 0 else "neg"}">{var_spot:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(spot_at+(v_max/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(spot_at+(v_jus/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(spot_at+(v_min/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            # PTAX + PONTOS (SEM PERCENTUAL)
            st.markdown(f'<div class="asset-row"><div class="name">PTAX</div><div class="price price-ptax">{val_ptax_manual:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frp-box"><div class="frp-item"><span>MAXIMA</span><span class="pos">{(val_ptax_manual+(v_max/1000)):.4f}</span></div><div class="frp-item"><span>JUSTO </span><span class="blu">{(val_ptax_manual+(v_jus/1000)):.4f}</span></div><div class="frp-item"><span>MINIMA </span><span class="neg">{(val_ptax_manual+(v_min/1000)):.4f}</span></div></div>', unsafe_allow_html=True)

            # DXY / EWZ
            st.markdown(f'<div class="asset-row"><div class="name">DXY INDEX</div><div class="price">{d_at:.2f}</div><div class="var {"pos" if v_dxy >= 0 else "neg"}">{v_dxy:+.2f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_at:.2f}</div><div class="var {"pos" if v_ewz >= 0 else "neg"}">{v_ewz:+.2f}%</div></div>', unsafe_allow_html=True)

            # TRAVA
            st.markdown(f'<div class="trava-orange">TRAVA 16H: {trava_exibir:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
