import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS: GRID COMPLETO COM LINHAS VERTICAIS, BORDAS E PONTO PISCANTE
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
    
    /* Cabeçalho */
    .city-name { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 11px; letter-spacing: 1px; text-align: center; margin-bottom: 2px; }
    .clock-container { background: #161b22; border: 1px solid #3d444d; padding: 6px; border-radius: 2px; text-align: center; }
    .digital-time { color: #ffffff; font-size: 18px; font-weight: bold; font-family: 'Courier New', monospace; }

    /* BORDAS EM TODO O PAINEL E GRID TÉCNICO */
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
    .pre-mkt { color: #ffcc00; font-size: 9px; font-family: sans-serif; }

    /* Painel de Cálculos Operacionais - FONTE REDUZIDA */
    .calc-row { 
        display: flex; 
        justify-content: space-between; 
        font-size: 13.5px; 
        font-family: 'Arial Black', sans-serif; 
        font-weight: 900; 
        padding: 2px 0; 
        border-bottom: 1px solid #1c2127; 
    }
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    .eixo-frame { border: 2px dashed #00f2ff; color: #ffcc00; font-weight: 900; text-align: center; padding: 6px; margin: 10px 0; font-size: 16px; }

    /* Rodapé */
    .footer-ticker {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000; padding: 10px; border-top: 2px solid #00f2ff;
        overflow: hidden; white-space: nowrap; z-index: 1000;
    }
    .ticker-move { display: inline-block; animation: move 35s linear infinite; font-family: 'Arial Black', sans-serif; font-size: 14px; }
    @keyframes move { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
    """, unsafe_allow_html=True)

# FUNÇÃO PARA TROCAR PONTO POR VÍRGULA SEM MEXER NO VALOR
def fmt_v(val):
    if isinstance(val, float):
        return f"{val:.4f}".replace(".", ",")
    return str(val).replace(".", ",")

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
    with c1: adm_val = st.text_input("VALOR ATUAL:", "5,4000")
    with c2: close_ref = st.number_input("CLOSE REF:", value=5.4200, format="%.4f")

# --- CORPO DO TERMINAL ---
m_col, s_col = st.columns([3.2, 1.2])

with m_col:
    st.markdown('<div class="frame-box">', unsafe_allow_html=True)
    st.markdown('<p style="color:#848e9c; font-size:10px; font-weight:900; margin-bottom:5px;">SYSTEM GRADE MONITORING</p>', unsafe_allow_html=True)
    
    ativos_data = [
        ("SPOT", 5.4000, 5.4200, 5.4100, 5.4350, 5.3910, "0,00%"),
        ("DOLFUT", 5.4120, 5.4300, 5.4200, 5.4400, 5.4050, "0,05%"),
        ("DXY", 104.20, 104.10, 104.15, 104.50, 104.05, "0,10%"),
        ("EWZ", 32.10, 32.20, 32.15, 32.40, 31.90, "-0,12%"),
        ("EUR/USD", 1.0850, 1.0840, 1.0845, 1.0890, 1.0820, "0,09%"),
        ("XAU/USD", 2030.5, 2028.0, 2029.0, 2040.0, 2025.0, "0,12%"),
        ("PETROLEO BRENT", 82.40, 81.90, 82.00, 83.10, 81.50, "0,61%")
    ]
    
    t_html = "<table><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>MAX</th><th>MIN</th><th>VAR%</th></tr>"
    for name, p, c, o, mx, mn, v in ativos_data:
        pre_tag = '<br><span class="pre-mkt">PRE-MARKET</span>' if name == "EWZ" else ""
        color = "perc-green" if "-" not in v else "perc-red"
        # Aplica a vírgula sem alterar a precisão
        t_html += f"<tr><td><span class='asset-tag'>{name}</span>{pre_tag}</td><td>{fmt_v(p)}</td><td>{fmt_v(c)}</td><td>{fmt_v(o)}</td><td>{fmt_v(mx)}</td><td>{fmt_v(mn)}</td><td class='{color}'>{v}</td></tr>"
    st.markdown(t_html + "</table></div>", unsafe_allow_html=True)

with s_col:
    st.markdown('<div class="frame-box">', unsafe_allow_html=True)
    st.markdown('<p style="color:#ffcc00; font-weight:900; font-size:12px; text-align:center;">CÁLCULOS OPERACIONAIS</p>', unsafe_allow_html=True)
    
    for p, m in [("3,00%", 1.03), ("2,34%", 1.0234), ("2,00%", 1.02), ("1,34%", 1.0134), ("1,00%", 1.01), ("0,34%", 1.0034)]:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span>{fmt_v(close_ref*m)}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-frame">EIXO: {fmt_v(close_ref)}</div>', unsafe_allow_html=True)

    for p, m in [("-0,66%", 0.9934), ("-1,00%", 0.99), ("-1,66%", 0.9834), ("-2,00%", 0.98), ("-2,66%", 0.9734), ("-3,00%", 0.97)]:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span>{fmt_v(close_ref*m)}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- RODAPÉ ---
st.markdown(f"""
    <div class="footer-ticker">
        <div class="ticker-move">
            <span style="color:#ffffff;">DXY</span> <span style="color:#00ff88;">▲ 0,01%</span> | 
            <span style="color:#ffffff;">PETROLEO BRENT</span> <span style="color:#00ff88;">▲ 0,61%</span> | 
            <span style="color:#ffffff;">GBPUSD</span> <span style="color:#00ff88;">▲ 0,15%</span> | 
            <span style="color:#ffffff;">EURUSD</span> <span style="color:#00ff88;">▲ 0,05%</span> | 
            <span style="color:#ffffff;">EWZ</span> <span style="color:#ff4d4d;">▼ -0,12%</span> | 
            <span style="color:#ffffff;">SPOT</span> <span style="color:#ffffff;">● 0,00%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(1)
st.rerun()
