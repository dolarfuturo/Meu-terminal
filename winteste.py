import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(page_title="K97 INDEX - TERMINAL", layout="wide")

# Função para formatar milhar (Ex: 130.500)
def fmt_m(valor):
    try:
        return f"{int(valor):,}".replace(",", ".")
    except:
        return str(valor)

# --- CÁLCULO AUTOMÁTICO DO EIXO EWZ (TRAVA DAS 18H) ---
@st.cache_data(ttl=600)
def calcular_eixo_automatico():
    try:
        t = yf.Ticker("EWZ")
        # Pegamos 7 dias para cobrir finais de semana e feriados
        df = t.history(period="7d", interval="1d", prepost=False)
        if df.empty: return 37.85, 0, 0
        
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        hoje = agora.date()
        ultima_data_yahoo = df.index[-1].date()
        
        # --- LÓGICA DA SENTINELA: Reset apenas às 18h ---
        if ultima_data_yahoo == hoje and agora.hour < 18:
            idx = -2 # Mantém o eixo do pregão anterior (Ontem)
        else:
            idx = -1 # Assume o novo fechamento após as 18h
            
        mx = df['High'].iloc[idx]
        mn = df['Low'].iloc[idx]
        eixo = (mx + mn) / 2
        
        return eixo, mx, mn
    except: 
        return 37.85, 0, 0

# --- MOTOR DE CÁLCULO K97 INDEX (CALIBRADO +1.22) ---
def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_index):
    try:
        v_pura = ((p_ewz_atual / eixo_ewz) - 1) * 100 
        index_vivo = eixo_index * (1 + (v_pura / 100))
        index_fraja = eixo_index * (1 + (v_pura / 100))
        
        ewz_medio_dia = (max_ewz + min_ewz) / 2
        var_medio = ((p_ewz_atual / ewz_medio_dia) - 1) * 100
        index_medio = eixo_index * (1 + (var_medio / 100)) 
        
        # Calibragem de Amplitude WIN (+1.22) - Mantida conforme sua estratégia
        v_neg = ((min_ewz / eixo_ewz) - 1) * 100 -0.9
        v_pos = ((max_ewz / eixo_ewz) - 1) * 100 + 0.65
        alvo_max = eixo_index * (1 + (v_pos / 100))  
        alvo_min = eixo_index * (1 + (v_neg / 100)) 
        
        return {
            "vivo": index_vivo, "fraja": index_fraja, "medio": index_medio, 
            "v_atual": v_pura, "ewz_med": ewz_medio_dia,
            "max": alvo_max, "p75_up": (eixo_index + (alvo_max - eixo_index)*0.75), 
            "p50_up": (eixo_index + alvo_max) / 2, 
            "p25_up": (eixo_index + (alvo_max - eixo_index)*0.25),
            "min": alvo_min, "p75_down": (eixo_index + (alvo_min - eixo_index)*0.75), 
            "p50_down": (eixo_index + alvo_min) / 2, 
            "p25_down": (eixo_index + (alvo_min - eixo_index)*0.25)
        }
    except: return None

@st.cache_data(ttl=2)
def fetch_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        if df.empty: return None
        return {"at": df['Close'].iloc[-1], "mx_real": df['High'].max(), "mn_real": df['Low'].min()}
    except: return None

# --- ESTILO VISUAL (CIANO E AMARELO) ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .vivo-box { background: #161b22; border: 2px solid #00f2ff; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 10px; }
    .medio-box { background: #1e2226; border-left: 5px solid #ffcc00; padding: 10px; text-align: center; border-radius: 4px; margin-bottom: 10px; }
    .fraja-box { background: #1c1c1c; border: 1px dashed #ffffff; padding: 10px; text-align: center; border-radius: 8px; }
    .price-row-mini { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 16px; font-weight: bold; }
    .eixo-box-mini { background: #1e2226; border: 1px solid #ffcc00; padding: 5px; text-align: center; margin: 5px 0; border-radius: 4px; }
    .label-k97 { color: #ffcc00; font-size: 12px; font-weight: bold; }
    .valor-vivo { font-size: 42px; font-family: 'Arial Black'; color: #00f2ff; line-height: 1; }
    .mini-info { font-size: 10px; color: #848d96; text-align: center; }
</style>""", unsafe_allow_html=True)

e_sug, mx_ref, mn_ref = calcular_eixo_automatico()

with st.sidebar:
    st.header("⚙️ AJUSTE WIN")
    e_ewz = st.number_input("EIXO EWZ:", value=float(e_sug), format="%.2f")
    e_index = st.number_input("EIXO WIN:", value=130500, step=50, format="%d")
    st.markdown("---")
    st.write(f"Ref. Calculada: **{e_sug:.2f}**")
    st.write(f"MAX EWZ ONTEM: **{mx_ref:.2f}**")
    st.write(f"MIN EWZ ONTEM: **{mn_ref:.2f}**")

data = fetch_data()

if data:
    res = calcular_k97_total(e_ewz, data["at"], data["mx_real"], data["mn_real"], e_index)
    if res:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown(f'<div class="vivo-box"><div class="label-k97">SINTÉTICO INDEX (2.0)</div><div class="valor-vivo">{fmt_m(res["vivo"])}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="medio-box"><div class="label-k97">SINTÉTICO MÉDIO</div><div style="font-size:25px; font-weight:bold; color:#ffcc00;">{fmt_m(res["medio"])}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="fraja-box"><div class="label-k97">SINTÉTICO (3.6)</div><div style="font-size:25px; font-weight:bold;">{fmt_m(res["fraja"])}</div></div>', unsafe_allow_html=True)
            
            st.metric("EWZ VIVO", f"{data['at']:.2f}", delta=f"{res['v_atual']:+.2f}%")
            
            m1, m2, m3 = st.columns(3)
            m1.markdown(f'<div class="mini-info">MAX<br><b style="color:#ff4d4d">{data["mx_real"]:.2f}</b></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="mini-info">MED<br><b style="color:#ffffff">{res["ewz_med"]:.2f}</b></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="mini-info">MIN<br><b style="color:#00ff88">{data["mn_real"]:.2f}</b></div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown(f'<div class="price-row-mini" style="color:#00ff88; border-top: 2px solid #00ff88;"><span>MÁXIMA</span> <span>{fmt_m(res["max"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#55efc4;"><span>75% UP</span> <span>{fmt_m(res["p75_up"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#81ecec;"><span>50% UP</span> <span>{fmt_m(res["p50_up"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ffeaa7;"><span>25% UP</span> <span>{fmt_m(res["p25_up"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="eixo-box-mini"><div class="label-k97">EIXO: {fmt_m(e_index)}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ffeaa7;"><span>25% DN</span> <span>{fmt_m(res["p25_down"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#fab1a0;"><span>50% DN</span> <span>{fmt_m(res["p50_down"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ff7675;"><span>75% DN</span> <span>{fmt_m(res["p75_down"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ff4d4d; border-bottom: 2px solid #ff4d4d;"><span>MÍNIMA</span> <span>{fmt_m(res["min"])}</span></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
