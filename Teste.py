import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(page_title="K97 - TERMINAL FINAL", layout="wide")

# --- CÁLCULO AUTOMÁTICO DO EIXO (MÁX+MÍN)/2 DO PREGÃO ANTERIOR ---
@st.cache_data(ttl=600)
def calcular_eixo_automatico():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="5d", interval="15m", prepost=False)
        if df.empty: return 37.85, 0, 0
        
        datas = df.index.normalize().unique()
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        
        # Se for noite, já olha para o pregão de hoje como referência
        data_ref = datas[-1] if agora.hour >= 18 else datas[-2]
        
        df_dia = df.loc[data_ref.strftime('%Y-%m-%d')]
        # Filtra o horário oficial: 10:30 às 17:00 BRT
        df_sessao = df_dia.between_time('09:30', '16:00')
        
        mx = df_sessao['High'].max()
        mn = df_sessao['Low'].min()
        eixo = (mx + mn) / 2
        return eixo, mx, mn
    except:
        return 37.85, 0, 0

# --- MOTOR DE CÁLCULO K97 ---
def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 1.5
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 3
        dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
        
        # --- CÁLCULO SINTÉTICO MÉDIO (50% DA MÁX/MÍN DO DIA) ---
        ewz_medio_dia = (max_ewz + min_ewz) / 2
        var_medio = ((eixo_ewz / ewz_medio_dia) - 1) * 100 
        dolar_medio = eixo_dol * (1 + (var_medio / 100)) 
        
        v_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2
        v_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2
        alvo_max = eixo_dol * (1 + (v_pos / 100))
        alvo_min = eixo_dol * (1 + (v_neg / 100))
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, 
            "v_atual": var_atual, "ewz_med": ewz_medio_dia,
            "max": alvo_max, "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), 
            "p50_up": (eixo_dol + alvo_max) / 2, 
            "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25),
            "min": alvo_min, "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), 
            "p50_down": (eixo_dol + alvo_min) / 2, 
            "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
        }
    except: return None

@st.cache_data(ttl=2)
def fetch_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        if df.empty: return None
        return {
            "at": df['Close'].iloc[-1], 
            "mx_real": df['High'].max(), 
            "mn_real": df['Low'].min()
        }
    except: return None

# --- ESTILO VISUAL ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .vivo-box { background: #161b22; border: 2px solid #ffcc00; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 10px; }
    .medio-box { background: #1e2226; border-left: 5px solid #00f2ff; padding: 10px; text-align: center; border-radius: 4px; margin-bottom: 10px; }
    .fraja-box { background: #1c1c1c; border: 1px dashed #ffffff; padding: 10px; text-align: center; border-radius: 8px; }
    .price-row-mini { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 16px; font-weight: bold; }
    .eixo-box-mini { background: #1e2226; border: 1px solid #00f2ff; padding: 5px; text-align: center; margin: 5px 0; border-radius: 4px; }
    .label-k97 { color: #00f2ff; font-size: 12px; font-weight: bold; }
    .valor-vivo { font-size: 42px; font-family: 'Arial Black'; color: #ffcc00; line-height: 1; }
    .realtime-box { font-size: 14px; color: #888; margin-top: 5px; font-family: 'monospace'; }
    .ewz-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; background: #000; padding: 8px; border-radius: 4px; margin-top: 10px; text-align: center; font-size: 12px; }
</style>""", unsafe_allow_html=True)

# Lógica de Inicialização
eixo_sugerido, mx_ref, mn_ref = calcular_eixo_automatico()

with st.sidebar:
    st.header("⚙️ AJUSTE")
    e_ewz = st.number_input("EIXO EWZ:", value=float(eixo_sugerido), format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f")
    st.markdown("---")
    st.write(f"Ref. Calculada: **{eixo_sugerido:.2f}**")
    st.write(f"MAX EWZ ONTEM: **{mx_ref:.2f}**")
    st.write(f"MIN EWZ ONTEM: **{mn_ref:.2f}**")

data = fetch_data()

if data:
    res = calcular_k97_total(e_ewz, data["at"], data["mx_real"], data["mn_real"], e_dol)
    if res:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown(f'<div class="vivo-box"><div class="label-k97">SINTÉTICO (2.0)</div><div class="valor-vivo">{res["vivo"]:.2f}</div></div>', unsafe_allow_html=True)
            
            # ADICIONADO: SINTÉTICO MÉDIO (50% DIA)
            st.markdown(f'<div class="medio-box"><div class="label-k97">SINTÉTICO MÉDIO (50% DIA)</div><div style="font-size:25px; font-weight:bold; color:#00f2ff;">{res["medio"]:.2f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="fraja-box"><div class="label-k97">SINTÉTICO (3.6)</div><div style="font-size:25px; font-weight:bold;">{res["fraja"]:.2f}</div></div>', unsafe_allow_html=True)
            
            st.metric("EWZ VIVO", f"{data['at']:.2f}", delta=f"{res['v_atual']:+.2f}%")
            
            # ADICIONADO: MONITOR EWZ (MAX | MED | MIN)
            st.markdown(f"""
            <div class="ewz-grid">
                <div><span style="color:#ff4d4d">MAX</span><br><b>{data['mx_real']:.2f}</b></div>
                <div><span style="color:#00f2ff">MED</span><br><b>{res['ewz_med']:.2f}</b></div>
                <div><span style="color:#00ff88">MIN</span><br><b>{data['mn_real']:.2f}</b></div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f'<div class="price-row-mini" style="color:#ff4d4d; border-top: 2px solid #ff4d4d;"><span>MÁXIMA</span> <span>{res["max"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ff7675;"><span>75% UP</span> <span>{res["p75_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#fab1a0;"><span>50% UP</span> <span>{res["p50_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ffeaa7;"><span>25% UP</span> <span>{res["p25_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="eixo-box-mini"><div class="label-k97">EIXO: {e_dol:.2f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ffeaa7;"><span>25% DN</span> <span>{res["p25_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#81ecec;"><span>50% DN</span> <span>{res["p50_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#55efc4;"><span>75% DN</span> <span>{res["p75_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#00ff88; border-bottom: 2px solid #00ff88;"><span>MÍNIMA</span> <span>{res["min"]:.2f}</span></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
