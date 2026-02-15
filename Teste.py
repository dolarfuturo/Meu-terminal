import streamlit as st
import pandas as pd
import hashlib

# 1. SETUP DO TERMINAL K97 (SHAKE VISION)
st.set_page_config(page_title="ALPHA VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

# --- SISTEMA DE GESTÃO DE ACESSO ---
def verificar_acesso():
    # LINK DA SUA PLANILHA JÁ CONFIGURADO PARA EXPORTAÇÃO
    URL_SISTEMA = "https://docs.google.com/spreadsheets/d/1m86_Lj5p7tV9U4sNIKudbU1DVWFgAfaSXSIRATo6G70/export?format=csv"
    
    if "autenticado" not in st.session_state:
        st.markdown("""
            <style>
            .login-box {
                background-color: #080808;
                padding: 40px;
                border-radius: 10px;
                border: 2px solid #D4AF37;
                text-align: center;
            }
            </style>
            <div class="login-box">
                <h1 style='color: #D4AF37;'>ALPHA VISION LOGIN</h1>
                <p style='color: white;'>Terminal K97 - Shake Vision</p>
            </div>
        """, unsafe_allow_html=True)
        
        _, col2, _ = st.columns([1,2,1])
        with col2:
            chave = st.text_input("Insira sua Chave de Licença:", type="password")
        
        if chave:
            try:
                # O Python lê a planilha em tempo real
                df = pd.read_csv(URL_SISTEMA)
                
                # Criptografa a senha digitada para comparar
                hash_tentativa = hashlib.sha256(chave.encode()).hexdigest()
                
                # Validação nas colunas MAIÚSCULAS: CLIENTE, HASH_SENHA, STATUS
                valido = df[(df['HASH_SENHA'] == hash_tentativa) & (df['STATUS'] == 'ATIVO')]
                
                if not valido.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = valido.iloc[0]['CLIENTE']
                    st.rerun()
                else:
                    st.error("❌ Acesso Negado: Verifique sua licença ou pendências de amortização.")
            except Exception as e:
                st.error("Erro de conexão. Certifique-se de que a planilha está como 'Qualquer pessoa com o link'.")
        
        st.stop()

# Executa a trava
verificar_acesso()

# --- ABAIXO SEGUE O RESTANTE DO SEU CÓDIGO (MOEDAS, GRÁFICOS E VWAP) ---
st.success(f"Bem-vindo, {st.session_state['usuario']}! Conectado ao Terminal K97.")
