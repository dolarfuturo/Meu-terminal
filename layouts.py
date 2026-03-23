import streamlit as st
import yfinance as yf
import time

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL")

# --- CSS: PADRÃO BAIR ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; background-color: #0d1b22; font-family: 'monospace'; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 18px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 10px; background: #0a141a; font-family: monospace; }
    .calc-row { display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #444; font-size: 15px; font-weight: bold; }
    .axis-center { text-align: center; padding: 15px; color: #00f2ff; font-size: 24px; border-top: 2px solid #fff; border-bottom: 2px solid #fff; margin: 10px 0; }
    h1 { color: #00f2ff; font-family: monospace; font-weight: 950; }
</style>
""", unsafe_allow_html=True)

# --- BUSCA DE DADOS (SPOT) ---
def get_spot():
    try:
        t = yf.Ticker("USDBRL=X")
        d = t.history(period="1d", interval="1m")
        if d.empty: return {"mx": 0.0, "mn": 0.0}
        # Multiplicado por 1000 para escala de milhar
        return {"mx": d['High'].max() * 1000, "mn": d['Low'].min() * 1000}
    except: return {"mx": 0.0, "mn": 0.0}

# --- ENTRADA DE DADOS ---
with st.sidebar:
    a_dol = st.number_input("AXIS DOLFUT:", value=5308.00)
    st.button("ATUALIZAR")

spot = get_spot()

if spot["mx"] > 0:
    # --- EXECUÇÃO DAS SUAS INSTRUÇÕES ---
    
    # 1. SPREED (Amplitude do spot / 8)
    v_spreed = (spot['mx'] - spot['mn']) / 8
    
    # 2. MÁXIMA = AXIS + MAX SPOT + SPREED
    max_final = a_dol + spot['mx'] + v_spreed
    
    # 3. MÍNIMA = AXIS - MIN SPOT + SPREED
    min_final = a_dol - spot['mn'] + v_spreed
    
    # Pontos de 50%
    p50_up = (max_final + a_dol) / 2
    p50_down = (min_final + a_dol) / 2

    # --- RENDERIZAÇÃO ---
    st.markdown("<h1>BAIR SYSTEM</h1>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.markdown(f"""
        <div class="main-grid">
            <table class="terminal-table">
                <tr><td>ATIVO</td><td>AXIS</td><td>MAX SPOT</td><td>MIN SPOT</td></tr>
                <tr>
                    <td style="color:#fff; font-weight:bold;">DOLFUT</td>
                    <td class="price-col">{a_dol:.2f}</td>
                    <td>{spot['mx']:.2f}</td>
                    <td>{spot['mn']:.2f}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
        <div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{max_final:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>50% MAX</span> <span>{p50_up:.2f}</span></div>
            <div class="axis-center">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffa500;"><span>50% MIN</span> <span>{p50_down:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MÍNIMA</span> <span>{min_final:.2f}</span></div>
        </div>
        <div class="calc-panel" style="margin-top:10px;">
            <div class="calc-row" style="border-bottom:none;"><span>SPREED</span> <span style="color:#00f2ff;">{v_spreed:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

# Auto-refresh
time.sleep(5)
st.rerun()
