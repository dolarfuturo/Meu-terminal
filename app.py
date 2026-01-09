import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="BLOOMBERG COMPACT", layout="wide")

# 2. Memória da Sessão
if 'history' not in st.session_state: st.session_state.history = []
if 'spot_ref_locked' not in st.session_state: st.session_state.spot_ref_locked = None

# 3. CSS para Layout Reduzido
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stMetricValue"] { font-size: 20px !important; color: #FFB900 !important; }
    [data-testid="stMetricLabel"] { font-size: 12px !important; text-transform: uppercase; }
    .frp-box { border: 1px solid #333; padding: 8px; background-color: #000; text-align: center; border-radius: 4px; }
    .price-text { font-size: 18px; font-family: 'Courier New'; font-weight: bold; }
    .pre-market-mini { 
        background-color: #111; border: 1px solid #0080FF; padding: 5px; 
        border-radius: 4px; margin-top: -15px; text-align: center;
    }
    .spread-box { border: 1px dashed #444; padding: 5px; background-color: #050505; text-align: center; font-size: 14px; }
    .history-table { width: 100%; font-size: 12px; color: #ccc; }
    </style>
    """, unsafe_allow_html=True)

# 4. Sidebar Compacta
with st.sidebar:
    st.caption("AJUSTE FRP")
    v_min = st.number_input("Mín", value=22.0, step=1.0)
    v_justo = st.number_input("Justo", value=31.0, step=1.0)
    v_max = st.number_input("Máx", value=42.0, step=1.0)

def get_live_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

# 5. Execução
placeholder = st.empty()
with placeholder.container():
    spot_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    now_br = datetime.now() - timedelta(hours=3)
    hora_br_str = now_br.strftime("%H:%M:%S")
    is_pre_market = now_br.time() < datetime.strptime("11:30", "%H:%M").time()

    if not spot_df.empty:
        spot_at = float(spot_df['Close'].iloc[-1])
        
        # Trava 16h
        try:
            lock_data = spot_df.between_time('15:58', '16:02')
            if not lock_data.empty and st.session_state.spot_ref_locked is None:
                st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
        except: pass
        
        ref_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else float(spot_df['Open'].iloc[0])

        # LINHA 1: MÉTRICAS PRINCIPAIS
        c1, c2, c3, c4 = st.columns(4)
        
        c1.metric("REF 16:00", f"{ref_val:.4f}")
        
        v_spot = ((spot_at - ref_val) / ref_val) * 100
        c2.metric("SPOT ATUAL", f"{spot_at:.4f}", f"{v_spot:.2f}%")
        
        v_dxy = 0.0
        if not dxy_df.empty:
            d_at = float(dxy_df['Close'].iloc[-1])
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0])) * 100
            c3.metric("DXY", f"{d_at:.2f}", f"{v_dxy:.2f}%")
            
        v_ewz_reg = 0.0
        if not ewz_df.empty:
            ewz_at = float(ewz_df['Close'].iloc[-1])
            # Variação Regular (sempre baseada na abertura do dia)
            ref_reg = float(ewz_df['Open'].iloc[0])
            v_ewz_reg = ((ewz_at - ref_reg) / ref_reg) * 100
            c4.metric("EWZ REGULAR", f"{ewz_at:.2f}", f"{v_ewz_reg:.2f}%")

        # LINHA 2: PRÉ-MARKET (SÓ APARECE ANTES DAS 11:30)
        v_ewz_final = v_ewz_reg
        if is_pre_market and not ewz_df.empty:
            fech_ontem = float(ewz_df['Close'].iloc[0])
            v_pre = ((ewz_at - fech_ontem) / fech_ontem) * 100
            v_ewz_final = v_pre # Linka o Spread ao Pré-mercado
            
            _, _, _, c4_sub = st.columns(4)
            with c4_sub:
                st.markdown(f"""
                <div class="pre-market-mini">
                    <span style="font-size:10px; color:#0080FF;">PRE-MARKET</span><br>
                    <span style="font-size:14px; font-weight:bold;">{ewz_at:.2f}</span> 
                    <span style="font-size:12px; color:{'#00FF00' if v_pre >= 0 else '#FF0000'};">{v_pre:.2f}%</span>
                </div>
                """, unsafe_allow_html=True)

        # SPREAD
        spread = v_dxy - v_ewz_final
        cor_spread = "#00FF00" if spread >= 0 else "#FF0000"
        st.markdown(f'<div class="spread-box">SPREAD DXY-EWZ: <span style="color:{cor_spread}; font-weight:bold;">{spread:.2f}%</span></div>', unsafe_allow_html=True)

        # PROJEÇÕES FRP (Compactas)
        st.write("")
        p1, p2, p3 = st.columns(3)
        p1.markdown(f'<div class="frp-box"><span style="color:#FF4B4B; font-size:10px;">MÍN (+{v_min})</span><br><span class="price-text" style="color:#FF4B4B;">{spot_at + (v_min/1000):.4f}</span></div>', unsafe_allow_html=True)
        p2.markdown(f'<div class="frp-box"><span style="color:#0080FF; font-size:10px;">JUSTO (+{v_justo})</span><br><span class="price-text" style="color:#0080FF;">{spot_at + (v_justo/1000):.4f}</span></div>', unsafe_allow_html=True)
        p3.markdown(f'<div class="frp-box"><span style="color:#00FF00; font-size:10px;">MÁX (+{v_max})</span><br><span class="price-text" style="color:#00FF00;">{spot_at + (v_max/1000):.4f}</span></div>', unsafe_allow_html=True)

        # HISTÓRICO
        if not st.session_state.history or st.session_state.history[0]['Preço'] != spot_at:
            st.session_state.history.insert(0, {'Hora': hora_br_str, 'Preço': spot_at})
            st.session_state.history = st.session_state.history[:3] # Só 3 linhas para encurtar

        st.write("")
        hist_html = "<table class='history-table'>"
        for row in st.session_state.history:
            hist_html += f"<tr><td>{row['Hora']}</td><td style='text-align:right;'>{row['Preço']:.4f}</td></tr>"
        st.markdown(hist_html + "</table>", unsafe_allow_html=True)

time.sleep(2)
st.rerun()
