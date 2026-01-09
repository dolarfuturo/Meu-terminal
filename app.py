import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="TERMINAL BLOOMBERG", layout="wide")

# 2. Memória da Sessão
if 'spot_ref_locked' not in st.session_state: st.session_state.spot_ref_locked = None

# 3. Estilo CSS Terminal (Letras Quadradas e Alinhamento)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Roboto Mono', monospace; }
    
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px;
        border-bottom: 1px solid #222;
        background-color: #050505;
    }
    
    .ticker-name { font-size: 13px; font-weight: bold; color: #888; width: 150px; }
    .ticker-price { font-size: 20px; font-weight: bold; color: #FFB900; width: 150px; text-align: right; }
    .ticker-var { font-size: 15px; width: 100px; text-align: right; font-weight: bold; }
    
    .frp-label { font-size: 9px; color: #555; text-transform: uppercase; }
    .frp-value { font-size: 15px; font-weight: bold; margin-right: 15px; }
    
    .positive { color: #00FF00; }
    .negative { color: #FF4B4B; }
    
    .alvo-box {
        background-color: #0A0A0A;
        border-left: 4px solid #FFB900;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 0 4px 4px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Sidebar de Configuração
with st.sidebar:
    st.header("⚙️ CONFIG")
    val_ajuste_manual = st.number_input("Ajuste DOL (Manual)", value=5.3900, format="%.4f")
    st.divider()
    v_min = st.number_input("Pts Mín", value=22.0)
    v_justo = st.number_input("Pts Justo", value=31.0)
    v_max = st.number_input("Pts Máx", value=42.0)
    if st.button("Resetar Trava 16h"): st.session_state.spot_ref_locked = None

def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 5. Processamento de Dados
placeholder = st.empty()
with placeholder.container():
    spot_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    now_br = datetime.now() - timedelta(hours=3)
    hora_br = now_br.strftime("%H:%M:%S")
    is_pre_market = now_br.time() < datetime.strptime("11:30", "%H:%M").time()

    if not spot_df.empty:
        spot_at = float(spot_df['Close'].iloc[-1])
        
        # Lógica Trava 16h
        try:
            lock_data = spot_df.between_time('15:58', '16:02')
            if not lock_data.empty and st.session_state.spot_ref_locked is None:
                st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
        except: pass
        
        trava_16h = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else spot_at

        # Variações DXY e EWZ
        v_dxy = 0.0
        d_price = 0.0
        if not dxy_df.empty:
            d_price = float(dxy_df['Close'].iloc[-1])
            v_dxy = ((d_price - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0])) * 100
        
        v_ewz = 0.0
        e_price = 0.0
        if not ewz_df.empty:
            e_price = float(ewz_df['Close'].iloc[-1])
            ref_ewz = float(ewz_df['Close'].iloc[0]) if is_pre_market else float(ewz_df['Open'].iloc[0])
            v_ewz = ((e_price - ref_ewz) / ref_ewz) * 100

        # Spread e Preço Alvo
        spread_total = v_dxy - v_ewz
        alvo_calc = val_ajuste_manual * (1 + (spread_total / 100))

        # --- EXIBIÇÃO ---
        
        # 1. BLOCO DE DESTAQUE (ALVO)
        st.markdown(f"""
            <div class="alvo-box">
                <div style="font-size:11px; color:#888;">ALVO PELO SPREAD (AJUSTE + SPREAD)</div>
                <div style="font-size:28px; font-weight:bold; color:#FFB900;">{alvo_calc:.4f} 
                <span style="font-size:14px; color:{'#00FF00' if spread_total >= 0 else '#FF4B4B'}; font-family:sans-serif;"> ({spread_total:+.2f}%)</span></div>
            </div>
        """, unsafe_allow_html=True)

        # 2. LISTA DE ATIVOS (UM EMBAIXO DO OUTRO)
        
        # USD/BRL SPOT
        v_spot_ajuste = ((spot_at - val_ajuste_manual) / val_ajuste_manual) * 100
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">USD/BRL SPOT</div>
                <div class="ticker-price">{spot_at:.4f}</div>
                <div class="ticker-var {'positive' if v_spot_ajuste >= 0 else 'negative'}">{v_spot_ajuste:+.2f}%</div>
                <div style="display:flex; width: 400px; justify-content: flex-end;">
                    <div style="text-align:right;"><span class="frp-label">MÍN</span><br><span class="frp-value" style="color:#FF4B4B;">{spot_at + (v_min/1000):.4f}</span></div>
                    <div style="text-align:right;"><span class="frp-label">JUSTO</span><br><span class="frp-value" style="color:#0080FF;">{spot_at + (v_justo/1000):.4f}</span></div>
                    <div style="text-align:right;"><span class="frp-label">MÁX</span><br><span class="frp-value" style="color:#00FF00;">{spot_at + (v_max/1000):.4f}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # TRAVA 16H
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">TRAVA 16:00</div>
                <div class="ticker-price" style="color:#888;">{trava_16h:.4f}</div>
                <div class="ticker-var" style="color:#444;">FIXO</div>
                <div style="width: 400px; text-align: right; color: #444; font-size: 11px;">Ref. Fechamento Anterior</div>
            </div>
        """, unsafe_allow_html=True)

        # DXY
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">DXY INDEX</div>
                <div class="ticker-price">{d_price:.2f}</div>
                <div class="ticker-var {'positive' if v_dxy >= 0 else 'negative'}">{v_dxy:+.2f}%</div>
                <div style="width: 400px; text-align: right; color: #444; font-size: 11px;">Dólar Global</div>
            </div>
        """, unsafe_allow_html=True)

        # EWZ
        label_ewz = "EWZ PRE" if is_pre_market else "EWZ REG"
        st.markdown(f"""
            <div class="ticker-row">
                <div class="ticker-name">{label_ewz}</div>
                <div class="ticker-price">{e_price:.2f}</div>
                <div class="ticker-var {'positive' if v_ewz >= 0 else 'negative'}">{v_ewz:+.2f}%</div>
                <div style="width: 400px; text-align: right; color: #444; font-size: 11px;">Brasil em NY</div>
            </div>
        """, unsafe_allow_html=True)

        st.caption(f"ATUALIZADO ÀS: {hora_br} BRT")

time.sleep(2)
st.rerun()
