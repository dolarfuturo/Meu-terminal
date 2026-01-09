import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Configuração - Isso força a barra lateral (Sidebar) a ficar aberta
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="expanded")

# 2. Inicialização segura do estado
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Estilo Terminal, Cores e Tamanhos
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    * { font-family: 'Roboto Mono', monospace !important; text-transform: uppercase; }
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Limpeza do topo e erro 'KEYBOARD' */
    header[data-testid="stHeader"] { visibility: hidden; display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin-left: 10px; }

    /* Forçar Sidebar visível */
    [data-testid="stSidebar"] { background-color: #111111 !important; border-right: 1px solid #333; min-width: 250px !important; }

    .terminal-header {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 25px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }

    /* Linhas principais */
    .asset-row { display: flex; gap: 20px; margin-bottom: 15px; align-items: center; }
    .name { width: 160px; font-size: 18px; color: #888; text-align: left; }
    .price { width: 110px; font-size: 18px; font-weight: bold; color: #FFFFFF; }
    .var { font-size: 18px; font-weight: bold; }
    
    /* Paridade em Amarelo */
    .price-paridade { color: #FFB900 !important; }

    /* Bloco MAX/JUS/MIN - PEQUENO E SEM NEGRITO */
    .frp-box {
        margin-left: 180px;
        margin-top: -5px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        gap: 3px;
    }
    .frp-item { 
        display: flex; 
        gap: 25px; 
        font-size: 13px !important; 
        font-weight: 400 !important; 
        text-transform: uppercase;
    }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    
    /* Trava em Laranja */
    .trava-orange { color: #FF8C00 !important; font-size: 18px; margin-top: 15px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. VARIÁVEIS NA BARRA LATERAL (SIDEBAR - ESQUERDA)
with st.sidebar:
    st.markdown("### ⚙️ AJUSTE MANUAL")
    val_aj_manual = st.number_input("VALOR AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    st.markdown("---")
    st.markdown("### 📊 PONTOS (PTS)")
    v_max = st.number_input("MAXIMA (PTS)", value=42.0)
    v_jus = st.number_input("JUSTO (PTS)", value=31.0)
    v_min = st.number_input("MINIMA (PTS)", value=22.0)
    st.markdown("---")
    if st.button("LIMPAR TRAVA 16H"):
        st.session_state.spot_ref_locked = None

# Interface Principal
st.markdown('<div class="terminal-header">TERMINAL DE CAMBIO</div>', unsafe_allow_html=True)

def get_data(ticker):
    try:
        # Usando threads=False para evitar conflitos no Streamlit Cloud
        return yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
    except: return pd.DataFrame()

placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = get_data("BRL=X")
        dxy_df = get_data("DX-Y.NYB")
        ewz_df = get_data("EWZ")

        if not spot_df.empty:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Lógica da Trava
            try:
                lock = spot_df.between_time('15:58', '16:02')
                if not lock.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock['Close'].iloc[-1])
            except: pass
            trava_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

            # Cálculos
            d_at = float(dxy_df['Close'].iloc[-1]) if not dxy_df.empty else 0
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0]) * 100) if not dxy_df.empty else 0
            e_at = float(ewz_df['Close'].iloc[-1]) if not ewz_df.empty else 0
            v_ewz = ((e_at - float(ewz_df['Open'].iloc[0])) / float(ewz_df['Open'].iloc[0]) * 100) if not ewz_df.empty else 0

            spread = v_dxy - v_ewz
            paridade = val_aj_manual * (1 + (spread/100))
            v_s = ((spot_at - val_aj_manual) / val_aj_manual * 100)

            # --- RENDERIZAÇÃO (F-strings corrigidas para evitar SyntaxError) ---
            
            # PARIDADE (Antigo Alvo Spread)
            class_spread = "pos" if spread >= 0 else "neg"
            st.markdown(f'<div class="asset-row"><div class="name">PARIDADE</div><div class="price price-paridade">{paridade:.4f}</div><div class="var {class_spread}">{spread:+.2f}%</div></div>', unsafe_allow_html=True)
            
            # SPOT
            class_spot = "pos" if v_s >= 0 else "neg"
            st.markdown(f'<div class="asset-row"><div class="name">USD/BRL SPOT</div><div class="price">{spot_at:.4f}</div><div class="var {class_spot}">{v_s:+.2f}%</div></div>', unsafe_allow_html=True)

            # PONTOS (MAXIMA -> JUSTO -> MINIMA) - Pequenos e Sem Negrito
            st.markdown(f'''
                <div class="frp-box">
                    <div class="frp-item"><span>MAXIMA</span><span class="pos">{(spot_at + (v_max/1000)):.4f}</span></div>
                    <div class="frp-item"><span>JUSTO </span><span class="blu">{(spot_at + (v_jus/1000)):.4f}</span></div>
                    <div class="frp-item"><span>MINIMA </span><span class="neg">{(spot_at + (v_min/1000)):.4f}</span></div>
                </div>
            ''', unsafe_allow_html=True)

            # DXY e EWZ
            class_dxy = "pos" if v_dxy >= 0 else "neg"
            st.markdown(f'<div class="asset-row"><div class="name">DXY INDEX</div><div class="price">{d_at:.2f}</div><div class="var {class_dxy}">{v_dxy:+.2f}%</div></div>', unsafe_allow_html=True)
            
            class_ewz = "pos" if v_ewz >= 0 else "neg"
            st.markdown(f'<div class="asset-row"><div class="name">EWZ ADR</div><div class="price">{e_at:.2f}</div><div class="var {class_ewz}">{v_ewz:+.2f}%</div></div>', unsafe_allow_html=True)

            # TRAVA 16H (LARANJA)
            st.markdown(f'<div class="trava-orange">TRAVA 16H: {trava_val:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
