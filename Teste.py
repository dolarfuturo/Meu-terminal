import streamlit as st
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import hashlib  # Necessário para a segurança

# 1. SETUP ALPHA
st.set_page_config(page_title="ALPHA VISION LIVE", layout="wide", initial_sidebar_state="collapsed")

# --- SISTEMA DE GESTÃO DE ALUGUEL (GOOGLE SHEETS) ---
def verificar_acesso():
    # URL DO SEU CSV (Substitua pelo link que você vai gerar no Google Sheets)
    URL_SISTEMA = "COLE_AQUI_O_LINK_DO_SEU_CSV_PUBLICO"
    
    if "autenticado" not in st.session_state:
        st.markdown("""
            <style>
            .login-box {
                background-color: #080808;
                padding: 40px;
                border-radius: 10px;
                border: 1px solid #D4AF37;
                text-align: center;
            }
            </style>
            <div class="login-box">
                <h1 style='color: #D4AF37;'>ALPHA VISION LOGIN</h1>
                <p style='color: white;'>Terminal de Dados Cripto - Acesso Restrito</p>
            </div>
        """, unsafe_allow_html=True)
        
        chave = st.text_input("Insira sua Chave de Licença:", type="password")
        
        if chave:
            try:
                # Lê a planilha de controle
                df = pd.read_csv(URL_SISTEMA)
                hash_tentativa = hashlib.sha256(chave.encode()).hexdigest()
                
                # Valida se o Hash existe e se o Status é ATIVO
                valido = df[(df['Hash_Senha'] == hash_tentativa) & (df['Status'] == 'ATIVO')]
                
                if not valido.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = valido.iloc[0]['Cliente']
                    st.rerun()
                else:
                    st.error("❌ Licença Inválida ou Mensalidade em Atraso.")
            except Exception as e:
                st.error("Erro ao conectar com o servidor de licenças. Verifique o link do banco de dados.")
        
        st.stop() # Interrompe o script se não estiver logado

# Executa a trava antes de carregar o terminal
verificar_acesso()

# --- DAQUI PARA BAIXO SEGUE O SEU CÓDIGO ORIGINAL ---

COINS_CONFIG = {
    "BTC-USD": {"label": "BTC/USDT", "dec": 0},
    "ETH-USD": {"label": "ETH/USDT", "dec": 0},
    "SOL-USD": {"label": "SOL/USDT", "dec": 2},
    "XRP-USD": {"label": "XRP/USDT", "dec": 2},
    "BNB-USD": {"label": "BNB/USDT", "dec": 4},
    "DOGE-USD": {"label": "DOGE/USDT", "dec": 4},
    "LINK-USD": {"label": "LINK/USDT", "dec": 4},
    "ADA-USD": {"label": "ADA/USDT", "dec": 2},
    "AVAX-USD": {"label": "AVAX/USDT", "dec": 2},
    "DOT-USD": {"label": "DOT/USDT", "dec": 2},
    "MATIC-USD": {"label": "MATIC/USDT", "dec": 4},
    "PEPE-USD": {"label": "PEPE/USDT", "dec": 4},
    "SUI-USD": {"label": "SUI/USDT", "dec": 2},
    "NEAR-USD": {"label": "NEAR/USDT", "dec": 2},
    "APT-USD": {"label": "APT/USDT", "dec": 6},
    "OP-USD": {"label": "OP/USDT", "dec": 3},
    "ARB-USD": {"label": "ARB/USDT", "dec": 2},
    "INJ-USD": {"label": "INJ/USDT", "dec": 2},
    "RNDR-USD": {"label": "RNDR/USDT", "dec": 3},
    "HYPE-USD": {"label": "HYPE/USDT", "dec": 4}
}

# ... (Continue com suas funções get_calculation_date, get_alpha_midpoint e o Loop While True)
