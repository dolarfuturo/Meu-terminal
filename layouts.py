import streamlit as st
import yfinance as yf
import time
from datetime import datetime
import pytz

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- CSS: TRAVA ANTI-PISCADA (IGUAL CRYPTO) ---
st.markdown("""
<style>
    /* Oculta a barra de progresso e o bonequinho de 'running' */
    [data-testid="stStatusWidget"] { display: none !important; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container { padding-top: 0rem !important; }

    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 2.5px solid #ffffff; margin-bottom: 12px; }
    .title-box { display: flex; align-items: center; gap: 8px; line-height: 1; }
    .bair-text { font-size: 46px; color: #00f2ff; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; } 
    .sep-text { font-size: 46px; color: #ffffff; font-weight: 950; margin: 0 5px; }
    .terminal-text { font-size: 46px; color: #d4a017; font-weight: 950; font-family: 'monospace'; letter-spacing: -1px; }
    .clock-container { display: flex; gap: 10px; color: #888; font-family: 'monospace'; }
    .clock-box { text-align: center; border: 1.5px solid #ffffff; padding: 4px 10px; border-radius: 4px; background: #0a141a; min-width: 95px; }
    .clock-label { font-size: 10px; color: #d4a017; font-weight: bold; display: block; text-transform: uppercase; margin-bottom: 2px; }
    .clock-time { color: #fff; font-size: 17px; font-weight: bold; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 8px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 5px 8px; border-bottom: 1px solid #444; font-size: 13px; font-weight: bold; align-items: center; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 15px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        f = t.fast_info
        return {"at": f['last_price'], "cl": f['previous_close'], "op": f['open'], "mx": f['day_high'], "mn": f['day_low']}
    except:
        return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

@st.cache_data(ttl=600)
def calcular_sentinela():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d")
        return (df['High'].iloc[-2] + df['Low'].iloc[-2]) / 2
    except: return 37.85

def calcular_k97_total(eixo_ewz, p_ewz_atual, max_ewz, min_ewz, eixo_dol):
    try:
        if p_ewz_atual <= 0: return None
        var_atual = ((eixo_ewz / p_ewz_atual) - 1) * 100 / 1.5
        dolar_vivo = eixo_dol * (1 + (var_atual / 100))
        var_fraja = ((eixo_ewz / p_ewz_atual) - 1) * 100 
        dolar_fraja = eixo_dol * (1 + (var_fraja / 100))
        ewz_medio_dia = (max_ewz + min_ewz) / 2
        var_medio = ((p_ewz_atual / ewz_medio_dia) - 1) * 100 if ewz_medio_dia > 0 else 0
        dolar_medio = eixo_dol * (1 + (var_medio / 100)) 
        v_neg = ((eixo_ewz / max_ewz) - 1) * 100 / 1.5 if max_ewz > 0 else 0
        v_pos = ((eixo_ewz / min_ewz) - 1) * 100 / 1.5 if min_ewz > 0 else 0
        alvo_max, alvo_min = eixo_dol * (1 + (v_pos / 100)), eixo_dol * (1 + (v_neg / 100))
        return {
            "vivo": dolar_vivo, "fraja": dolar_fraja, "medio": dolar_medio, "ewz_med": ewz_medio_dia,
            "max": alvo_max, "min": alvo_min,
            "p75_up": (eixo_dol + (alvo_max - eixo_dol)*0.75), "p50_up": (eixo_dol + alvo_max) / 2, 
            "p25_up": (eixo_dol + (alvo_max - eixo_dol)*0.25), "p75_down": (eixo_dol + (alvo_min - eixo_dol)*0.75), 
            "p50_down": (eixo_dol + alvo_min) / 2, "p25_down": (eixo_dol + (alvo_min - eixo_dol)*0.25)
        }
    except: return None

# --- PAINEL ADM (FORA DO LOOP) ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    # Usamos o form para o botão de acesso/salvamento funcionar
    with st.form("config_form"):
        a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        submit = st.form_submit_button("SALVAR E ATUALIZAR")
        if submit:
            st.success("Configurações Aplicadas!")

# --- ÁREA DO TERMINAL (LOOP INFINITO) ---
placeholder = st.empty()

while True:
    # 1. Coleta dados
    ewz_live = fetch("EWZ")
    res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol)
    
    if res:
        with placeholder.container():
            tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
            
            # Cabeçalho com Relógios
            st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M:%S')}</span></div><div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M:%S')}</span></div><div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M:%S')}</span></div></div></div>""", unsafe_allow_html=True)

            c1, c2 = st.columns([3, 1])
            with c1:
                v_v = ((res['vivo']/a_dol)-1)*100
                html = f"""<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>
                <tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{"#00ff00" if v_v >= 0 else "#ff4d4d"}; font-weight:bold;'>{v_v:+.2f}%</td></tr>"""
                
                ticker = [f"DOLFUT: {v_v:+.2f}%"]
                outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "BRENT": "BZ=F"}
                
                for lbl, sym in outros.items():
                    d = fetch(sym)
                    var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                    f = ".4f" if "USD" in lbl or "DOL" in lbl else ".2f"
                    html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['op']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{"#00ff00" if var >=0 else "#ff4d4d"}; font-weight:bold;'>{var:+.2f}%</td></tr>"
                    ticker.append(f"{lbl}: {var:+.2f}%")
                
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

            with c2:
                # Paineis laterais
                st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {a_dol:.2f}</div><div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div><div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div><div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div><div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="padding: 10px 8px;"><span style="color:#ffffff;">DOLFUT</span> <span style="color:#00f2ff; font-size: 16px; font-weight: 950;">{res['vivo']:.2f}</span></div><div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff; font-size: 16px;">{res['medio']:.2f}</span></div><div class="calc-row" style="border-bottom: none;"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#ffffff; font-size: 16px; font-weight: bold;">{res['fraja']:.2f}</span></div><div style="display: flex; justify-content: space-around; padding: 4px 0; border-top: 1px solid #444; margin-top: 4px;"><span style="font-size: 11px; font-weight: bold; color:#00ff88;">{ewz_live['mx']:.2f}</span><span style="font-size: 11px; font-weight: bold; color:#00f2ff;">{res['ewz_med']:.2f}</span><span style="font-size: 11px; font-weight: bold; color:#ff4d4d;">{ewz_live['mn']:.2f}</span></div></div>""", unsafe_allow_html=True)

            st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker)} • {" • ".join(ticker)}</div></div>', unsafe_allow_html=True)

    time.sleep(1) 
