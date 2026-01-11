import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

st.set_page_config(layout="wide")

# Conexão sem cache para atualizar na hora
conn = st.connection("gsheets", type=GSheetsConnection)

def buscar_dados():
    try:
        # Tenta ler a aba Sheet1. Se falhar, avisa o erro na tela.
        df = conn.read(worksheet="Sheet1", ttl=0)
        return float(df.iloc[0, 0]), float(df.iloc[0, 1])
    except Exception as e:
        st.error(f"ERRO DE CONEXÃO: Verifique se a aba chama-se 'Sheet1'. Detalhe: {e}")
        return 0.0, 0.0

# Interface simplificada para teste
aj, ref = buscar_dados()

st.title("TESTE DE CONEXÃO")
st.metric("AJUSTE ATUAL", f"{aj:.4f}")
st.metric("REFERENCIAL ATUAL", f"{ref:.4f}")

if st.button("FORÇAR ATUALIZAÇÃO"):
    st.rerun()

time.sleep(3)
st.rerun()
