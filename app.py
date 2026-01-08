import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="BLOOMBERG | EWZ DUAL SESSION", layout="wide")

# 2. Memória da Sessão
if 'history' not in st.session_state: st.session_state.history = []
if 'spot_ref_locked' not in st.session_state: st.session_state.spot_ref_locked = None

# 3. Estilo Visual
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #FFB900 !important; font-family: 'Courier New', monospace; font-size: 24px !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: 800 !important; }
    .frp-box { border: 1px solid #333333; padding: 15px; background-color: #000000; text-align: center; }
    .spread-box { border: 1px dashed #555555; padding: 10px; background-color: #111111; text-align: center; margin-top: 10px; }
    .price-text { font-size: 24px; font-family: 'Courier New'; font-weight: bold; }
    .history-table { width: 100%; border-collapse: collapse; font-family: 'Courier New'; font-size: 14px; color: white; }
    .history-table td { border-bottom: 1px solid #222; padding: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 4. Ajustes Laterais
with st.sidebar:
    st.title("Ajustes de Fluxo")
    v_min = st.number_input("Mínima FRP", value=22.0)
    v_justo = st.number_input("Justo FRP", value=31.0)
    v_max = st.number_input("Máxima FRP", value=42.0)

def get_live_data(ticker):
    try:
        # Pega 2 dias com prepost=True para garantir o fechamento de ontem e o pre-market de hoje
        data = yf.download(ticker, period="2d", interval="1m", progress=False, prepost=True)
        return data
    except: return pd.DataFrame()

placeholder = st.empty()
with placeholder.container():
    spot_df = get_live_data("BRL=X")
    dxy_df = get_live_data("DX-Y.NYB")
    ewz_df = get_live_data("EWZ")

    now_br = datetime.now() - timedelta(hours=3)
    hora_br_str = now_br.strftime("%H:%M:%S")
    time_1130 = datetime.strptime("11:30", "%H:%M").time()

    if not spot_df.empty:
        spot_at = float(spot_df['Close'].iloc[-1])
        
        # Trava 16h Automática
        try:
            lock_data = spot_df.between_time('15:58', '16:02')
            if not lock_data.empty and st.session_state.spot_ref_locked is None:
                st.session_state.spot_ref_locked = float(lock_data['Close'].iloc[-1])
        except: pass
        
        ref_val = st.session_state.spot_ref_locked if st.session_state.spot_ref_locked else float(spot_df['Open'].iloc[0])

        # Grid de Cabeçalho (DXY e SPOT)
        c1, c2, c3 = st.columns([1,1,1])
        c1.metric("SPOT 16:00 REF", f"{ref_val:.4f}")
        
        v_spot = ((spot_at - ref_val) / ref_val) * 100
        c2.metric("SPOT ATUAL", f"{spot_at:.4f}", f"{v_spot:.2f}%")
        
        v_dxy = 0.0
        if not dxy_df.empty:
            d_at = float(dxy_df['Close'].iloc[-1])
            v_dxy = ((d_at - float(dxy_df['Open'].iloc[0])) / float(dxy_df['Open'].iloc[0])) * 100
            c3.metric("DXY INDEX", f"{d_at:.2f}", f"{v_dxy:.2f}%")

        # Seção EWZ: PRÉ vs REGULAR
        st.markdown("---")
        e1, e2 = st.columns(2)
        
        v_ewz_final = 0.0 # Para usar no Spread
        
        if not ewz_df.empty:
            ewz_at = float(ewz_df['Close'].iloc[-1])
            
            # Cálculo Pré-Mercado (Sempre comparando com Fechamento de Ontem)
            fech_ontem = float(ewz_df['Close'].iloc[0]) 
            v_pre = ((ewz_at - fech_ontem) / fech_ontem) * 100
            
            # Cálculo Regular (Sempre comparando com Abertura de Hoje 11:30)
            abert_hoje = float(ewz_df['Open'].iloc[0])
            v_reg = ((ewz_at - abert_hoje) / abert_hoje) * 100

            # Exibição Condicional
            if now_br.time() < time_1130:
                e1.metric("EWZ PRE-MARKET (vs ONTEM)", f"{ewz_at:.2f}", f"{v_pre:.2f}%")
                e2.write("Mercado Regular abre às 11:30")
                v_ewz_final = v_pre
            else:
                e1.metric("EWZ PRE-MARKET (FECHADO)", f"{ewz_at:.2f}", f"{v_pre:.2f}%", delta_color="off")
                e2.metric("EWZ REGULAR (vs ABERTURA)", f"{ewz_at:.2f}", f"{v_reg:.2f}%")
                v_ewz_final = v_reg

        # Spread Linkado
        spread = v_dxy - v_ewz_final
        cor_spread = "#00FF00" if spread >= 0 else "#FF0000"
        st.markdown(f'<div class="spread-box">SPREAD DXY-EWZ ATIVO: <span style="color:{cor_spread}; font-size:22px; font-weight:bold;">{spread:.2f}%</span></div>', unsafe_allow_html=True)

        # Projeções FRP
        st.markdown("---")
        p1, p2, p3 = st.columns(3)
        p1.markdown(f'<div class="frp-box"><span style="color:#FF0000;">MÍN (+{v_min})</span><br><span class="price-text" style="color:#FF0000;">{spot_at + (v_min/1000):.4f}</span></div>', unsafe_allow_html=True)
        p2.markdown(f'<div class="frp-box"><span style="color:#0080FF;">JUSTO (+{v_justo})</span><br><span class="price-text" style="color:#0080FF;">{spot_at + (v_justo/1000):.4f}</span></div>', unsafe_allow_html=True)
        p3.markdown(f'<div class="frp-box"><span style="color:#00FF00;">MÁX (+{v_max})</span><br><span class="price-text" style="color:#00FF00;">{spot_at + (v_max/1000):.4f}</span></div>', unsafe_allow_html=True)

        # Histórico
        if not st.session_state.history or st.session_state.history[0]['Preço'] != spot_at:
            st.session_state.history.insert(0, {'Hora': hora_br_str, 'Preço': spot_at})
            st.session_state.history = st.session_state.history[:5]

        st.markdown(f"### 📜 TAPE READING SPOT (BR: {hora_br_str})")
        hist_html = "<table class='history-table'><tr><th>Hora</th><th>Preço</th><th>Sentido</th></tr>"
        for i, row in enumerate(st.session_state.history):
            s_seta = ""
            if i < len(st.session_state.history) - 1:
                if row['Preço'] > st.session_state.history[i+1]['Preço']: s_seta = "<span style='color:#00FF00;'>▲</span>"
                elif row['Preço'] < st.session_state.history[i+1]['Preço']: s_seta = "<span style='color:#FF0000;'>▼</span>"
            hist_html += f"<tr><td>{row['Hora']}</td><td>{row['Preço']:.4f}</td><td>{s_seta}</td></tr>"
        st.markdown(hist_html + "</table>", unsafe_allow_html=True)

time.sleep(2)
st.rerun()
