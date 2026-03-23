import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

st.set_page_config(layout="wide", page_title="BAIR - TERMINAL")

# --- ESTILO ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; font-family: monospace; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; }
    .bair-title { font-size: 40px; color: #00f2ff; font-weight: 950; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- BUSCA DE DADOS ---
def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: return None
        m = 1000 if ticker == "USDBRL=X" else 1
        return {
            "at": d['Close'].iloc[-1] * m,
            "cl": t.info.get('previousClose', d['Open'].iloc[0]) * m,
            "mx": d['High'].max() * m,
            "mn": d['Low'].min() * m,
            "op": d['Open'].iloc[0] * m
        }
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    a_dol = st.number_input("AXIS DOLFUT:", value=5308.00)
    st.button("RECALCULAR")

spot = get_data("USDBRL=X")
ewz = get_data("EWZ")

if spot:
    # --- CÁLCULOS EXATOS ---
    # Spreed baseado na volatilidade do Spot
    spreed = (spot['mx'] - spot['mn']) / 8
    
    # Projeções: AXIS + o deslocamento real do Spot no dia
    # Isso evita que o valor dobre para 10.000
    max_proj = a_dol + (spot['mx'] - spot['cl']) + spreed
    min_proj = a_dol - (spot['cl'] - spot['mn']) + spreed
    
    # Intermediários
    p50_max = (max_proj + a_dol) / 2
    p50_min = (min_proj + a_dol) / 2
    
    # Variações e Justo
    v_spot = (spot['at'] / spot['cl']) - 1
    v_ewz = (ewz['at'] / ewz['cl']) - 1 if ewz else 0
    v_final = (v_spot * 0.6) - (v_ewz * 0.4)
    vivo = a_dol * (1 + v_final)
    justo = a_dol * (1 + (v_final / 2))

    # --- TELA ---
    st.markdown(f'<div class="bair-title">BAIR - TERMINAL DOLLAR</div>', unsafe_allow_html=True)
    
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        # Tabela Principal
        html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>MAX</th><th>MIN</th><th>VAR</th></tr></thead><tbody>"""
        # Linha DOLFUT
        html += f"<tr><td>DOLFUT</td><td style='color:#00f2ff;'>{vivo:.2f}</td><td>{a_dol:.2f}</td><td>{max_proj:.2f}</td><td>{min_proj:.2f}</td><td style='color:#00ff00;'>{v_final*100:+.2f}%</td></tr>"
        # Linha SPOT
        html += f"<tr><td>DOLSPOT</td><td>{spot['at']:.2f}</td><td>{spot['cl']:.2f}</td><td>{spot['mx']:.2f}</td><td>{spot['mn']:.2f}</td><td>{v_spot*100:+.2f}%</td></tr>"
        st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

    with col_right:
        # Painel Lateral
        st.markdown(f"""
        <div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{max_proj:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>50% MAX</span> <span>{p50_max:.2f}</span></div>
            <div style="text-align:center; padding:15px; color:#00f2ff; font-size:20px;">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffa500;"><span>50% MIN</span> <span>{p50_min:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{min_proj:.2f}</span></div>
            <br>
            <div class="calc-row"><span>P. JUSTO</span> <span>{justo:.2f}</span></div>
            <div class="calc-row"><span>SPREED</span> <span style="color:#00f2ff;">{spreed:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

time.sleep(5)
st.rerun()
