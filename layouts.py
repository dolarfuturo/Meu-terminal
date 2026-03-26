import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração Otimizada para Mobile
st.set_page_config(layout="centered", page_title="BAIR MOBILE", initial_sidebar_state="collapsed")

# --- CSS: ARQUITETURA MOBILE (VERTICAL) ---
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #050a0e !important;
        color: #fff;
    }
    .block-container { padding: 0.5rem !important; }

    /* Cabeçalho Mobile */
    .header-mobile { text-align: center; border-bottom: 2px solid #FFD700; padding-bottom: 5px; margin-bottom: 10px; }
    .title-mobile { font-size: 22px; font-family: monospace; font-weight: bold; margin: 0; }
    .clock-mobile { font-size: 14px; color: #00ff00; font-family: monospace; }

    /* Grade de Ativos Mobile - Cards ao invés de tabela larga */
    .section-title { 
        background: #0d1b22; border: 1px solid #ffffff; color: #00f2ff; 
        text-align: center; font-size: 12px; padding: 3px; margin: 10px 0 5px 0;
    }
    
    .mobile-card {
        background: #0d1b22; border: 1px solid #444; border-radius: 5px;
        padding: 8px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center;
    }
    .asset-info { font-family: monospace; font-weight: bold; }
    .asset-name { color: #FFD700; font-size: 14px; }
    .asset-price { font-size: 16px; color: #fff; }
    .asset-var { font-size: 14px; font-weight: bold; }

    /* Projeções Mobile - Empilhadas */
    .calc-grid-mobile {
        display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-bottom: 10px;
    }
    .calc-box-mini {
        background: #0a141a; border: 1px solid #fff; border-radius: 4px;
        padding: 5px; text-align: center; font-family: monospace;
    }
    .label-mini { font-size: 10px; color: #aaa; display: block; }
    .val-mini { font-size: 14px; font-weight: bold; }

    /* Barra de Força Mobile - Maior para toque */
    .bar-wrapper-mobile { 
        background: #0a141a; padding: 10px; border: 2px solid #fff; border-radius: 8px; 
        text-align: center; margin-top: 10px;
    }
    .force-container-mobile { 
        background: #111; height: 25px; width: 100%; border-radius: 5px; 
        position: relative; display: flex; border: 1px solid #444; margin: 8px 0;
    }
    .sinal-mobile { font-size: 18px; font-weight: 900; min-height: 20px; }

    /* Esconder elementos desnecessários no mobile */
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS (MANTIDO) ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1] * m, "cl": t.info.get('previousClose', d['Open'].iloc[0]) * m}
    except: return {"at": 0.0, "cl": 1.0}

def get_resumo(a_dol, spot_live):
    # Lógica simplificada de variação para o exemplo mobile
    v_v = ((spot_live['at'] / a_dol) - 1) * 100
    p_v = min(100, abs(v_v) * 10) if v_v < 0 else 0
    p_r = min(100, v_v * 10) if v_v > 0 else 0
    seta, cor = "", "#000"
    if p_v >= 90: seta, cor = "▲ COMPRA FORTE", "#00ff88"
    elif p_r >= 90: seta, cor = "▼ VENDA FORTE", "#ff4d4d"
    return {"v_v": v_v, "p_v": p_v, "p_r": p_r, "seta": seta, "cor": cor}

# --- INTERFACE MOBILE ---
a_dol = 5246.00 # Axis fixo para mobile ou vindo de cache
spot_live = fetch("USDBRL=X")
ewz_live = fetch("EWZ")
res = get_resumo(a_dol, spot_live)
now = datetime.now(pytz.timezone('America/Sao_Paulo'))

# Header
st.markdown(f"""
    <div class="header-mobile">
        <p class="title-mobile"><span style="color:#00BFFF">BAIR</span> <span style="color:#FFD700">TERMINAL</span></p>
        <span class="clock-mobile">{now.strftime('%H:%M:%S')} 🇧🇷</span>
    </div>
""", unsafe_allow_html=True)

# Grade de Ativos (Estilo Cards para Mobile)
st.markdown('<div class="section-title">MERCADO VIVO</div>', unsafe_allow_html=True)

ativos = {"DOLFUT": spot_live, "EWZ": ewz_live, "DXY": fetch("DX-Y.NYB")}
for nome, dados in ativos.items():
    var = ((dados['at'] / dados['cl']) - 1) * 100 if dados['cl'] > 0 else 0
    cor_var = "#00ff88" if var >= 0 else "#ff4d4d"
    st.markdown(f"""
        <div class="mobile-card">
            <div class="asset-info">
                <span class="asset-name">{nome}</span><br>
                <span class="asset-price">{(dados['at']/1000 if nome=="DOLFUT" else dados['at']):.2f}</span>
            </div>
            <div class="asset-var" style="color:{cor_var}">{var:+.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

# Projeções (Grid 2x2)
st.markdown('<div class="section-title">PROJEÇÕES</div>', unsafe_allow_html=True)
st.markdown(f"""
    <div class="calc-grid-mobile">
        <div class="calc-box-mini"><span class="label-mini">AXIS</span><span class="val-mini">{a_dol:.2f}</span></div>
        <div class="calc-box-mini"><span class="label-mini">VIVO</span><span class="val-mini">{spot_live['at']:.2f}</span></div>
    </div>
""", unsafe_allow_html=True)

# Barra de Força (Grande para Mobile)
st.markdown(f"""
    <div class="bar-wrapper-mobile">
        <div style="display:flex; justify-content:space-between; font-size:10px; color:#aaa; font-family:monospace;">
            <span>COMPRA</span><span>VENDA</span>
        </div>
        <div class="force-container-mobile">
            <div style="position:absolute; left:50%; top:0; width:2px; height:100%; background:#fff; z-index:10;"></div>
            <div style="width:50%; height:100%; background:#050a0e;">
                <div style="background:#00ff88; float:right; height:100%; width:{res['p_v']}%;"></div>
            </div>
            <div style="width:50%; height:100%; background:#050a0e;">
                <div style="background:#ff4d4d; float:left; height:100%; width:{res['p_r']}%;"></div>
            </div>
        </div>
        <div class="sinal-mobile blink" style="color:{res['cor']}">{res['seta']}</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True) # Espaço para o rodapé não cobrir nada
time.sleep(2)
st.rerun()
