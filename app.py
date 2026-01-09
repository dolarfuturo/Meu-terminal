import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração
st.set_page_config(page_title="BLOOMBERG | PREÇO ALVO", layout="wide")

# 2. CSS Compacto
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stMetricValue"] { font-size: 20px !important; color: #FFB900 !important; }
    .alvo-box { background-color: #111; border: 1px solid #FFB900; padding: 10px; text-align: center; border-radius: 5px; margin-bottom: 15px; }
    .spread-box { border: 1px dashed #444; padding: 5px; background-color: #050505; text-align: center; font-size: 13px; }
    .frp-box { border: 1px solid #333; padding: 8px; background-color: #000; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar com Inputs
with st.sidebar:
    st.header("📊 INPUTS")
    val_ajuste = st.number_input("Ajuste DOL (Manual)", value=5.3900, format="%.4f")
    st.divider()
    v_min = st.number_input("Mín FRP", value=22.0)
    v_justo = st.number_input("Justo FRP", value=31.0)
    v_max = st.number_input("Máx FRP", value=42.0)

def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 4. Processamento
placeholder = st.empty()
with placeholder.container():
    spot_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    now_br = datetime.now() - timedelta(hours=3)
    is_pre_market = now_br.time() < datetime.strptime("11:30", "%H:%M").time()

    if not spot_df.empty:
        spot_at = float(spot_df['Close'].iloc[-1])
        
        # Cálculos de Variação
        v_dxy = 0.0
        if not dxy_df.empty:
            v_dxy = ((d_at := float(dxy_df['Close'].iloc[-1])) - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0]) * 100
            
        v_ewz_final = 0.0
        if not ewz_df.empty:
            ewz_at = float(ewz_df['Close'].iloc[-1])
            ref_ewz = float(ewz_df['Close'].iloc[0]) if is_pre_market else float(ewz_df['Open'].iloc[0])
            v_ewz_final = ((ewz_at - ref_ewz) / ref_ewz) * 100

        # SPREAD E PREÇO ALVO
        spread_val = v_dxy - v_ewz_final
        preco_alvo = val_ajuste * (1 + (spread_val / 100))
        distancia = ((spot_at - preco_alvo) / preco_alvo) * 100

        # --- EXIBIÇÃO ---
        
        # Bloco de Destaque: Preço Alvo
        st.markdown(f"""
            <div class="alvo-box">
                <span style="color:#AAA; font-size:12px;">PREÇO ALVO PELO SPREAD (AJUSTE + SPREAD)</span><br>
                <span style="font-size:28px; font-weight:bold; color:#FFB900;">{preco_alvo:.4f}</span><br>
                <span style="font-size:14px; color:{'#00FF00' if spread_val >= 0 else '#FF4B4B'};">Spread: {spread_val:.2f}%</span>
            </div>
        """, unsafe_allow_html=True)

        # Métricas Principais
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AJUSTE INFORMADO", f"{val_ajuste:.4f}")
        c2.metric("SPOT ATUAL", f"{spot_at:.4f}", f"{((spot_at-val_ajuste)/val_ajuste*100):.2f}%")
        c3.metric("DXY", f"{d_at if not dxy_df.empty else 0:.2f}", f"{v_dxy:.2f}%")
        c4.metric("EWZ " + ("PRE" if is_pre_market else "REG"), f"{ewz_at if not ewz_df.empty else 0:.2f}", f"{v_ewz_final:.2f}%")

        # Projeções FRP (Sobre o Spot Atual)
        st.write("")
        p1, p2, p3 = st.columns(3)
        p1.markdown(f'<div class="frp-box"><span style="color:#FF4B4B; font-size:10px;">MÍN (+{v_min})</span><br><span style="color:#FF4B4B; font-size:18px; font-weight:bold;">{spot_at + (v_min/1000):.4f}</span></div>', unsafe_allow_html=True)
        p2.markdown(f'<div class="frp-box"><span style="color:#0080FF; font-size:10px;">JUSTO (+{v_justo})</span><br><span style="color:#0080FF; font-size:18px; font-weight:bold;">{spot_at + (v_justo/1000):.4f}</span></div>', unsafe_allow_html=True)
        p3.markdown(f'<div class="frp-box"><span style="color:#00FF00; font-size:10px;">MÁX (+{v_max})</span><br><span style="color:#00FF00; font-size:18px; font-weight:bold;">{spot_at + (v_max/1000):.4f}</span></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
