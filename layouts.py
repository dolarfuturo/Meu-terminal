import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# Configuração para Tablet - Força o layout a não criar barras de rolagem desnecessárias
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS AVANÇADO: FIXAÇÃO E ALINHAMENTO ---
st.markdown("""
<style>
    /* Esconde elementos nativos do Streamlit */
    header[data-testid="stHeader"] { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .stApp { background-color: #050a0e !important; }
    
    /* Ajuste de margens do container principal */
    .block-container { padding: 0rem 1rem !important; max-width: 100% !important; }

    /* Estilo da Grade Principal */
    .main-grid { border: 2px solid #ffffff; border-radius: 6px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 8px; text-align: center; font-size: 12px; }
    .terminal-table td { border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 14px; }
    .asset-name { font-size: 15px; color: #fff; text-align: left; font-weight: bold; padding-left: 12px; }

    /* Painéis da Direita */
    .calc-panel { 
        border: 2px solid #ffffff; border-radius: 6px; background: #0a141a; 
        font-family: monospace; padding: 8px 5px; margin-bottom: 10px;
    }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #333; font-size: 13px; font-weight: bold; }

    /* Relógios */
    .clock-container { display: flex; gap: 8px; }
    .clock-box { text-align: center; border: 1px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 80px; }
    .clock-label { font-size: 9px; color: #d4a017; font-weight: bold; display: block; }
    .clock-time { color: #fff; font-size: 15px; font-weight: bold; }

    /* RODAPÉ FIXO NO FUNDO DA TELA */
    .ticker-fixed {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000; border-top: 2px solid #ffffff;
        padding: 6px 0; z-index: 999; overflow: hidden; white-space: nowrap;
    }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 50s linear infinite; font-family: 'monospace'; font-size: 13px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    /* Cores de Variação */
    .up { color: #00ff00 !important; }
    .down { color: #ff4d4d !important; }
</style>
""", unsafe_allow_html=True)

# --- TRATAMENTO DE DADOS (CORREÇÃO DE SINTAXE GARANTIDA) ---
def fetch_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="1m", prepost=True)
        prev_close = ticker.info.get('previousClose', 0)
        if hist.empty:
            return {"at": prev_close, "cl": prev_close, "mx": prev_close, "mn": prev_close, "op": prev_close}
        return {
            "at": hist['Close'].iloc[-1], "cl": prev_close, "op": hist['Open'].iloc[0],
            "mx": hist['High'].max(), "mn": hist['Low'].min()
        }
    except Exception:
        return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

def calcular_projeções(e_ewz, p_ewz, mx_e, mn_e, e_dol):
    try:
        v_at = ((e_ewz / p_ewz) - 1) * 100 / 1.5
        v_fr = ((e_ewz / p_ewz) - 1) * 100 / 4.5
        ewz_m = (mx_e + mn_e) / 2
        v_m = ((e_ewz / ewz_m) - 1) * 100
        v_neg = ((e_ewz / mx_e) - 1) * 100 / 1.5
        v_pos = ((e_ewz / mn_e) - 1) * 100 / 1.5
        a_max = e_dol * (1 + (v_pos / 100))
        a_min = e_dol * (1 + (v_neg / 100))
        return {
            "vivo": e_dol * (1 + (v_at / 100)), "fraja": e_dol * (1 + (v_fr / 100)), "medio": e_dol * (1 + (v_m / 100)),
            "ewz_med": ewz_m, "max": a_max, "min": a_min,
            "p75_up": (e_dol + (a_max - e_dol)*0.75), "p50_up": (e_dol + a_max) / 2, 
            "p25_up": (e_dol + (a_max - e_dol)*0.25), "p75_down": (e_dol + (a_min - e_dol)*0.75), 
            "p50_down": (e_dol + a_min) / 2, "p25_down": (e_dol + (a_min - e_dol)*0.25)
        }
    except Exception: return None

