import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Configurações Básicas
st.set_page_config(page_title="ATA", layout="centered")

# 2. Inicialização do Estado
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS - Estilo Terminal Puro (Sem quadros, tudo alinhado à esquerda)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    /* Fonte Terminal em tudo */
    * {
        font-family: 'Roboto Mono', monospace !important;
        text-transform: uppercase;
        background-color: #000000;
        color: #FFFFFF;
    }

    /* Remove lixo do topo */
    header { visibility: hidden; display: none !important; }
    .block-container { padding-top: 1rem !important; }

    /* Título ATA */
    .title-ata {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 30px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }

    /* Linha de Ativo: Nome | Preço | Variação */
    .row {
        display: flex;
        align-items: baseline;
        gap: 15px;
        margin-bottom: 25px;
    }

    .name { width: 140px; font-size: 14px; color: #888; text-align: left; }
    .price { font-size: 26px; font-weight: bold; color: #FFFFFF; }
    .var { font-size: 18px; font-weight: bold; }

    /* Ajuste específico para o Alvo Spread */
    .price-alvo { color: #FFB900 !important; }

    /* FRP Vertical (Alinhado abaixo do Spot) */
    .frp-container {
        margin-left: 140px;
        margin-top: -15px;
        margin-bottom: 25px;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    .frp-line { display: flex; gap: 20px; font-size: 16px; font-weight: bold; }

    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }
    .blue { color: #0080FF !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. Acesso às Variáveis (SET)
with st.expander("CONFIG «"):
    c1, c2 = st.columns(2)
    val_aj_manual = c1.number_input("AJUSTE", value=5.3900, format="%.4f")
    v_min = c2.number_input("PTS MIN", value=22.0)
    v_jus = c1.number_input("PTS JUS", value=31.0)
    v_max = c2.number_input("PTS MAX", value=42.0)
    if st.button("LIMPAR TRAVA"):
        st.session_state.spot_ref_locked = None

st.markdown('<div class="title-ata">ATA</div>', unsafe_allow_html=True)

def get_data(ticker):
    try:
        return yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
    except: return pd.DataFrame()

# 5. Loop Principal
placeholder = st.empty()

while True:
    with placeholder.container():
        spot_df = get_data("BRL=X")
        dxy_df = get_data("DX-Y.NYB")
        ewz_df = get_data("EWZ")

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

            # --- RENDERIZAÇÃO ---

            # ALVO SPREAD
            st.markdown(f'''
                <div class="row">
                    <div class="name">ALVO SPREAD</div>
                    <div class="price price-alvo">{alvo:.4f}</div>
                    <div class="var {"positive" if spread >= 0 else "negative"}">{spread:+.2f}%</div>
                </div>
            ''', unsafe_allow_html=True)

            # USD/BRL SPOT
            st.markdown(f'''
                <div class="row">
                    <div class="name">USD/BRL SPOT</div>
                    <div class="price">{spot_at:.4f}</div>
                    <div class="var {"positive" if v_s >= 0 else "negative"}">{v_s:+.2f}%</div>
                </div>
            ''', unsafe_allow_html=True)

            # PONTOS (Abaixo do Spot)
            st.markdown(f'''
                <div class="frp-container">
                    <div class="frp-line"><span>MIN</span><span class="negative">{spot_at + (v_min/1000):.4f}</span></div>
                    <div class="frp-line"><span>JUS</span><span class="blue">{spot_at + (v_jus/1000):.4f}</span></div>
                    <div class="frp-line"><span>MAX</span><span class="positive">{spot_at + (v_max/1000):.4f}</span></div>
                </div>
            ''', unsafe_allow_html=True)

            # DXY
            st.markdown(f'''
                <div class="row">
                    <div class="name">DXY INDEX</div>
                    <div class="price">{d_at:.2f}</div>
                    <div class="var {"positive" if v_dxy >= 0 else "negative"}">{v_dxy:+.2f}%</div>
                </div>
            ''', unsafe_allow_html=True)

            # EWZ
            st.markdown(f'''
                <div class="row">
                    <div class="name">EWZ ADR</div>
                    <div class="price">{e_at:.2f}</div>
                    <div class="var {"positive" if v_ewz >= 0 else "negative"}">{v_ewz:+.2f}%</div>
                </div>
            ''', unsafe_allow_html=True)

            # TRAVA
            st.markdown(f'<div style="font-size:12px; color:#444; margin-left:140px;">TRAVA 16H: {trava_val:.4f}</div>', unsafe_allow_html=True)

    time.sleep(2)
