import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO DE TELA
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL", initial_sidebar_state="collapsed")

# --- 2. ESTADO DO SISTEMA ---
if 'a_ewz' not in st.session_state: st.session_state.a_ewz = 37.85
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00

# --- 3. CSS: TERMINAL PROFISSIONAL ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background-color: #050a0e !important; }
    
    /* ESTILO DO EXPANDER (A GAVETA) */
    .stDetails { border: 1px solid #d4a017 !important; background-color: #0a141a !important; border-radius: 8px !important; }
    .stDetails summary { color: #d4a017 !important; font-weight: bold; font-family: monospace; }

    /* TABELA */
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; font-family: monospace; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-transform: uppercase; font-size: 13px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 16px; }
    .asset-name { font-size: 18px; color: #fff; text-align: left !important; font-weight: bold; padding-left: 15px !important; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    
    /* HEADER */
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 10px; }
    .bair-text { font-size: 42px; color: #00f2ff; font-weight: 950; font-family: monospace; } 
    .term-text { font-size: 42px; color: #d4a017; font-weight: 950; font-family: monospace; }
    .clock-box { border: 1.5px solid #ffffff; padding: 5px 15px; border-radius: 4px; background: #0a141a; color: #fff; font-size: 28px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- 4. PAINEL ADM (GAVETA RETRÁTIL NO TOPO) ---
with st.expander("▶ CONFIGURAR EIXOS (SET ADM)"):
    with st.form("set_form"):
        col_adm1, col_adm2 = st.columns(2)
        new_ewz = col_adm1.number_input("AXIS EWZ", value=st.session_state.a_ewz, format="%.2f")
        new_dol = col_adm2.number_input("AXIS DOLFUT", value=st.session_state.a_dol, format="%.2f")
        if st.form_submit_button("SALVAR AJUSTES"):
            st.session_state.a_ewz = new_ewz
            st.session_state.a_dol = new_dol
            st.rerun()

# --- 5. FUNÇÃO DE DADOS ---
def fetch_safe(s):
    try:
        t = yf.Ticker(s)
        d = t.history(period="1d", interval="1m")
        if d.empty: return {"at":0.0001, "cl":0.0001, "mx":0.0001, "mn":0.0001}
        m = 1000 if s == "USDBRL=X" else 1
        return {"at": d['Close'].iloc[-1]*m, "cl": t.info.get('previousClose', d['Open'].iloc[0])*m, "mx": d['High'].max()*m, "mn": d['Low'].min()*m}
    except: return {"at":0.0001, "cl":0.0001, "mx":0.0001, "mn":0.0001}

# --- 6. MOTOR DO TERMINAL ---
main_space = st.empty()

while True:
    spot = fetch_safe("USDBRL=X")
    ewz = fetch_safe("EWZ")
    dxy = fetch_safe("DX-Y.NYB")
    
    # Cálculos Nexus
    v_spot = (spot['at'] / spot['cl'] - 1) if spot['cl'] > 0 else 0
    v_ewz = (ewz['at'] / ewz['cl'] - 1) if ewz['cl'] > 0 else 0
    v_calc = (v_spot * 0.6) - (v_ewz * 0.4)
    p_justo = st.session_state.a_dol * (1 + (v_calc / 2))

    with main_space.container():
        # Renderização do Header
        st.markdown(f"""
        <div class="header-bair">
            <div><span class="bair-text">BAIR</span><span class="term-text">-TERMINAL</span></div>
            <div class="clock-box">{datetime.now().strftime('%H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([3, 1])
        with c1:
            # Tabela (Com blindagem de erro)
            html = """<div class="main-grid"><table class="terminal-table"><tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>MAX</th><th>MIN</th><th>VAR</th></tr>"""
            ativos = [
                ("DOLFUT (CALC)", p_justo, st.session_state.a_dol, spot['mx'], spot['mn'], v_calc*100),
                ("DOLSPOT", spot['at'], spot['cl'], spot['mx'], spot['mn'], v_spot*100),
                ("EWZ", ewz['at'], ewz['cl'], ewz['mx'], ewz['mn'], v_ewz*100),
                ("DXY", dxy['at'], dxy['cl'], dxy['mx'], dxy['mn'], (dxy['at']/dxy['cl']-1)*100 if dxy['cl'] > 0 else 0)
            ]
            for n, at, cl, mx, mn, vr in ativos:
                div = 1000 if "DOL" in n else 1
                f = ".4f" if "DOL" in n else ".2f"
                html += f"""<tr><td class="asset-name">{n}</td><td class="price-col">{(at/div if at else 0):{f}}</td><td>{(cl/div if cl else 0):{f}}</td><td>{(mx/div if mx else 0):{f}}</td><td>{(mn/div if mn else 0):{f}}</td><td style="color:{('#00ff88' if vr>=0 else '#ff4d4d')}; font-weight:bold;">{vr:+.2f}%</td></tr>"""
            st.markdown(html + "</table></div>", unsafe_allow_html=True)

        with c2:
            # Painel Lateral de Resumo
            st.markdown(f"""
            <div style="border:2.5px solid #fff; border-radius:8px; padding:20px; background:#0a141a; text-align:center;">
                <div style="color:#d4a017; font-size:14px; font-weight:bold;">AXIS DOLFUT</div>
                <div style="color:#fff; font-size:32px; font-weight:bold;">{st.session_state.a_dol:.2f}</div>
                <hr style="border:0.5px solid #333; margin:15px 0;">
                <div style="color:#00f2ff; font-size:14px;">PREÇO JUSTO</div>
                <div style="color:#fff; font-size:24px; font-weight:bold;">{p_justo:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
    time.sleep(2)
