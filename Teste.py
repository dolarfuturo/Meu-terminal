import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# Configuração para Tablet
st.set_page_config(page_title="K97 - EIXO AUTO 10:30-17:00", layout="wide")

# --- FUNÇÃO PARA PEGAR EIXO AUTOMÁTICO (MAX+MIN/2 do pregão anterior) ---
@st.cache_data(ttl=3600)
def calcular_eixo_dinamico():
    try:
        t = yf.Ticker("EWZ")
        # Puxa 5 dias para garantir que pegamos o último pregão útil completo
        df = t.history(period="5d", interval="15m", prepost=False)
        if df.empty: return 37.85
        
        # Pega a data do último pregão fechado (ontem útil)
        datas = df.index.normalize().unique()
        data_referencia = datas[-2] 
        
        # Filtra o dia e o horário específico de Brasília (convertido para NY aprox.)
        df_dia = df.loc[data_referencia.strftime('%Y-%m-%d')]
        # 10:30 BR -> 09:30 NY | 17:00 BR -> 16:00 NY
        df_full_session = df_dia.between_time('09:30', '16:00')
        
        mx = df_full_session['High'].max()
        mn = df_full_session['Low'].min()
        return (mx + mn) / 2
    except:
        return 37.85

@st.cache_data(ttl=2)
def fetch_data():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        return {"at": df['Close'].iloc[-1], "mx": df['High'].max(), "mn": df['Low'].min()} if not df.empty else None
    except: return None

# --- MOTOR DE CÁLCULO K97 ---
def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 2
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 3.6
        dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
        
        # Alvos baseados na volatilidade do dia atual
        v_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2
        v_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2
        alvo_max = eixo_dol * (1 + (v_pos / 100))
        alvo_min = eixo_dol * (1 + (v_neg / 100))
        
        p50_up = (eixo_dol + alvo_max) / 2
        p25_up = (eixo_dol + p50_up) / 2
        p75_up = (p50_up + alvo_max) / 2
        p50_down = (eixo_dol + alvo_min) / 2
        p25_down = (eixo_dol + p50_down) / 2
        p75_down = (p50_down + alvo_min) / 2
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "v_atual": var_atual,
            "max": alvo_max, "p75_up": p75_up, "p50_up": p50_up, "p25_up": p25_up,
            "min": alvo_min, "p75_down": p75_down, "p50_down": p50_down, "p25_down": p25_down
        }
    except: return None

# --- ESTILO ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .vivo-box { background: #161b22; border: 2px solid #ffcc00; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 10px; }
    .fraja-box { background: #1c1c1c; border: 1px dashed #ffffff; padding: 10px; text-align: center; border-radius: 8px; }
    .price-row-mini { display: flex; justify-content: space-between; padding: 4px 8px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 16px; font-weight: bold; }
    .eixo-box-mini { background: #1e2226; border: 1px solid #00f2ff; padding: 5px; text-align: center; margin: 5px 0; border-radius: 4px; }
    .label-k97 { color: #00f2ff; font-size: 12px; font-weight: bold; }
    .valor-vivo { font-size: 42px; font-family: 'Arial Black'; color: #ffcc00; line-height: 1; }
</style>""", unsafe_allow_html=True)

# Lógica de Dados
eixo_auto = calcular_eixo_dinamico()
data = fetch_data()

with st.sidebar:
    st.header("⚙️ AJUSTE")
    # O valor padrão agora é o cálculo automático do pregão anterior
    e_ewz = st.number_input("EIXO EWZ (AUTO):", value=float(eixo_auto), format="%.2f")
    e_dol = st.number_input("EIXO DOLFUT:", value=5219.50, format="%.2f")

if data:
    res = calcular_k97_total(e_ewz, data["at"], data["mx"], data["mn"], e_dol)
    if res:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown(f'<div class="vivo-box"><div class="label-k97">SINTÉTICO (2.0)</div><div class="valor-vivo">{res["vivo"]:.2f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="fraja-box"><div class="label-k97">SINTÉTICO (3.6)</div><div style="font-size:25px; font-weight:bold;">{res["fraja"]:.2f}</div></div>', unsafe_allow_html=True)
            st.metric("EWZ VIVO", f"{data['at']:.2f}", delta=f"{res['v_atual']:+.2f}%")
        with c2:
            st.markdown(f'<div class="price-row-mini" style="color:#ff4d4d; border-top: 2px solid #ff4d4d;"><span>MÁXIMA</span> <span>{res["max"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ff7675;"><span>75% UP</span> <span>{res["p75_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#fab1a0;"><span>50% UP</span> <span>{res["p50_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ffeaa7;"><span>25% UP</span> <span>{res["p25_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="eixo-box-mini"><div class="label-k97">EIXO DOL: {e_dol:.2f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#ffeaa7;"><span>25% DN</span> <span>{res["p25_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#81ecec;"><span>50% DN</span> <span>{res["p50_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#55efc4;"><span>75% DN</span> <span>{res["p75_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row-mini" style="color:#00ff88; border-bottom: 2px solid #00ff88;"><span>MÍNIMA</span> <span>{res["min"]:.2f}</span></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