# --- SIDEBAR (PAINEL DE CONTROLE ADM) ---
with st.sidebar:
    st.header("⚙️ CONFIGURAÇÃO AXIS")
    st.info("Ajuste os valores abaixo para atualizar o terminal.")
    axis_ewz = st.number_input("AXIS EWZ", value=36.42, step=0.01, format="%.2f")
    axis_dol = st.number_input("AXIS DOLFUT", value=5274.0, step=1.0, format="%.2f")
    if st.button("ATUALIZAR AGORA"): st.rerun()

# --- HEADER COM LOGO E RELÓGIOS ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:2.5px solid #fff; margin-bottom:15px;">
    <div style="font-size:35px; font-weight:950; font-family:monospace;"><span style="color:#00f2ff;">BAIR</span><span style="color:#fff;"> - </span><span style="color:#d4a017;">TERMINAL DOLAR</span></div>
    <div class="clock-container">
        <div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div>
        <div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div>
    </div>
</div>""", unsafe_allow_html=True)

# --- BUSCA E PROCESSAMENTO ---
ewz_data = fetch_data("EWZ")
res = calcular_projeções(axis_ewz, ewz_data['at'], ewz_data['mx'], ewz_data['mn'], axis_dol)

if res:
    c1, c2 = st.columns([3.1, 1])
    
    with c1:
        st.markdown('<div style="background:#0a141a; border:2px solid #fff; padding:4px; text-align:center; color:#00f2ff; font-weight:bold; margin-bottom:5px; font-size:11px;">GRADE PRINCIPAL DE ATIVOS</div>', unsafe_allow_html=True)
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        ativos = {"DOLFUT": "BRL=X", "SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
        ticker_items = []

        for label, symbol in ativos.items():
            d = fetch_data(symbol)
            var = ((d['at']/d['cl'])-1)*100 if d['cl'] > 0 else 0
            cor_class = "up" if var >= 0 else "down"
            html_table += f"<tr><td class='asset-name'>{label}</td><td style='color:#00f2ff; font-weight:bold;'>{d['at']:.4f}</td><td>{d['cl']:.4f}</td><td>{d['op']:.4f}</td><td>{d['mx']:.4f}</td><td>{d['mn']:.4f}</td><td class='{cor_class}'>{var:+.2f}%</td></tr>"
            ticker_items.append(f"{label}: <span class='{cor_class}'>{var:+.2f}%</span>")
        
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div style="background:#0a141a; border:2px solid #fff; padding:4px; text-align:center; color:#00f2ff; font-weight:bold; margin-bottom:5px; font-size:11px;">PROJEÇÕES</div>', unsafe_allow_html=True)
        # Painel Superior (Ajustado para ocupar a altura da tabela)
        st.markdown(f"""<div class="calc-panel" style="min-height:385px; display:flex; flex-direction:column; justify-content:space-between;">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div>
            <div style="text-align:center; padding: 12px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444;">AXIS: {axis_dol:.2f}</div>
            <div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom:none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
        </div>""", unsafe_allow_html=True)
        
        # Painel Inferior
        st.markdown(f"""<div class="calc-panel">
            <div class="calc-row"><span style="color:#fff;">DOLFUT</span> <span style="color:#00f2ff; font-size:15px;">{res['vivo']:.2f}</span></div>
            <div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff;">{res['medio']:.2f}</span></div>
            <div class="calc-row" style="border-bottom:none;"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#fff;">{res['fraja']:.2f}</span></div>
            <div style="display:flex; justify-content:space-around; padding-top:8px; border-top:1px solid #444; margin-top:5px;">
                <span class="up" style="font-size:11px;">{ewz_data['mx']:.2f}</span>
                <span style="color:#00f2ff; font-size:11px;">{res['ewz_med']:.2f}</span>
                <span class="down" style="font-size:11px;">{ewz_data['mn']:.2f}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # RODAPÉ FIXO COLORIDO
    ticker_content = " • ".join(ticker_items)
    st.markdown(f"""<div class="ticker-fixed"><div class="ticker-text">{ticker_content} • {ticker_content}</div></div>""", unsafe_allow_html=True)

# Loop de atualização
time.sleep(10)
st.rerun()
