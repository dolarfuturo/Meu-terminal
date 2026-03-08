import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS: BLOCOS SEPARADOS COM BORDAS INDEPENDENTES
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    
    /* Cabeçalho */
    .header-container { display: flex; align-items: center; margin-bottom: 20px; }
    .bair-text { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 32px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 32px; font-weight: 900; margin-left: 5px; }
    
    .status-dot {
        height: 14px; width: 14px;
        background-color: #00ff88;
        border-radius: 50%;
        margin-left: 15px;
        box-shadow: 0 0 12px #00ff88;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

    /* BLOCOS SEPARADOS (CONFORME DESENHO) */
    .block-container { 
        border: 2px solid #3d444d; 
        border-top: 4px solid #00f2ff; 
        padding: 15px; 
        background: #0b0e11; 
        border-radius: 4px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        height: 100%; /* Garante que os blocos alinhem a altura */
    }
    
    /* Grade de Monitoramento */
    table { width: 100%; border-collapse: collapse; }
    th { 
        color: #00f2ff !important; font-size: 11px !important; 
        border-bottom: 2px solid #3d444d !important; 
        padding: 12px 5px !important; text-align: left;
    }
    td { 
        font-size: 19px !important; font-family: 'Arial Black', sans-serif !important; font-weight: 900 !important; 
        border-bottom: 1px solid #1c2127 !important; 
        padding: 15px 5px !important; 
    }
    tr:nth-child(even) { background-color: rgba(255,255,255,0.02); }

    /* Cálculos Operacionais */
    .calc-row { 
        display: flex; justify-content: space-between; 
        padding: 10px 5px; 
        border-bottom: 1px solid #1c2127; 
        font-family: 'Arial Black', sans-serif; font-weight: 900; font-size: 16px;
    }
    .perc-green { color: #00ff88; }
    .perc-red { color: #ff4d4d; }
    
    .eixo-box { 
        border: 2px dashed #00f2ff; 
        color: #ffcc00; font-weight: 900; text-align: center; 
        padding: 12px; margin: 15px 0; font-size: 18px;
        background: rgba(0, 242, 255, 0.05);
    }

    /* Rodapé */
    .footer-ticker {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000; padding: 12px; border-top: 2px solid #00f2ff;
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
c_logo, c_br, c_ny, c_ldn = st.columns([2.5, 1, 1, 1])
with c_logo:
    st.markdown('<div class="header-container"><span class="bair-text">BAIR</span><span class="terminal-text">- TERMINAL DOLAR</span><div class="status-dot"></div></div>', unsafe_allow_html=True)

# Relógios simplificados
def clock(city, tz):
    t = datetime.now(pytz.timezone(tz)).strftime("%H:%M:%S")
    return f'<div style="text-align:center; background:#161b22; border:1px solid #3d444d; padding:5px;"><div style="color:#ffcc00; font-size:10px;">{city}</div><div style="font-size:18px; font-weight:bold;">{t}</div></div>'

with c_br: st.markdown(clock("BRASÍLIA", "America/Sao_Paulo"), unsafe_allow_html=True)
with c_ny: st.markdown(clock("NEW YORK", "America/New_York"), unsafe_allow_html=True)
with c_ldn: st.markdown(clock("LONDRES", "Europe/London"), unsafe_allow_html=True)

st.write("") # Espaçador

# --- CORPO COM BLOCOS SEPARADOS (CONFORME IMAGEM) ---
col_main, col_side = st.columns([3.2, 1.2])

with col_main:
    st.markdown('<div class="block-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#848e9c; font-size:10px; font-weight:900; margin-bottom:10px;">MONITORAMENTO DA GRADE PRINCIPAL</p>', unsafe_allow_html=True)
    
    ativos = [
        ("SPOT", "5,4000", "5,4200", "0,00%"),
        ("DOLFUT", "5,4120", "5,4300", "0,05%"),
        ("DXY", "104,20", "104,10", "0,10%"),
        ("EWZ", "32,10", "32,20", "-0,12%"),
        ("EUR/USD", "1,0850", "1,0840", "0,09%"),
        ("XAU/USD", "2030,5", "2028,0", "0,12%"),
        ("PETROLEO", "82,40", "81,90", "0,61%")
    ]
    
    html = "<table><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>VAR%</th></tr>"
    for n, p, c, v in ativos:
        clr = "perc-green" if "-" not in v else "perc-red"
        html += f"<tr><td><span style='color:#00f2ff;'>{n}</span></td><td>{p}</td><td>{c}</td><td class='{clr}'>{v}</td></tr>"
    st.markdown(html + "</table></div>", unsafe_allow_html=True)

with col_side:
    st.markdown('<div class="block-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#ffcc00; font-weight:900; font-size:11px; text-align:center;">CÁLCULOS OPERACIONAIS</p>', unsafe_allow_html=True)
    
    # Exemplo de valores
    for p, v in [("3,00%", "5,5826"), ("2,34%", "5,5468"), ("1,00%", "5,4742"), ("0,34%", "5,4384")]:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span>{v}</span></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="eixo-box">EIXO: 5,4200</div>', unsafe_allow_html=True)
    
    for p, v in [("-0,66%", "5,3842"), ("-1,00%", "5,3658"), ("-2,66%", "5,2758")]:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span>{v}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- RODAPÉ ---
st.markdown("""
    <div class="footer-ticker">
        <div style="font-family:'Arial Black'; font-size:14px; color:#ffffff; white-space:nowrap;">
            DXY ▲ 0,01% | XAUUSD ▲ 0,12% | JPYUSD ▼ -0,08% | EWZ ▼ -0,12% | SPOT ● 0,00%
        </div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(1)
st.rerun()
