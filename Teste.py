import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS PARA COPIAR O LAYOUT DA IMAGEM EXATAMENTE
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #e0e0e0; }
    
    /* Título e Cabeçalho */
    .bair-title { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 32px; letter-spacing: 2px; }
    .header-box { text-align: center; border: 1px solid #1f2329; padding: 10px; border-radius: 4px; background: #161b22; }
    .clock-time { color: #ffffff; font-size: 24px; font-weight: bold; }
    .clock-label { color: #848e9c; font-size: 12px; }

    /* Estilo das Grades */
    .grid-border { border: 1px solid #00f2ff; border-radius: 5px; padding: 10px; height: 100%; }
    
    /* Painel de Cálculos */
    .calc-row { display: flex; justify-content: space-between; margin-bottom: 4px; font-family: 'Courier New', monospace; font-size: 15px; }
    .eixo-data { background: #00f2ff; color: #000; font-weight: bold; text-align: center; padding: 6px; margin: 10px 0; border-radius: 2px; }
    .perc-green { color: #00ff88; font-weight: bold; }
    .perc-red { color: #ff4d4d; font-weight: bold; }
    
    /* Tabelas */
    th { color: #00f2ff !important; border-bottom: 1px solid #00f2
