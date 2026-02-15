import streamlit as st
import pandas as pd
import hashlib

# 1. SETUP DO TERMINAL K97 (SHAKE VISION)
st.set_page_config(page_title="ALPHA VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

def verificar_acesso():
    # URL que força o Google a entregar os dados mais recentes
    URL_SISTEMA = "https://docs.google.com/spreadsheets/d/1m86_Lj5p7tV9U4sNIKudbU1DVWFgAfaSXSIRATo6G70/gviz/tq?tqx=out:csv"
    
    if "autenticado" not in st.session_state:
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>ALPHA VISION LOGIN</h1>", unsafe_allow_html=True)
        
        chave = st.text_input("Insira sua Chave de Licença:", type="password")
        
        if chave:
            try:
                # Lendo a planilha
                df = pd.read_csv(URL_SISTEMA)
                
                # NORMALIZAÇÃO TOTAL: Remove espaços e coloca tudo em MAIÚSCULO no cabeçalho
                df.columns = [str(c).strip().upper() for c in df.columns]
                
                # Criptografa a tentativa
                hash_tentativa = hashlib.sha256(chave.encode()).hexdigest()
                
                # Filtra removendo espaços das células também
                df['STATUS'] = df['STATUS'].astype(str).str.strip().upper()
                df['HASH_SENHA'] = df['HASH_SENHA'].astype(str).str.strip()

                valido = df[(df['HASH_SENHA'] == hash_tentativa) & (df['STATUS'] == 'ATIVO')]
                
                if not valido.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = valido.iloc[0]['CLIENTE']
                    st.rerun()
                else:
                    # Mostra o erro e ajuda a diagnosticar
                    st.error("❌ Acesso Negado.")
                    with st.expander("Ver detalhes técnicos"):
                        st.write("Colunas detectadas:", list(df.columns))
                        st.write("Status lido:", df['STATUS'].tolist())
            except Exception as e:
                st.error(f"Erro de conexão: {e}")
        st.stop()

verificar_acesso()
st.success(f"Conectado: {st.session_state['usuario']}")
