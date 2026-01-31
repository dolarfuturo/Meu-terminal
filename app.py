import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="TERMINAL", layout="wide")

@st.cache_resource
def get_vars():
    return {"ajuste": 5.4000, "v_jus": 1.0041, "ref": 5.4000}

v_global = get_vars()

# 2. LOGIN
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    senha = st.text_input("CHAVE", type="password")
    if st.button("ENTRAR"):
        if senha == "admin123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. DADOS
def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        last = t.fast_info.last_price
        prev = t.fast_info.previous_close
        return {"last": last, "prev": prev, "var": ((last - prev) / prev * 100)}
    except: return {"last": 0.0, "prev": 0.0, "var": 0.0}

# 4. TERMINAL
@st.fragment(run_every=2)
def monitor():
    d_m, e_m, s_m = get_data("DX-Y.NYB"), get_data("EWZ"), get_data("BRL=X")
    
    # Trava de Segurança contra erro 5.1604
    agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
    spot_real = s_m["last"]
    fechamento = s_m["prev"]
    
    # Se o preço do Yahoo fugir do ajuste (erro detectado), usa fechamento
    if abs(spot_real - v_global["ajuste"]) > 0.15 or agora.hour >= 18:
        spot = fechamento
    else:
        spot = spot_real

    v_spot = ((spot - fechamento) / fechamento * 100) if fechamento != 0 else 0
    paridade = v_global["ajuste"] * (1 + ((d_m["var"] - e_m["var"])/100))
    justo = round((spot * v_global["v_jus"]) * 2000) / 2000

    # Layout Simples (Sem aspas triplas para não quebrar)
    st.title(f"{spot:.4f}")
    st.subheader(f"Variação: {v_spot:+.2f}%")
    st.write(f"PARIDADE: {paridade:.4f} | JUSTO: {justo:.4f}")
    st.write(f"DXY: {d_m['var']:+.2f}% | EWZ: {e_m['var']:+.2f}%")

    with st.expander("ADM"):
        v_global["ajuste"] = st.number_input("AJUSTE", value=v_global["ajuste"], format="%.4f")
        if st.button("SALVAR"): st.rerun()

monitor()
