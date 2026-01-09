import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL DE CÂMBIO", layout="wide")

# 2. Memória da Sessão
if 'spot_ref_locked' not in st.session_state: 
    st.session_state.spot_ref_locked = None

# 3. CSS BITMAP DOT (Fonte Estilo Matrix / Vídeo Antigo)
st.markdown("""
    <style>
    /* Fonte Bitmap Dot */
    @import url('https://fonts.googleapis.com/css2?family=DotGothic16&display=swap');

    html, body, [class*="st-"], div, span, p {
        font-family: 'DotGothic16', sans-serif !important;
        text-transform: uppercase;
    }

    .stApp { 
        background-color: #000000; 
        color: #FFFFFF; 
    }

    /* Título Branco Estilo Vídeo Antigo */
    .terminal-header {
        padding: 10px 0px;
        border-bottom: 3px double #FFFFFF;
        margin-bottom: 20px;
    }

    .terminal-title {
        font-size: 30px;
        color: #FFFFFF;
        letter-spacing: 5px;
        text-shadow: 2px 2px #333;
    }

    /* Linhas de Ativos */
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0px;
        border-bottom: 1px solid #1a1a1a;
        background-color: #000000;
    }

    /* Ativos em Branco */
    .ticker-name { 
        font-size: 18px; 
        color: #FFFFFF; 
        width: 180px;
        letter-spacing: 1px;
    }

    /* Preços em Amarelo */
    .ticker-price { 
        font-size: 28px; 
        color: #FFB900; 
        width: 160px; 
        text-align: right;
    }

    .ticker-var { font-size: 22px; width: 110px; text-align: right; }

    /* FRP Container */
    .frp-container { display: flex; gap: 20px; }
    .frp-item { text-align: right; }
    .frp-label { font-size: 12px; color: #555; display: block; }
    .frp-value { font-size: 20px; }

    /* Cores de Variação */
    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }

    /* Bloco Alvo com Spread Colorido */
    .alvo-box {
        background-color: #050505;
        border: 1px solid #222;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #FFB900;
    }
    .alvo-label { font-size: 18px; color: #FFFFFF; margin-bottom: 8px; }
    .alvo-price { font-size: 40px; color: #FFB900; }
    
    /* Efeito de Scanline (Opcional - Estilo Vídeo Antigo) */
    .stApp::before {
        content: " ";
        display: block;
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        z-index: 2;
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Funções de Dados
def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 5. Sidebar
with st.sidebar:
    st.markdown("### SETTINGS")
    val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f")
    st.divider()
    v_min = st.number_input("PTS MIN", value=22.0)
    v_jus = st.number_input("PTS JUS", value=31.0)
    v_max = st.number_input("PTS MAX", value=42.0)
    if st.button("RESET 16H"): st.session_state.spot_ref_locked = None

# 6. Loop de Renderização
placeholder = st.empty()
while True:
    with placeholder.container():
        st.markdown('<div class="terminal-header"><div class="terminal-title">TERMINAL DE CAMBIO</div></div>', unsafe_allow_html=True)

        spot_df = get_live_data("BRL=X")
        dxy_df = get_live_data("DX-Y.NYB")
        ewz_df = get_live_data("EWZ")
        now_br = datetime.now() - timedelta(hours=3)
        is_pre = now_br.time() < datetime.strptime("11:30", "%H:%M").time()

        if not spot_df.empty:
            spot_at = float(spot_df['Close'].iloc[-1])
            
            # Trava 16h
            try:
                lock_data = spot_df.between_time('15:58', '16:02')
                if not lock_data.empty and st.session_state.spot_ref_locked is None:
                    st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
            except: pass
            trava_16 = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

            # Globais
            d_at = float(dxy_df['Close'].iloc[-1]) if not dxy_df.empty else 0
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0]) * 100) if not dxy_df.empty else 0
            
            e_at = float(ewz_df['Close'].iloc[-1]) if not ewz_df.empty else 0
            ref_e = float(ewz_df['Close'].iloc[0]) if is_pre and not ewz_df.empty else (float(ewz_df['Open'].iloc[0]) if not ewz_df.empty else 1)
            v_ewz = ((e_at - ref_e) / ref_e * 100) if not ewz_df.empty else 0

            # Spread e Alvo Colorido
            spread = v_dxy - v_ewz
            alvo = val_aj_manual * (1 + (spread/100))
            spread_color = "positive" if spread >= 0 else "negative"

            # DISPLAY ALVO
            st.markdown(f"""
                <div class="alvo-box">
                    <div class="alvo-label">ALVO SPREAD (SINAL: <span class="{spread_color}">{spread:+.2f}%</span>)</div>
                    <div class="alvo-price">{alvo:.4f}</div>
                </div>
            """, unsafe_allow_html=True)

            # USD/BRL SPOT
            v_s = ((spot_at - val_aj_manual) / val_aj_manual * 100)
            st.markdown(f"""
                <div class="ticker-row">
                    <div class="ticker-name">USD/BRL SPOT</div>
                    <div class="ticker-price">{spot_at:.4f}</div>
                    <div class="ticker-var {'positive' if v_s >= 0 else 'negative'}">{v_s:+.2f}%</div>
                    <div class="frp-container">
                        <div class="frp-item"><span class="frp-label">MIN</span><span class="frp-value negative">{spot_at + (v_min/1000):.4f}</span></div>
                        <div class="frp-item"><span class="frp-label">JUS</span><span class="frp-value" style="color:#0080FF;">{spot_at + (v_jus/1000):.4f}</span></div>
                        <div class="frp-item"><span class="frp-label">MAX</span><span class="frp-value positive">{spot_at + (v_max/1000):.4f}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # DXY e EWZ
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">DXY INDEX</div><div class="ticker-price">{d_at:.2f}</div><div class="ticker-var {"positive" if v_dxy >= 0 else "negative"}">{v_dxy:+.2f}%</div><div style="width:350px;"></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">EWZ {"(PRE)" if is_pre else "(REG)"}</div><div class="ticker-price">{e_at:.2f}</div><div class="ticker-var {"positive" if v_ewz >= 0 else "negative"}">{v_ewz:+.2f}%</div><div style="width:350px;"></div></div>', unsafe_allow_html=True)

            # TRAVA
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">TRAVA 16H</div><div class="ticker-price" style="color:#555;">{trava_16h:.4f}</div><div class="ticker-var" style="color:#333;">LOCKED</div><div style="width:350px;"></div></div>', unsafe_allow_html=True)

        st.caption(f"SYSTEM RUNNING - {now_br.strftime('%H:%M:%S')}")
    time.sleep(2)
