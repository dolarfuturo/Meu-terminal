import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Configurações Iniciais - Sidebar aberta por padrão
st.set_page_config(page_title="TERMINAL", layout="wide", initial_sidebar_state="expanded")

# 2. Inicialização do Estado
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Estilo Limpo, Alinhado à Esquerda e Sem Quadros
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    /* Fonte Terminal em tudo */
    * {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
    }

    /* Fundo Preto e Texto Branco */
    .stApp { background-color: #000000; color: #FFFFFF; }

    /* Esconde o cabeçalho nativo do Streamlit */
    header[data-testid="stHeader"] { visibility: hidden; display: none !important; }
    
    /* Espaçamento do corpo */
    .block-container { padding-top: 1rem !important; max-width: 800px !important; margin-left: 20px; }

    /* Barra Lateral (SET) */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #333;
        width: 250px !important;
    }

    /* Título */
    .terminal-header {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 30px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }

    /* Linhas de Ativos - Tamanho Único */
    .asset-row {
        display: flex;
        gap: 25px;
        margin-bottom: 20px;
        align-items: center;
    }

    .name { width: 160px; font-size: 18px; color: #888; }
    .price { width: 120px; font-size: 18px; font-weight: bold; color: #FFFFFF; }
    .var { font-size: 18px; font-weight: bold; }

    /* Destaque Alvo Spread (mesmo tamanho, cor diferente) */
    .price-alvo { color: #FFB900 !important; }

    /* Pontos FRP */
    .frp-box {
        margin-left: 185px; /* Alinha abaixo do preço */
        margin-top: -10px;
        margin-bottom: 25px;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    .frp-item { display: flex; gap: 30px; font-size: 16px; font-weight: bold; }

    .pos { color: #00FF00 !important; }
    .neg { color: #FF0000 !important; }
    .blu { color: #0080FF !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. VARIÁVEIS NA ESQUERDA (SIDEBAR)
with st.sidebar:
    st.markdown("### SET «")
    st.markdown("---")
    val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f", step=0.0001)
    v_min = st.number_input("PTS MIN", value=22.0)
    v_jus = st.number_input("PTS JUS", value=31.0)
    v_max = st.number_input("PTS MAX", value=42.0)
    st.markdown("---")
    if st.button("LIMPAR TRAVA"):
        st.session_state.spot_ref_locked = None

# Título Principal
st.markdown('<div class="terminal-header">TERMINAL DE CAMBIO</div>', unsafe_allow_html=True)

def get_market_data(ticker):
    try:
        return yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
    except: return pd.DataFrame()

# 5. Loop de Atualização
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = get_market_data("BRL=X")
        dxy_df = get_market_data("DX-Y.NYB")
        ewz_df = get_market_data("EWZ")

        if not spot_df.empty:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Trava 16h
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
            alvo = val_aj_manual * (1 + (spread/100))
            v_s = ((spot_at - val_aj_manual) / val_aj_manual * 100)

            # RENDERIZAÇÃO VERTICAL ALINHADA
            
            # 1. ALVO SPREAD
            st.markdown(f'''
                <div class="asset-row">
                    <div class="name">ALVO SPREAD</div>
                    <div class="price price-alvo">{alvo:.4f}</div>
                    <div class="var {"pos" if spread >= 0 else "neg"}">{spread:+.2f}%</div>
                </div>
            ''', unsafe_allow_html=True)

            # 2. USD/BRL SPOT
            st.markdown(f'''
                <div class="asset-row">
                    <div class="name">USD/BRL SPOT</div>
                    <div class="price">{spot_at:.4f}</div>
                    <div class="var {"pos" if v_s >= 0 else "neg"}">{v_s:+.2f}%</div>
                </div>
            ''', unsafe_allow_html=True)

            # FRP PONTOS
            st.markdown(f'''
                <div class="frp-box">
                    <div class="frp-item"><span>MIN</span><span class="neg">{spot_at + (v_min/1000):.4f}</span></div>
                    <div class="frp-item"><span>JUS</span><span class="blu">{spot_at + (v_jus/1000):.4f}</span></div>
                    <div class="frp-item"><span>MAX</span><span class="pos">{spot_at + (v_max/1000):.4f}</span></div>
                </div>
            ''', unsafe_allow_html=True)

            # 3. DXY
            st.markdown(f'''
                <div class="asset-row">
                    <div class="name">DXY INDEX</div>
                    <div class="price">{d_at:.2f}</div>
                    <div class="var {"pos" if v_dxy >= 0 else "neg"}">{v_dxy:+.2f}%</div>
                </div>
            ''', unsafe_allow_html=True)

            # 4. EWZ
            st.markdown(f'''
                <div class="asset-row">
                    <div class="name">EWZ ADR</div>
                    <div class="price">{e_at:.2f}</div>
                    <div class="var {"pos" if v_ewz >= 0 else "neg"}">{v_ewz:+.2f}%</div>
                </div>
            ''', unsafe_allow_html=True)

            # 5. TRAVA
            st.markdown(f'<div style="font-size:14px; color:#444; margin-top:10px;">TRAVA 16H: {trava_val:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
