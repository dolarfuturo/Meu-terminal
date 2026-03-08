import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS: LINHAS DE PAINEL, NEGRITO E CORES DO RODAPÉ
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    
    /* Título com Letra Cheia (Extra Bold) */
    .bair-text { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 34px; font-weight: 900; text-shadow: 0 0 10px #00f2ff; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 34px; font-weight: 900; text-shadow: 0 0 10px #ffcc00; }
    
    /* Relógios Compactos */
    .header-box { text-align: center; border: 1px solid #1f2329; padding: 5px; background: #161b22; border-radius: 4px; }
    .clock-time { color: #ffffff; font-size: 20px; font-weight: bold; font-family: monospace; }
    .clock-label { color: #848e9c; font-size: 9px; }

    /* BORDAS DO TERMINAL (Efeito Painel) */
    .grid-container { 
        border: 3px solid #00f2ff; 
        padding: 15px; 
        border-radius: 10px; 
        background: #0b0e11; 
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.2), inset 0 0 10px rgba(0, 242, 255, 0.1);
        margin-bottom: 10px;
    }
    
    /* Tabelas em Negrito */
    th { color: #00f2ff !important; font-size: 14px !important; border-bottom: 2px solid #00f2ff !important; font-weight: 900 !important; }
    td { font-size: 21px !important; font-family: 'Arial Black', sans-serif !important; font-weight: 900 !important; border-bottom: 1px solid #1f2329 !important; }
    .asset-tag { color: #ffffff; background: #1e1e2d; padding: 4px 10px; border-radius: 4px; border-left: 5px solid #00f2ff; }

    /* Cálculos */
    .calc-row { display: flex; justify-content: space-between; font-size: 20px; font-family: 'Arial Black', sans-serif; font-weight: 900; margin-bottom: 4px; }
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    .eixo-data { background: #ffcc00; color: #000; font-weight: 900; text-align: center; padding: 8px; margin: 10px 0; font-size: 20px; border-radius: 4px; }

    /* Rodapé: Tickets Brancos e Variações Coloridas */
    .footer-ticker {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000; color: #fff; padding: 10px;
        font-family: 'Arial Black', sans-serif; font-size: 16px;
        border-top: 3px solid #00f2ff; z-index: 1000;
        overflow: hidden; white-space: nowrap;
    }
    .ticker-move { display: inline-block; animation: move 30s linear infinite; }
    @keyframes move { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    .tk-name { color: #ffffff; font-weight: bold; }
    .tk-up { color: #00ff88; font-weight: bold; }
    .tk-down { color: #ff4d4d; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
c_logo, c_br, c_ny, c_ldn = st.columns([2.8, 0.8, 0.8, 0.8])
with c_logo:
    st.markdown('<span class="bair-text">BAIR</span> <span class="terminal-text">- TERMINAL DOLAR</span>', unsafe_allow_html=True)

def get_tz(tz): return datetime.now(pytz.timezone(tz)).strftime("%H:%M:%S")
with c_br: st.markdown(f'<div class="header-box"><div class="clock-label">BRASÍLIA</div><div class="clock-time">{get_tz("America/Sao_Paulo")}</div></div>', unsafe_allow_html=True)
with c_ny: st.markdown(f'<div class="header-box"><div class="clock-label">NEW YORK</div><div class="clock-time">{get_tz("America/New_York")}</div></div>', unsafe_allow_html=True)
with c_ldn: st.markdown(f'<div class="header-box"><div class="clock-label">LONDRES</div><div class="clock-time">{get_tz("Europe/London")}</div></div>', unsafe_allow_html=True)

# --- ADM COM BOTÃO SALVAR ---
with st.expander("⚙️ PAINEL ADM"):
    c1, c2 = st.columns(2)
    with c1: adm_val = st.text_input("VALOR ATUAL:", "5,4000")
    with c2: close_ref = st.number_input("FECHAMENTO (CLOSE):", value=5.4200, format="%.4f")
    if st.button("💾 SALVAR CONFIGURAÇÕES"):
        st.success("Dados salvos no terminal!")

# --- CORPO ---
m_col, s_col = st.columns([3, 1.4])

with m_col:
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#00f2ff; font-weight:900; font-size:14px;">MONITORAMENTO PRINCIPAL</p>', unsafe_allow_html=True)
    ativos = ["SPOT", "DOLFUT", "DXY", "EWZ", "EUR/USD", "XAU/USD"]
    t_html = "<table><tr><th>ATIVO</th><th>PREÇO</th><th>VAR%</th><th>MÁX</th><th>MÍN</th></tr>"
    for a in ativos:
        t_html += f"<tr><td><span class='asset-tag'>{a}</span></td><td>5.4000</td><td class='perc-green'>0,00%</td><td>5.4100</td><td>5.3900</td></tr>"
    st.markdown(t_html + "</table></div>", unsafe_allow_html=True)

with s_col:
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#ffcc00; font-weight:900; font-size:16px; text-align:center;">CÁLCULOS</p>', unsafe_allow_html=True)
    
    # Altas
    for p, m in [("3,00%", 1.03), ("2,34%", 1.0234), ("2,00%", 1.02), ("1,34%", 1.0134), ("1,00%", 1.01)]:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span>{close_ref*m:.4f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-data">EIXO CLOSE: {close_ref:.4f}</div>', unsafe_allow_html=True)

    # Baixas (Incluindo o -2,66%)
    for p, m in [("-0,66%", 0.9934), ("-1,00%", 0.99), ("-1,66%", 0.9834), ("-2,00%", 0.98), ("-2,66%", 0.9734), ("-3,00%", 0.97)]:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span>{close_ref*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# RODAPÉ ESTILIZADO
st.markdown(f"""
    <div class="footer-ticker">
        <div class="ticker-move">
            <span class="tk-name">DXY</span> <span class="tk-up">▲ 0,01%</span> | 
            <span class="tk-name">EURUSD</span> <span class="tk-up">▲ 0,05%</span> | 
            <span class="tk-name">EWZ</span> <span class="tk-down">▼ -0,12%</span> | 
            <span class="tk-name">PETROLEO</span> <span class="tk-up">▲ 0,45%</span> | 
            <span class="tk-name">GBPUSD</span> <span class="tk-down">▼ -0,02%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(1)
st.rerun()
