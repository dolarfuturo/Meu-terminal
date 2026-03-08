import streamlit as st
from datetime import datetime
import pytz
import time

# Configuração para Tablet
st.set_page_config(page_title="BAIR - TERMINAL DOLAR", layout="wide")

# CSS: GRID TÉCNICO ROBUSTO (LINHAS HORIZONTAIS E VERTICAIS IDENTICAS)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11 !important; color: #ffffff !important; }
    
    /* Títulos e Fontes Robustas */
    .bair-text { color: #00f2ff; font-family: 'Arial Black', sans-serif; font-size: 30px; font-weight: 900; }
    .terminal-text { color: #ffcc00; font-family: 'Arial Black', sans-serif; font-size: 30px; font-weight: 900; }
    
    /* Relógios */
    .header-box { text-align: center; border: 1px solid #1f2329; padding: 10px; background: #161b22; border-radius: 4px; }
    .clock-time { color: #ffffff; font-size: 26px; font-weight: bold; font-family: monospace; }
    .clock-label { color: #848e9c; font-size: 11px; text-transform: uppercase; }

    /* BORDA EM VOLTA DE TODO O PAINEL DE DADOS */
    .main-panel-border { 
        border: 2px solid #3d444d; /* Linha reta tipo monitor */
        border-radius: 6px; 
        padding: 15px; 
        background: #0b0e11; 
        margin-bottom: 10px;
    }

    /* GRID TÉCNICO - LINHAS HORIZONTAIS E VERTICAIS (Copiar Imagem) */
    .custom-table { width: 100%; border-collapse: collapse; border: 1px solid #ffffff; } /* Borda externa branca */
    
    .custom-table th { 
        color: #00f2ff; 
        font-size: 14px; 
        text-align: left; 
        border: 1px solid #ffffff !important; /* Linhas brancas horizontais e verticais no topo */
        padding: 10px !important; 
        text-transform: uppercase;
        font-family: 'Arial Black', sans-serif;
    }
    
    .custom-table td { 
        font-size: 21px; 
        font-family: 'Arial Black', sans-serif !important; 
        font-weight: 900 !important; 
        border: 1px solid #ffffff !important; /* Linhas brancas horizontais e verticais em todas as células */
        padding: 12px !important; 
    }
    
    .asset-tag { color: #ffffff; font-weight: 900; }

    /* Cálculos */
    .calc-row { display: flex; justify-content: space-between; font-family: monospace; font-size: 19px; margin-bottom: 5px; }
    .perc-green { color: #00ff88; font-weight: bold; }
    .perc-red { color: #ff4d4d; font-weight: bold; }
    .eixo-frame { background: #00f2ff; color: #000; font-weight: bold; text-align: center; padding: 10px; margin: 15px 0; font-size: 18px; }

    /* Inputs Dark */
    input { background-color: #161b22 !important; color: #00f2ff !important; border: 1px solid #00f2ff !important; font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
c1, c2, c3, c4 = st.columns([2.5, 1, 1, 1])
with c1:
    st.markdown('<span class="bair-text">BAIR</span> <span class="terminal-text">- TERMINAL DOLAR</span>', unsafe_allow_html=True)

def get_now(tz): return datetime.now(pytz.timezone(tz)).strftime("%H:%M:%S")

with c2: st.markdown(f'<div class="header-box"><div class="clock-label">BRASÍLIA</div><div class="clock-time">{get_now("America/Sao_Paulo")}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="header-box"><div class="clock-label">NEW YORK</div><div class="clock-time">{get_now("America/New_York")}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="header-box"><div class="clock-label">LONDRES</div><div class="clock-time">{get_now("Europe/London")}</div></div>', unsafe_allow_html=True)

st.write("")

# --- PAINEL ADM ESCONDIDO ---
with st.expander("⚙️ CONFIGURAÇÕES ADM"):
    adm_val = st.text_input("PAINEL ADM:", "5,4000")
    close_ref = st.number_input("CLOSE REF:", value=5.4200, format="%.4f")

# --- CORPO (GRADE TÉCNICA IDÊNTICA) ---
left_c, right_c = st.columns([3, 1.4])

with left_c:
    # Borda em volta de todo o painel de grade
    st.markdown('<div class="main-panel-border">', unsafe_allow_html=True)
    st.markdown('<p style="color:#848e9c; font-size:12px; font-weight:bold;">MAIN MONITORING SYSTEM</p>', unsafe_allow_html=True)
    
    # Lista de ativos com as colunas completas
    ativos_data = [
        ("SPOT", "5.4000", "5.4200", "5.4100", "0,00%"),
        ("DOLFUT", "5.4120", "5.4300", "5.4200", "0,05%"),
        ("DXY", "104.20", "104.10", "104.15", "0,10%"),
        ("EWZ", "32.10", "32.20", "32.15", "-0,12%"),
        ("EUR/USD", "1.0850", "1.0840", "1.0845", "0,09%"),
        ("XAU/USD", "2030.5", "2028.0", "2029.0", "0,12%")
    ]
    
    # Criando a tabela HTML manual para garantir o GRID
    table_html = """<table class="custom-table">
        <tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>OPEN</th><th>VAR%</th></tr>"""
    for name, p, c, o, v in ativos_data:
        color = "perc-green" if "-" not in v else "perc-red"
        table_html += f"""<tr>
            <td><span class='asset-tag'>{name}</span></td>
            <td>{p}</td><td>{c}</td><td>{o}</td><td class='{color}'>{v}</td>
        </tr>"""
    table_html += "</table></div>"
    st.markdown(table_html, unsafe_allow_html=True)

with right_c:
    # Borda em volta de todo o painel de cálculos
    st.markdown('<div class="main-panel-border">', unsafe_allow_html=True)
    st.markdown('<p style="color:#ffcc00; font-weight:bold; font-size:15px; text-align:center;">CÁLCULOS</p>', unsafe_allow_html=True)
    
    v_close = close_ref if 'close_ref' in locals() else 5.4200

    # Altas (Incluindo 0,34%)
    for p, m in [("3,00%", 1.03), ("2,34%", 1.0234), ("2,00%", 1.02), ("1,34%", 1.0134), ("1,00%", 1.01), ("0,34%", 1.0034)]:
        st.markdown(f'<div class="calc-row"><span class="perc-green">{p}</span><span>{v_close*m:.4f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="eixo-frame">CLOSE EIXO: {v_close:.4f}</div>', unsafe_allow_html=True)

    # Baixas (Incluindo -2,66%)
    for p, m in [("-0,66%", 0.9934), ("-1,00%", 0.99), ("-1,66%", 0.9834), ("-2,00%", 0.98), ("-2,66%", 0.9734), ("-3,00%", 0.97)]:
        st.markdown(f'<div class="calc-row"><span class="perc-red">{p}</span><span>{v_close*m:.4f}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Rodapé simples
st.markdown('<p style="text-align:center; color:#00f2ff; margin-top:10px;">DXY 0,01% | EWZ 0,0% | SPOT 0,0%</p>', unsafe_allow_html=True)

# Auto-refresh
time.sleep(1)
st.rerun()
