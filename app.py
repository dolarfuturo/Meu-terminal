import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. Configuração de Tela Compacta
st.set_page_config(page_title="Slim Pro", layout="centered")
st_autorefresh(interval=5000, key="datarefresh") 

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=JetBrains+Mono:wght@700&display=swap');
    
    /* Fundo Preto e Redução de Margens */
    .stApp { background-color: #000000 !important; }
    .block-container { padding: 0.2rem !important; max-width: 250px !important; margin: 0 auto; }
    
    /* Cabeçalho Minimalista */
    .header-box {
        font-family: 'JetBrains Mono', monospace; color: #FFFFFF; font-size: 11px;
        text-align: center; border-bottom: 1px solid #333; padding-bottom: 2px; margin-bottom: 5px;
    }

    /* Estilo das Métricas */
    [data-testid="stMetricValue"] {
        font-family: 'Share Tech Mono', monospace !important;
        color: #ffffff !important; font-size: 18px !important; line-height: 1 !important;
    }
    
    [data-testid="stMetricLabel"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 9px !important; color: #ff9900 !important; margin-bottom: -8px !important;
    }

    [data-testid="stMetricDelta"] { font-size: 10px !important; }

    /* Cores Específicas */
    div[data-testid="stMetric"]:has(p:contains("FUTURO")) div[data-testid="stMetricValue"] { color: #FFFF00 !important; }
    .max-box div[data-testid="stMetricValue"] { color: #00FF66 !important; }
    .min-box div[data-testid="stMetricValue"] { color: #FF0033 !important; }

    /* Ajuste de Espaçamento entre Linhas */
    [data-testid="stMetric"] { border-bottom: 1px solid #111; padding: 1px 0 !important; margin-bottom: -18px !important; }
    
    .st-expanderHeader { background-color: #000 !important; font-size: 8px !important; height: 20px !important; }

    /* --- RODAPÉ AJUSTADO (MAIOR) --- */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; border-top: 2px solid #ff9900;
        position: fixed; bottom: 0; left: 0; 
        padding: 8px 0; /* Aumentado de 2px para 8px */
        height: 40px;   /* Altura fixa
