import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS: GRADE DE RETAS, RELÓGIOS ANALÓGICOS E PAINEL ADM
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    
    /* Título Robusto */
    .bair-text { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 30px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 30px; font-weight: 900; }
    
    /* Relógios e Cidades */
    .header-box { text-align: center; border: 1px solid #3d444d; padding: 5px; background: #161b22; border-radius: 2px; display: flex; align-items: center; justify-content: center; gap: 10px; }
    .clock-time { color: #ffffff; font-size: 18px; font-weight: 900; font-family: monospace; }
    .clock-label { color: #00f2ff; font-size: 11px; font-weight: 900; letter-spacing: 1px; }

    /* Relógio Analógico Simulado (CSS) */
    .analog-clock { width: 25px; height: 25px; border: 2px solid #ffcc00; border-radius: 50%; position: relative; }
    .analog-clock::after { content: ''; position: absolute; width: 2px; height: 8px; background: #fff; left: 50%; top: 20%; transform-origin: bottom; }

    /* GRADE DE RETAS (ESTILO DESENHO) */
    .main-border { 
        border: 2px solid #ffffff; 
        padding: 10px; 
        margin-bottom: 20px;
    }
    
    /* Linhas Horizontais nos Ativos */
    .asset-row { 
        border-bottom: 1px solid #ffffff; 
        padding: 8px 0;
        display: flex;
        justify-content: space-between;
    }
    
    /* Tabelas e Fontes Cheias */
    th { color: #00f2ff !important; font-size: 12px !important; border-bottom: 2px solid #00f2ff !important; font-weight: 900 !important; text-align: left; }
    td { font-size: 19px !important; font-family: 'Arial Black', sans-serif !important; font-weight: 900 !important; padding: 10px 5px !important; }
    .asset-tag { color: #ffffff; font-weight: 900; border-left: 4px solid #00f2ff; padding-left: 8px; }

    /* Painel de Cálculos e Eixo */
    .calc-box { border: 2px solid #ffffff; padding: 10px; height: 100%; }
    .calc-row { display: flex; justify-content: space-between; font-size: 18px; font-family: 'Arial Black', sans-serif; font-weight: 900; margin-bottom: 2px; }
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    .eixo-clean { border-top: 1px solid #00f2ff; border-bottom: 1px solid #00f2ff; color: #ffcc00; text-align: center; padding: 4px; margin: 10px 0; font-weight: 900; }

    /* Rodapé Ticker */
    .footer-ticker {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000; color: #fff; padding: 6px;
        font-family: 'Arial Black', sans-serif; font-size: 14px;
        border-top: 2px solid #ffffff; z-index: 1000;
    }
    .ticker-move { display: inline-block; animation: move 35s linear infinite; }
    @keyframes move { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER COM RELÓGIOS ANALÓGICOS ---
c_logo, c_br, c_ny, c_ldn = st.columns([2.5, 1, 1, 1])

with c_logo:
    st.markdown('<span class="bair-text">BAIR</span> <span class="terminal-text">- TERMINAL DOLAR</span>', unsafe_allow_html=True)

def clock_html(city, tz_name):
    t = datetime.now(pytz.timezone(tz_name)).strftime("%H:%M:%S")
    return f'''
        <div class="header-box">
            <div class="analog-clock"></div>
            <div>
                <div class="clock-label">{city}</div>
                <div class="clock-time">{t}</div>
            </div>
        </div>
    '''

with c_br: st.markdown(clock_html("BRASÍLIA", "America/Sao_Paulo"), unsafe_allow_html=True)
with c_ny: st.markdown(clock_html("NEW YORK", "America/New_York"), unsafe_allow_html=True)
with c_ldn: st.markdown(clock_html("LONDRES", "Europe/London"), unsafe_allow_html=True)

# --- CONFIGURAÇÕES / PAINEL ADM ---
with st.expander("⚙️ CONFIGURAÇÕES - PAINEL ADM"):
    c1, c2 = st.columns(2)
    with c1: st.text_input("VALOR ATUAL DOLAR:", "5,4000")
    with c2: close_ref = st.number_input("FECHAMENTO REF (CLOSE):", value=5.4200, format="%.4f")
    st.button("💾 SALVAR DADOS NO TERMINAL")

# --- CORPO COM RETAS (ESTILO GRADE) ---
m_col, s_col = st.columns([3, 1.4])

with m_col:
    st.markdown('<div class="main-border">', unsafe_allow_html=True)
    st.markdown('<p style="color:#00f2ff; font-weight:900; font-size:11px; margin-bottom:5px;">MAIN MONITORING SYSTEM</p>', unsafe_allow_html=True)
    
    # Cabeçalho da Tabela
    st.markdown("""
        <div style="display:flex; justify-content:space-between; border-bottom:2px solid #00f2ff; padding-bottom:5px; margin-bottom:5px;">
            <div style="width:20%; font-weight:900; color:#00f2ff;">ATIVO</div>
            <div style="width:20%; font-weight:900; color:#00f2ff;">PRICE</div>
            <div style="width:20%; font-weight:900; color:#00f2ff;">CLOSE</div>
            <div style="width:20%; font-weight:900; color:#00f2ff;">OPEN</div>
            <div style="width:20%; font-weight:900; color:#00f2ff;">VAR%</div>
        </div>
    """, unsafe_allow_html=True)

    ativos = ["SPOT", "DOLFUT", "DXY", "EWZ", "EUR/USD", "XAU/USD"]
    for a in ativos:
        st.markdown(f'''
            <div class="asset-row">
                <div style="width:20%;" class="asset-tag">{a}</div>
                <div style="width:20%; font-weight:900;">5.4000</div>
                <div style="width:20%; font-weight:900;">5.4200</div>
                <div style="width:20%; font-weight:900;">5.4100</div>
                <div style="width:20%; font-weight:900;" class="perc-green">0,00%</div>
            </div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with s_col:
    st.markdown('<div class="calc-box">', unsafe_allow_html=True)
    st.markdown('<p style="color:#ffcc00; font-weight:900; font-size:13px; text-align:center; margin-bottom:10px;">CÁLCULOS OPERACIONAIS</p>', unsafe_allow_html=True)
    
    # Altas
    for p, m in [("3,00%", 1.03), ("2,34%", 1.0234), ("2,00%", 1.02), ("1,34%", 1.0134), ("1,00%", 1.01), ("0,34%", 1.0034)]:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span>{close_ref*m:.4f}</span></div>', unsafe_allow_html=True)

    # Eixo Central Discreto
    st.markdown(f'<div class="eixo-clean">EIXO: {close_ref:.4f}</div>', unsafe_allow_html=True)

    # Baixas
    for p, m in [("-0,66%", 0.9934), ("-1,00%", 0.99), ("-1,66%", 0.9834), ("-2,00%", 0.98), ("-2,66%", 0.9734), ("-3,00%", 0.97)]:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span>{close_ref*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# RODAPÉ
st.markdown(f"""
    <div class="footer-ticker">
        <div class="ticker-move">
            <span style="color:#ffffff;">DXY</span> <span class="perc-green">▲ 0,01%</span> | 
            <span style="color:#ffffff;">EURUSD</span> <span class="perc-green">▲ 0,05%</span> | 
            <span style="color:#ffffff;">EWZ</span> <span class="perc-red">▼ -0,12%</span> | 
            <span style="color:#ffffff;">PETROLEO</span> <span class="perc-green">▲ 0,45%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(1)
st.rerun()
