import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS: GRID, PONTO CENTRALIZADO E RODAPÉ ESPAÇADO
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    
    /* Cabeçalho: Títulos e Ponto Verde Centralizado */
    .header-container { display: flex; align-items: center; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 30px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 30px; font-weight: 900; margin-left: 5px; }
    
    .status-dot {
        height: 12px;
        width: 12px;
        background-color: #00ff88;
        border-radius: 50%;
        margin-left: 12px;
        box-shadow: 0 0 8px #00ff88;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    
    /* Relógios */
    .city-name { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 11px; text-align: center; margin-bottom: 2px; }
    .clock-container { background: #161b22; border: 1px solid #3d444d; padding: 6px; border-radius: 2px; text-align: center; }
    .digital-time { color: #ffffff; font-size: 18px; font-weight: bold; font-family: 'Courier New', monospace; }

    /* Molduras e Grades */
    .frame-box { 
        border: 2px solid #3d444d; 
        border-top: 4px solid #00f2ff; 
        padding: 10px; 
        background: #0b0e11; 
        margin-bottom: 15px;
    }
    
    table { width: 100%; border-collapse: collapse; border: 1px solid #3d444d; }
    th { 
        color: #00f2ff !important; font-size: 11px !important; 
        border: 1px solid #3d444d !important; 
        text-align: left; padding: 8px !important; background: #161b22;
    }
    td { 
        font-size: 18px !important; font-family: 'Arial Black', sans-serif !important; font-weight: 900 !important; 
        border: 1px solid #3d444d !important; 
        padding: 8px !important; 
    }
    
    .asset-tag { color: #00f2ff; font-weight: 900; }

    /* Painel de Cálculos - FONTE REDUZIDA */
    .calc-row { 
        display: flex; 
        justify-content: space-between; 
        font-size: 14px; /* Reduzido para caber no tablet */
        font-family: 'Arial Black', sans-serif; 
        font-weight: 900; 
        padding: 3px 0; 
        border-bottom: 1px solid #1c2127; 
    }
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    .eixo-frame { border: 2px dashed #00f2ff; color: #ffcc00; font-weight: 900; text-align: center; padding: 6px; margin: 10px 0; font-size: 16px; }

    /* RODAPÉ ESPAÇADO (JUSTIFICADO) */
    .footer-ticker {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000; padding: 12px 15px; border-top: 2px solid #00f2ff;
        display: flex; justify-content: space-around; align-items: center;
        z-index: 1000;
        font-family: 'Arial Black', sans-serif;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE FORMATAÇÃO (5400.0 -> 5.400,0) ---
def fmt(val):
    try:
        # Formata com separador de milhar e decimal, depois inverte para o padrão BR
        return f"{float(val):,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return val

# --- HEADER ---
c_logo, c_br, c_ny, c_ldn = st.columns([2.5, 1, 1, 1])
with c_logo:
    st.markdown("""
        <div class="header-container">
            <span class="bair-text">BAIR</span> 
            <span class="terminal-text">- TERMINAL DOLAR</span>
            <div class="status-dot"></div>
        </div>
    """, unsafe_allow_html=True)

def clock_simple(city, tz):
    t = datetime.now(pytz.timezone(tz)).strftime("%H:%M:%S")
    return f'<div class="city-name">{city}</div><div class="clock-container"><div class="digital-time">{t}</div></div>'

with c_br: st.markdown(clock_simple("BRASÍLIA", "America/Sao_Paulo"), unsafe_allow_html=True)
with c_ny: st.markdown(clock_simple("NEW YORK", "America/New_York"), unsafe_allow_html=True)
with c_ldn: st.markdown(clock_simple("LONDRES", "Europe/London"), unsafe_allow_html=True)

# --- PAINEL ADM ---
with st.expander("⚙️ PAINEL ADM"):
    c1, c2 = st.columns(2)
    with c1: adm_val = st.text_input("VALOR ATUAL:", "5.400,0")
    with c2: close_ref = st.number_input("CLOSE REF:", value=5420.0, step=1.0)

# --- CORPO DO TERMINAL ---
m_col, s_col = st.columns([3.2, 1.2])

with m_col:
    st.markdown('<div class="frame-box">', unsafe_allow_html=True)
    st.markdown('<p style="color:#848e9c; font-size:10px; font-weight:900; margin-bottom:5px;">SYSTEM GRADE MONITORING</p>', unsafe_allow_html=True)
    
    ativos_data = [
        ("SPOT", 5400.0, 5420.0, 5410.0, "0,00%"),
        ("DOLFUT", 5412.0, 5430.0, 5420.0, "0,05%"),
        ("DXY", 104.20, 104.10, 104.15, "0,10%"),
        ("EWZ", 32.10, 32.20, 32.15, "-0,12%"),
        ("EUR/USD", 1.0850, 1.0840, 1.0845, "0,09%"),
        ("XAU/USD", 2030.5, 2028.0, 2029.0, "0,12%"),
        ("PETROLEO BRENT", 82.40, 81.90, 82.00, "0,61%")
    ]
    
    t_html = "<table><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>VAR%</th></tr>"
    for name, p, c, o, v in ativos_data:
        color = "perc-green" if "-" not in v else "perc-red"
        t_html += f"<tr><td><span class='asset-tag'>{name}</span></td><td>{fmt(p)}</td><td>{fmt(c)}</td><td>{fmt(o)}</td><td class='{color}'>{v}</td></tr>"
    st.markdown(t_html + "</table></div>", unsafe_allow_html=True)

with s_col:
    st.markdown('<div class="frame-box">', unsafe_allow_html=True)
    st.markdown('<p style="color:#ffcc00; font-weight:900; font-size:12px; text-align:center;">CÁLCULOS OPERACIONAIS</p>', unsafe_allow_html=True)
    
    # Altas
    for p, m in [("3,00%", 1.03), ("2,00%", 1.02), ("1,00%", 1.01), ("0,34%", 1.0034)]:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span>{fmt(close_ref*m)}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-frame">EIXO: {fmt(close_ref)}</div>', unsafe_allow_html=True)

    # Baixas
    for p, m in [("-1,00%", 0.99), ("-2,00%", 0.98), ("-3,00%", 0.97)]:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span>{fmt(close_ref*m)}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- RODAPÉ ESPAÇADO COM BRENT ---
st.markdown(f"""
    <div class="footer-ticker">
        <span><b style="color:#00f2ff;">DXY</b> <span style="color:#00ff88;">▲ 0,01%</span></span>
        <span><b style="color:#00f2ff;">BRENT</b> <span style="color:#00ff88;">▲ 0,61%</span></span>
        <span><b style="color:#00f2ff;">EWZ</b> <span style="color:#ff4d4d;">▼ -0,12%</span></span>
        <span><b style="color:#00f2ff;">EURUSD</b> <span style="color:#00ff88;">▲ 0,05%</span></span>
        <span><b style="color:#00f2ff;">SPOT</b> <span style="color:#ffffff;">● 0,00%</span></span>
    </div>
    """, unsafe_allow_html=True)

time.sleep(1)
st.rerun()
