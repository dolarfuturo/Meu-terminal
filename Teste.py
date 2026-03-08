import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS: BORDAS DE "TELA DE PC", EIXO DISCRETO E FONTES PESADAS
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    
    /* Título Robusto */
    .bair-text { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 32px; font-weight: 900; text-shadow: 0 0 10px #00f2ff; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 32px; font-weight: 900; text-shadow: 0 0 10px #ffcc00; }
    
    /* Relógios Compactos */
    .header-box { text-align: center; border: 1px solid #1f2329; padding: 4px; background: #161b22; border-radius: 4px; }
    .clock-time { color: #ffffff; font-size: 18px; font-weight: bold; font-family: monospace; }
    .clock-label { color: #848e9c; font-size: 8px; }

    /* BORDAS TIPO MONITOR/PC */
    .grid-container { 
        border: 2px solid #3d444d; 
        padding: 15px; 
        border-radius: 4px; 
        background: #0b0e11; 
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        border-top: 4px solid #00f2ff; /* Detalhe superior em ciano */
        margin-bottom: 10px;
    }
    
    /* Tabelas e Dados */
    th { color: #00f2ff !important; font-size: 13px !important; border-bottom: 2px solid #00f2ff !important; font-weight: 900 !important; }
    td { font-size: 20px !important; font-family: 'Arial Black', sans-serif !important; font-weight: 900 !important; border-bottom: 1px solid #1f2329 !important; }
    .asset-tag { color: #ffffff; background: #1e1e2d; padding: 3px 8px; border-radius: 2px; border-left: 4px solid #00f2ff; }

    /* Painel de Cálculos */
    .calc-row { display: flex; justify-content: space-between; font-size: 19px; font-family: 'Arial Black', sans-serif; font-weight: 900; margin-bottom: 3px; }
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    
    /* Eixo Central Discreto */
    .eixo-discreto { 
        border-top: 1px dashed #00f2ff; 
        border-bottom: 1px dashed #00f2ff; 
        color: #ffcc00; 
        font-weight: 900; 
        text-align: center; 
        padding: 5px; 
        margin: 8px 0; 
        font-size: 18px;
        background: rgba(0, 242, 255, 0.05);
    }

    /* Rodapé Ticker */
    .footer-ticker {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000; color: #fff; padding: 8px;
        font-family: 'Arial Black', sans-serif; font-size: 15px;
        border-top: 2px solid #00f2ff; z-index: 1000;
        overflow: hidden; white-space: nowrap;
    }
    .ticker-move { display: inline-block; animation: move 35s linear infinite; }
    @keyframes move { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    .tk-name { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
c_logo, c_br, c_ny, c_ldn = st.columns([3, 0.7, 0.7, 0.7])
with c_logo:
    st.markdown('<span class="bair-text">BAIR</span> <span class="terminal-text">- TERMINAL DOLAR</span>', unsafe_allow_html=True)

def get_tz(tz): return datetime.now(pytz.timezone(tz)).strftime("%H:%M:%S")
with c_br: st.markdown(f'<div class="header-box"><div class="clock-label">BRASÍLIA</div><div class="clock-time">{get_tz("America/Sao_Paulo")}</div></div>', unsafe_allow_html=True)
with c_ny: st.markdown(f'<div class="header-box"><div class="clock-label">NEW YORK</div><div class="clock-time">{get_tz("America/New_York")}</div></div>', unsafe_allow_html=True)
with c_ldn: st.markdown(f'<div class="header-box"><div class="clock-label">LONDRES</div><div class="clock-time">{get_tz("Europe/London")}</div></div>', unsafe_allow_html=True)

# --- ADM ---
with st.expander("⚙️ CONFIGURAÇÕES"):
    c1, c2 = st.columns(2)
    with c1: adm_val = st.text_input("VALOR ATUAL:", "5,4000")
    with c2: close_ref = st.number_input("FECHAMENTO (CLOSE):", value=5.4200, format="%.4f")
    if st.button("💾 SALVAR DADOS"):
        st.success("Terminal Atualizado!")

# --- CORPO ---
m_col, s_col = st.columns([3, 1.4])

with m_col:
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#00f2ff; font-weight:900; font-size:12px; margin-bottom:10px;">MAIN MONITORING SYSTEM</p>', unsafe_allow_html=True)
    ativos = ["SPOT", "DOLFUT", "DXY", "EWZ", "EUR/USD", "XAU/USD"]
    t_html = "<table><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>VAR%</th></tr>"
    for a in ativos:
        t_html += f"<tr><td><span class='asset-tag'>{a}</span></td><td>5.4000</td><td>5.4200</td><td>5.4100</td><td class='perc-green'>0,00%</td></tr>"
    st.markdown(t_html + "</table></div>", unsafe_allow_html=True)

with s_col:
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#ffcc00; font-weight:900; font-size:14px; text-align:center;">CÁLCULOS OPERACIONAIS</p>', unsafe_allow_html=True)
    
    # Altas (Incluso 0,34%)
    altas = [("3,00%", 1.03), ("2,34%", 1.0234), ("2,00%", 1.02), ("1,34%", 1.0134), ("1,00%", 1.01), ("0,34%", 1.0034)]
    for p, m in altas:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span>{close_ref*m:.4f}</span></div>', unsafe_allow_html=True)

    # Eixo Discreto
    st.markdown(f'<div class="eixo-discreto">EIXO: {close_ref:.4f}</div>', unsafe_allow_html=True)

    # Baixas
    baixas = [("-0,66%", 0.9934), ("-1,00%", 0.99), ("-1,66%", 0.9834), ("-2,00%", 0.98), ("-2,66%", 0.9734), ("-3,00%", 0.97)]
    for p, m in baixas:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span>{close_ref*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# RODAPÉ
st.markdown(f"""
    <div class="footer-ticker">
        <div class="ticker-move">
            <span class="tk-name">DXY</span> <span style="color:#00ff88;">▲ 0,01%</span> | 
            <span class="tk-name">EURUSD</span> <span style="color:#00ff88;">▲ 0,05%</span> | 
            <span class="tk-name">EWZ</span> <span style="color:#ff4d4d;">▼ -0,12%</span> | 
            <span class="tk-name">SPOT</span> <span style="color:#ffffff;">● 0,00%</span> | 
            <span class="tk-name">PETROLEO</span> <span style="color:#00ff88;">▲ 0,45%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(1)
st.rerun()
