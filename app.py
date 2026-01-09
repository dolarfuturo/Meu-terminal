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

# 3. CSS TOTAL CUSTOMIZADO (Fonte Pixel/Square e Cores)
st.markdown("""
    <style>
    /* Importação da fonte pixelada quadrada estilo terminal antigo */
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    /* Aplicação da fonte em tudo */
    html, body, [class*="st-"], div, span, p, h1, h2, h3 {
        font-family: 'VT323', monospace !important;
        text-transform: uppercase;
    }

    .stApp { 
        background-color: #000000; 
        color: #FFFFFF; 
    }

    /* Título do Topo Branco */
    .terminal-header {
        padding: 5px 0px;
        border-bottom: 2px solid #FFFFFF;
        margin-bottom: 15px;
    }

    .terminal-title {
        font-size: 35px;
        color: #FFFFFF;
        letter-spacing: 2px;
    }

    /* Linhas de Ativos */
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0px;
        border-bottom: 1px solid #222;
        background-color: #000000;
    }

    /* Nomes dos ativos em BRANCO */
    .ticker-name { 
        font-size: 22px; 
        color: #FFFFFF; 
        width: 180px; 
    }

    /* Preços em Amarelo */
    .ticker-price { 
        font-size: 32px; 
        color: #FFB900; 
        width: 160px; 
        text-align: right; 
    }

    .ticker-var { font-size: 24px; width: 110px; text-align: right; }

    /* Pontos FRP */
    .frp-container { display: flex; gap: 25px; }
    .frp-item { text-align: right; }
    .frp-label { font-size: 16px; color: #888; display: block; }
    .frp-value { font-size: 24px; font-weight: bold; }

    /* Cores */
    .positive { color: #00FF00 !important; }
    .negative { color: #FF0000 !important; }

    /* Caixa do Alvo */
    .alvo-box {
        background-color: #080808;
        border: 1px solid #444;
        padding: 15px;
        margin-bottom: 20px;
    }
    .alvo-label { font-size: 20px; color: #FFFFFF; margin-bottom: 5px; }
    .alvo-price { font-size: 45px; color: #FFB900; }

    </style>
    """, unsafe_allow_html=True)

# 4. Funções e Dados
def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 5. Renderização Principal
with st.sidebar:
    st.markdown("### CONFIG")
    val_aj_manual = st.number_input("AJUSTE", value=5.3900, format="%.4f")
    st.divider()
    v_min = st.number_input("MIN", value=22.0)
    v_jus = st.number_input("JUS", value=31.0)
    v_max = st.number_input("MAX", value=42.0)

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

            # Alvo
            spread = v_dxy - v_ewz
            alvo = val_aj_manual * (1 + (spread/100))

            # --- DISPLAY ---
            st.markdown(f'<div class="alvo-box"><div class="alvo-label">ALVO SPREAD (AJUSTE {spread:+.2f}%)</div><div class="alvo-price">{alvo:.4f}</div></div>', unsafe_allow_html=True)

            # SPOT
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

            # DXY
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">DXY INDEX</div><div class="ticker-price">{d_at:.2f}</div><div class="ticker-var {"positive" if v_dxy >= 0 else "negative"}">{v_dxy:+.2f}%</div><div style="width:350px;"></div></div>', unsafe_allow_html=True)

            # EWZ
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">EWZ {"(PRE)" if is_pre else "(REG)"}</div><div class="ticker-price">{e_at:.2f}</div><div class="ticker-var {"positive" if v_ewz >= 0 else "negative"}">{v_ewz:+.2f}%</div><div style="width:350px;"></div></div>', unsafe_allow_html=True)

            # TRAVA
            st.markdown(f'<div class="ticker-row"><div class="ticker-name">TRAVA 16H</div><div class="ticker-price" style="color:#555;">{trava_16:.4f}</div><div class="ticker-var" style="color:#444;">FIXO</div><div style="width:350px;"></div></div>', unsafe_allow_html=True)

    time.sleep(2)
