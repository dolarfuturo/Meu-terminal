import streamlit as st
import yfinance as yf
import time
from datetime import datetime, timedelta
import pytz

# Configuração para Tablet
st.set_page_config(page_title="K97 - ARBITRAGE SYSTEM", layout="wide")

# --- LÓGICA DE EIXO FIXO (10:30 - 17:00) ---
@st.cache_data(ttl=3600) # Atualiza a lógica a cada hora, mas mantém o dia fixo
def calcular_eixo_estrito():
    try:
        t = yf.Ticker("EWZ")
        # Pegamos 5 dias para garantir que teremos o último pregão completo
        df = t.history(period="5d", interval="15m", prepost=False)
        if df.empty: return 37.85, 38.20, 37.50
        
        datas_disponiveis = df.index.normalize().unique()
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        
        # Se for antes das 18:00, o eixo é de ontem. 
        # Se for após as 18:00, o eixo já pode ser o de hoje (pois o pregão acabou).
        if agora.hour < 18:
            data_referencia = datas_disponiveis[-2] # Penúltimo dia
        else:
            data_referencia = datas_disponiveis[-1] # Último dia (hoje)
            
        df_dia = df.loc[data_referencia.strftime('%Y-%m-%d')]
        
        # Filtro Rigoroso: 10:30 às 17:00 BRT (NY 09:30 às 16:00)
        df_sessao = df_dia.between_time('09:30', '16:00')
        
        mx = df_sessao['High'].max()
        mn = df_sessao['Low'].min()
        eixo = (mx + mn) / 2
        return eixo, mx, mn
    except:
        return 37.85, 38.20, 37.50

# --- MOTOR K97 ---
def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        # Variação Sintética
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 2
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 3.6
        dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
        
        # Cálculo da Escada via Máxima/Mínima Realtime do EWZ
        v_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 2
        v_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 2
        alvo_max = eixo_dol * (1 + (v_pos / 100))
        alvo_min = eixo_dol * (1 + (v_neg / 100))
        
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "v_atual": var_atual,
            "max": alvo_max, "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), 
            "p50_up": (eixo_dol + alvo_max) / 2, 
            "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25),
            "min": alvo_min, "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), 
            "p50_down": (eixo_dol + alvo_min) / 2, 
            "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
        }
    except: return None

@st.cache_data(ttl=2)
def fetch_realtime():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="1d", interval="1m", prepost=True)
        if df.empty: return None
        return {"at": df['Close'].iloc[-1], "mx": df['High'].max(), "mn": df['Low'].min()}
    except: return None

# --- UI / DESIGN ---
st.markdown("""<style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    .vivo-box { background: #161b22; border: 2px solid #ffcc00; padding: 15px; text-align: center; border-radius: 8px; }
    .valor-vivo { font-size: 50px; font-family: 'Arial Black'; color: #ffcc00; line-height: 1; }
    .price-row { display: flex; justify-content: space-between; padding: 5px 10px; border-bottom: 1px solid #2d333b; font-family: 'monospace'; font-size: 18px; font-weight: bold; }
    .eixo-info { color: #00f2ff; font-size: 14px; font-weight: bold; margin-bottom: 20px; text-transform: uppercase; }
</style>""", unsafe_allow_html=True)

# Execução
eixo_fixo, mx_ref, mn_ref = calcular_eixo_estrito()

with st.sidebar:
    st.header("K97 CONTROL")
    # Agora o DOLFUT é a única variável que você ajusta conforme o ajuste do dia
    e_dol = st.number_input("AJUSTE DOLFUT (B3):", value=5219.50, step=0.5)
    st.markdown("---")
    st.markdown(f'<div class="eixo-info">Eixo EWZ Fixo: {eixo_fixo:.2f}</div>', unsafe_allow_html=True)
    st.write(f"Ref. Horário: 10:30 - 17:00")
    st.write(f"Max Ref: {mx_ref:.2f} | Min Ref: {mn_ref:.2f}")

data = fetch_realtime()

if data:
    res = calcular_k97_total(eixo_fixo, data["at"], data["mx"], data["mn"], e_dol)
    if res:
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown(f'<div class="vivo-box"><div style="color:#00f2ff; font-size:12px;">SINTÉTICO (2.0)</div><div class="valor-vivo">{res["vivo"]:.2f}</div></div>', unsafe_allow_html=True)
            st.metric("EWZ VIVO", f"{data['at']:.2f}", delta=f"{res['v_atual']:+.2f}%")
            st.write(f"Sintético (3.6): **{res['fraja']:.2f}**")
            st.markdown(f"**MAX REAL:** <span style='color:#ff4d4d'>{data['mx']:.2f}</span>", unsafe_allow_html=True)
            st.markdown(f"**MIN REAL:** <span style='color:#00ff88'>{data['mn']:.2f}</span>", unsafe_allow_html=True)

        with col2:
            st.markdown(f'<div class="price-row" style="color:#ff4d4d; border-top: 2px solid #ff4d4d;"><span>MÁXIMA</span> <span>{res["max"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#ff7675;"><span>75% UP</span> <span>{res["p75_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#fab1a0;"><span>50% UP</span> <span>{res["p50_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#ffeaa7;"><span>25% UP</span> <span>{res["p25_up"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center; color:#00f2ff; padding: 10px 0; font-weight:bold;">EIXO DOLFUT: {e_dol:.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#ffeaa7;"><span>25% DN</span> <span>{res["p25_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#81ecec;"><span>50% DN</span> <span>{res["p50_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#55efc4;"><span>75% DN</span> <span>{res["p75_down"]:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-row" style="color:#00ff88; border-bottom: 2px solid #00ff88;"><span>MÍNIMA</span> <span>{res["min"]:.2f}</span></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
