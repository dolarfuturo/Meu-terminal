import streamlit as st
import yfinance as yf
import time
from datetime import datetime

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL
if 'v_global' not in st.session_state:
    st.session_state.v_global = {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "notas_mural": "RESUMO DA ABERTURA E AGENDA: AGUARDANDO ATUALIZAÇÃO...",
        "notas": "MURAL: AGUARDANDO...",
        "notas2": "INFORMATIVO: OPERACIONAL ATIVO"
    }

# 4. CSS DO TERMINAL (COM ANIMAÇÃO PULSANTE)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    /* TÍTULO E SINAL PULSANTE */
    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: center; align-items: center; gap: 10px; }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    
    .pulse {
        width: 10px; height: 10px; background: #ff0000; border-radius: 50%;
        box-shadow: 0 0 0 rgba(255, 0, 0, 0.4);
        animation: pulse-animation 1.2s infinite;
    }

    @keyframes pulse-animation {
        0% { box-shadow: 0 0 0 0px rgba(255, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0px rgba(255, 0, 0, 0); }
    }

    .s-container { text-align: center; padding: 15px 0; margin-bottom: 5px; }
    .s-text { font-size: 38px; font-weight: 700; letter-spacing: 2px; font-family: 'Chakra Petch'; color: #ffffff; }
    .var-style { font-size: 22px; margin-left: 15px; font-weight: 400; }
    
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
</style>
""", unsafe_allow_html=True)

def get_clean_data(ticker):
    try:
        t = yf.Ticker(ticker)
        # fast_info é o método mais leve para atualizações frequentes
        last = t.fast_info.last_price
        prev = t.fast_info.previous_close
        var = ((last - prev) / prev * 100) if prev != 0 else 0
        return {"last": last, "var": var}
    except:
        return {"last": 0.0, "var": 0.0}

ui_area = st.empty()

# 6. LOOP DE EXECUÇÃO (1 SEGUNDO)
while True:
    s_m = get_clean_data("BRL=X")
    d_m = get_clean_data("DX-Y.NYB")
    e_m = get_clean_data("EWZ")
    
    if s_m["last"] > 0:
        spot = s_m["last"]
        variacao_spot = s_m["var"]
        cor_var = "#00cc66" if variacao_spot >= 0 else "#cc3333"
        
        # Cálculos baseados no seu ajuste ADM
        spr = d_m["var"] - e_m["var"]
        paridade_global = st.session_state.v_global["ajuste"]*(1+(spr/100))
        justo = round((spot + 0.0310) * 2000) / 2000

        with ui_area.container():
            # Cabeçalho com o Sinal Pulsando ao lado do T de TERMINAL
            st.markdown(f"""
            <div class="t-header">
                <div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div>
                <div class="pulse"></div>
            </div>
            """, unsafe_allow_html=True)

            # Preço Branco e VAR Colorida
            st.markdown(f"""
            <div class="s-container">
                <div class="s-text">
                    {spot:.4f} <span class="var-style" style="color:{cor_var}">({variacao_spot:+.2f}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Linhas de Dados
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{paridade_global:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="d-value c-jus">{justo:.4f}</div></div>', unsafe_allow_html=True)
            
            # Info de Reset (Conforme sua preferência de 00:00 UTC)
            st.markdown(f'<div style="text-align:center; color:#333; font-size:10px; margin-top:10px;">BINANCE RESET: 00:00 UTC | {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

    time.sleep(1)
