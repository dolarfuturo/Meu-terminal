import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO DE TELA
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL", initial_sidebar_state="collapsed")

# --- 2. ESTADO DO SISTEMA (PERSISTÊNCIA DOS EIXOS) ---
if 'a_ewz' not in st.session_state: st.session_state.a_ewz = 37.85
if 'a_dol' not in st.session_state: st.session_state.a_dol = 5246.00

# --- 3. CSS: GAVETA LATERAL E CHASSI NEXUS ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background-color: #050a0e !important; }
    
    /* GAVETA LATERAL (SIDEBAR) */
    section[data-testid="stSidebar"] { 
        background-color: #0a141a !important; 
        border-right: 2px solid #d4a017 !important; 
        width: 260px !important;
    }
    
    /* TABELA ESTILO TERMINAL */
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; background-color: #0d1b22; margin-top: 10px; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; font-family: 'Courier New', monospace; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 12px; text-transform: uppercase; font-size: 14px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 14px; text-align: center; font-size: 16px; font-weight: 500; }
    .asset-name { font-size: 18px; color: #fff; text-align: left !important; font-weight: 900; padding-left: 20px !important; background: #0f1f27; }
    .price-col { color: #00f2ff !important; font-weight: bold; font-size: 18px; }
    
    /* HEADER E RELÓGIO */
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px 5px; border-bottom: 2.5px solid #ffffff; margin-bottom: 10px; }
    .bair-text { font-size: 48px; color: #00f2ff; font-weight: 950; font-family: monospace; letter-spacing: -2px; } 
    .term-text { font-size: 48px; color: #d4a017; font-weight: 950; font-family: monospace; letter-spacing: -2px; }
    .clock-box { border: 2px solid #ffffff; padding: 8px 20px; border-radius: 6px; background: #0a141a; color: #fff; font-size: 32px; font-weight: bold; font-family: monospace; box-shadow: 0 0 10px #00f2ff33; }
    
    /* BARRA DE FORÇA (K97) */
    .bar-wrapper { background: #0a141a; padding: 20px; border: 2.5px solid #ffffff; border-radius: 8px; text-align: center; }
    .force-container { background: #111; height: 25px; width: 100%; position: relative; display: flex; border: 1px solid #444; overflow: hidden; border-radius: 4px; }
    .fill-green { background: #00ff88; height: 100%; transition: width 0.6s ease-in-out; }
    .fill-red { background: #ff4d4d; height: 100%; transition: width 0.6s ease-in-out; }
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.2; } }
</style>
""", unsafe_allow_html=True)

# --- 4. GAVETA LATERAL ADM (SET) ---
with st.sidebar:
    st.markdown("<h1 style='color:#d4a017; font-family:monospace; text-align:center;'>SET ADM</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #d4a017;'>", unsafe_allow_html=True)
    with st.form("set_form"):
        new_ewz = st.number_input("EIXO EWZ", value=st.session_state.a_ewz, format="%.2f", step=0.05)
        new_dol = st.number_input("EIXO DOLFUT", value=st.session_state.a_dol, format="%.2f", step=1.0)
        if st.form_submit_button("✅ ATUALIZAR EIXOS"):
            st.session_state.a_ewz = new_ewz
            st.session_state.a_dol = new_dol
            st.rerun()
    st.markdown("<p style='font-size:12px; color:#666; text-align:center; margin-top:20px;'>Clique na seta lateral para fechar este painel.</p>", unsafe_allow_html=True)

# --- 5. FUNÇÃO DE COLETA (COM BLINDAGEM ANTI-ERRO) ---
def fetch_nexus(symbol):
    try:
        t = yf.Ticker(symbol)
        d = t.history(period="1d", interval="1m")
        if d.empty: return {"at":0.0, "cl":0.0, "mx":0.0, "mn":0.0}
        m = 1000 if symbol == "USDBRL=X" else 1
        return {
            "at": float(d['Close'].iloc[-1] * m),
            "cl": float(t.info.get('previousClose', d['Open'].iloc[0]) * m),
            "mx": float(d['High'].max() * m),
            "mn": float(d['Low'].min() * m)
        }
    except:
        return {"at":0.0, "cl":0.0, "mx":0.0, "mn":0.0}

# --- 6. MOTOR DE RENDERIZAÇÃO ---
main_placeholder = st.empty()

while True:
    # Captura de dados
    spot = fetch_nexus("USDBRL=X")
    ewz = fetch_nexus("EWZ")
    dxy = fetch_nexus("DX-Y.NYB")
    
    # Cálculos Nexus
    v_spot = (spot['at'] / spot['cl'] - 1) if spot['cl'] > 0 else 0
    v_ewz = (ewz['at'] / ewz['cl'] - 1) if ewz['cl'] > 0 else 0
    v_calc = (v_spot * 0.6) - (v_ewz * 0.4)
    p_justo = st.session_state.a_dol * (1 + (v_calc / 2))
    
    # Lógica de Intensidade (Sinal)
    diff = spot['at'] - st.session_state.a_dol
    pr = min(100, abs(diff)/12 * 100) if diff > 0 else 0
    pv = min(100, abs(diff)/12 * 100) if diff < 0 else 0

    with main_placeholder.container():
        # Bloco Superior
        st.markdown(f"""
        <div class="header-bair">
            <div><span class="bair-text">BAIR</span><span class="term-text">-TERMINAL</span></div>
            <div class="clock-box">{datetime.now().strftime('%H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col_main, col_side = st.columns([3, 1])
        
        with col_main:
            # Tabela Nexus (Blindada contra ValueError)
            html = """<div class="main-grid"><table class="terminal-table">
            <tr><th>ATIVO</th><th>PRICE</th><th>CLOSE</th><th>MAX</th><th>MIN</th><th>VAR%</th></tr>"""
            
            ativos_lista = [
                ("DOLFUT (CALC)", p_justo, st.session_state.a_dol, spot['mx'], spot['mn'], v_calc*100),
                ("DOLSPOT", spot['at'], spot['cl'], spot['mx'], spot['mn'], v_spot*100),
                ("EWZ", ewz['at'], ewz['cl'], ewz['mx'], ewz['mn'], v_ewz*100),
                ("DXY", dxy['at'], dxy['cl'], dxy['mx'], dxy['mn'], (dxy['at']/dxy['cl']-1)*100 if dxy['cl'] > 0 else 0)
            ]
            
            for nome, preco, fechamento, maxima, minima, variacao in ativos_lista:
                # Segurança: Se o preço for zero, evita erro de formato
                div = 1000 if "DOL" in nome else 1
                fmt = ".4f" if "DOL" in nome else ".2f"
                cor_var = "#00ff88" if variacao >= 0 else "#ff4d4d"
                
                # Renderização da Linha
                html += f"""<tr>
                    <td class="asset-name">{nome}</td>
                    <td class="price-col">{(preco/div if preco else 0):{fmt}}</td>
                    <td>{(fechamento/div if fechamento else 0):{fmt}}</td>
                    <td>{(maxima/div if maxima else 0):{fmt}}</td>
                    <td>{(minima/div if minima else 0):{fmt}}</td>
                    <td style="color:{cor_var}; font-weight:bold;">{variacao:+.2f}%</td>
                </tr>"""
            
            st.markdown(html + "</table></div>", unsafe_allow_html=True)

        with col_side:
            # Painel de Status
            st.markdown(f"""
            <div style="border:2.5px solid #fff; border-radius:8px; padding:20px; background:#0a141a; text-align:center; margin-bottom:12px;">
                <div style="color:#d4a017; font-size:14px; font-weight:bold; letter-spacing:1px;">EIXO DOLFUT</div>
                <div style="color:#fff; font-size:36px; font-weight:900; font-family:monospace;">{st.session_state.a_dol:.2f}</div>
                <hr style="border:0.5px solid #333; margin:15px 0;">
                <div style="color:#00f2ff; font-size:14px;">PREÇO JUSTO</div>
                <div style="color:#fff; font-size:24px; font-weight:bold;">{p_justo:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # K97 Force Bar
            st.markdown(f"""
            <div class="bar-wrapper">
                <div class="force-container">
                    <div class="fill-green" style="width:{pv}%"></div>
                    <div style="width:3px; background:#fff; z-index:10;"></div>
                    <div class="fill-red" style="width:{pr}%"></div>
                </div>
                <div class="blink" style="margin-top:20px; font-size:22px; font-weight:900; color:{('#00ff88' if pv>pr else '#ff4d4d' if pr>pv else '#555')}">
                    {('▲ COMPRA' if pv>80 else '▼ VENDA' if pr>80 else '--- AGUARDE ---')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    time.sleep(2)
