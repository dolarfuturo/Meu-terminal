import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR")

# --- CSS: ESTILIZAÇÃO COMPACTA RESTAURADA E MANTIDA ---
st.markdown("""
<style>
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
    .ewz-mini-container { display: flex; justify-content: space-around; padding: 4px 0; border-top: 1px solid #444; margin-top: 4px; }
    .ewz-mini-val { font-size: 11px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def fetch(s):
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        ref_close = t.info.get('previousClose')
        
        if s == "EWZ":
            d_hist = t.history(period="3d", interval="1m", prepost=True)
            if not d_hist.empty:
                d_hist.index = d_hist.index.tz_convert(tz_sp)
                unique_dates = sorted(list(set(d_hist.index.date)))
                data_anterior = unique_dates[-2] if len(unique_dates) > 1 else unique_dates[0]
                f_21h = d_hist.between_time('05:00', '21:00').loc[d_hist.index.date == data_anterior]
                if not f_21h.empty:
                    ref_close = f_21h['Close'].iloc[-1]

        d = t.history(period="1d", interval="1m", prepost=True)
        if d.empty: 
            return {"at": 0.0, "cl": ref_close or 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}
        
        # Ajuste de escala para Dólar (Yahoo fornece 5.30 ao invés de 5300)
        mult = 1000 if s in ["USDBRL=X", "BRL=X"] else 1
        return {
            "at": d['Close'].iloc[-1] * mult, 
            "cl": (ref_close or d['Open'].iloc[0]) * mult, 
            "op": d['Open'].iloc[0] * mult,
            "mx": d['High'].max() * mult, 
            "mn": d['Low'].min() * mult
        }
    except: return {"at": 0.0, "cl": 0.0, "mx": 0.0, "mn": 0.0, "op": 0.0}

@st.cache_data(ttl=600)
def calcular_sentinela():
    try:
        t = yf.Ticker("EWZ")
        df = t.history(period="7d", interval="1d", prepost=False)
        if df.empty: return 37.85
        
        tz_sp = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(tz_sp)
        hoje = agora.date()
        ultima_data_yahoo = df.index[-1].date()
        
        if ultima_data_yahoo == hoje and agora.hour < 18:
            idx = -2 
        else:
            idx = -1 
            
        return (df['High'].iloc[idx] + df['Low'].iloc[idx]) / 2
    except: return 37.85

# --- PAINEL ADM ---
eixo_sug = calcular_sentinela()
with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    with st.form("ajuste_vars"):
        a_ewz = st.number_input("AXIS EWZ:", value=float(eixo_sug), format="%.2f")
        a_dol = st.number_input("AXIS DOLFUT:", value=5246.00, format="%.2f")
        st.markdown(f"<div style='color:#d4a017; font-weight:bold; margin-top:5px;'>SENTINELA: {eixo_sug:.2f}</div>", unsafe_allow_html=True)
        st.form_submit_button("SALVAR")

# --- UI HEADER ---
tz_sp, tz_ny, tz_ld = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London')
st.markdown(f"""<div class="header-bair"><div class="title-box"><span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span></div><div class="clock-container"><div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M')}</span></div><div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

# Captura dados em tempo real
ewz_live = fetch("EWZ")
spot_live = fetch("USDBRL=X") # DOLSPOT É A ÂNCORA DE VOLATILIDADE

# --- LÓGICA DE CÁLCULO SHARK AJUSTADA E BLINDADA ---
if spot_live:
    # 1. CÁLCULO DO SPREDD EM TEMPO REAL (DA MÁXIMA/MÍNIMA DO SPOT)
    # Fórmula: ( MAX_spot - MIN_spot /8)
    mx_s = spot_live['mx']
    mn_s = spot_live['mn']
    spreedd = (mx_s - mn_s) / 8 if mx_s > 0 else 0
    
    # 2. PROJEÇÕES DO BLOCO SETA VERMELHA (BASEADAS NO AXIS DO FUTURO)
    # Fórmula Max do Fut: AXIS + Max do spot + SPREED
    # Fórmula Min do Fut: AXIS - Min do spot + SPREED
    max_shark = a_dol + mx_s + spreedd
    min_shark = a_dol - mn_s + spreedd
    
    # Manutenção dos níveis proporcionais (25%, 50%, 75%) baseados nas novas pontas e no Axis fixo
    p75_up = (a_dol + (max_shark - a_dol) * 0.75)
    p50_up = (a_dol + max_shark) / 2 # Média entre Axis e Max Shark
    p25_up = (a_dol + (max_shark - a_dol) * 0.25)
    
    p75_down = (a_dol + (min_shark - a_dol) * 0.75)
    p50_down = (a_dol + min_shark) / 2 # Média entre Axis e Min Shark
    p25_down = (a_dol + (min_shark - a_dol) * 0.25)
    
    # 3. BLOCO INFERIOR (SETA VERDE - MÉDIA DOL)
    # Fórmula: ( MAX_spot + MIN_spot ) / 2
    media_dol_shark = (mx_s + mn_s) / 2
    
    # Variações e Dolar Vivo (mantidos para tabela e painel inferior)
    v_spot = ((spot_live['at'] / spot_live['cl']) - 1) if spot_live['cl'] > 0 else 0
    v_ewz = ((ewz_live['at'] / fetch("EWZ")['cl']) - 1) if fetch("EWZ")['cl'] > 0 else 0
    v_final = (v_spot * 0.6) - (v_ewz * 0.4)
    dolar_vivo = a_dol * (1 + v_final)
    dolar_fraja = a_dol * (1 + (v_final / 2)) # P. Justo conforme estrutura original
    ewz_medio_dia = (ewz_live['mx'] + ewz_live['mn']) / 2

    c_main, c_side = st.columns([3, 1])
    
    with c_main:
        # Tabela Principal Restaurada (Não tirei nada)
        html_table = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        
        html_table += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(dolar_vivo/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(a_dol/1000):.4f}</td><td>{(max_shark/1000):.4f}</td><td>{(min_shark/1000):.4f}</td><td style='color:{("#00ff00" if v_final >= 0 else "#ff4d4d")}; font-weight:bold;'>{v_final*100:+.2f}%</td></tr>"
        ticker = []
        
        outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
        for lbl, sym in outros.items():
            d = spot_live if lbl == "DOLSPOT" else (ewz_live if lbl == "EWZ" else fetch(sym))
            f = ".4f" if "USD" in lbl or "DOL" in lbl else ".2f"
            var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
            color = "#00ff00" if var >= 0 else "#ff4d4d"
            html_table += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['op']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
            ticker.append(f"<span style='color:#fff;'>{lbl}:</span> <span style='color:{color};'>{var:+.2f}%</span>")
        st.markdown(html_table + "</tbody></table></div>", unsafe_allow_html=True)

    with c_side:
        # PAINEL DA SETA VERMELHA RESTAURADO (COM TODAS AS LINHAS), MAS COM MATEMÁTICA CORRIGIDA
        st.markdown(f"""
        <div class="calc-panel">
            <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{max_shark:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{p75_up:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{p50_up:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{p25_up:.2f}</span></div>
            <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {a_dol:.2f}</div>
            <div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{p25_down:.2f}</span></div>
            <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{p50_down:.2f}</span></div>
            <div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{p75_down:.2f}</span></div>
            <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{min_shark:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # PAINEL INFERIOR RESTAURADO (COM MÉDIA DOL CORRIGIDA)
        st.markdown(f"""
        <div class="calc-panel">
            <div class="calc-row" style="padding: 10px 8px;"><span style="color:#ffffff;">DOLFUT VIVO</span> <span style="color:#00f2ff; font-size: 16px; font-weight: 950;">{dolar_vivo:.2f}</span></div>
            <div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff; font-size: 16px;">{media_dol_shark:.2f}</span></div>
            <div class="calc-row" style="border-bottom: none;"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#ffffff; font-size: 16px; font-weight: bold;">{dolar_fraja:.2f}</span></div>
            <div style="font-size: 10px; color: #666; text-align: center; margin-top: 5px;">SPREDD APLICADO: {spreedd:.2f}</div>
            <div class="ewz-mini-container"><span class="ewz-mini-val" style="color:#00ff88;">{ewz_live['mx']:.2f}</span><span class="ewz-mini-val" style="color:#00f2ff;">{ewz_medio_dia:.2f}</span><span class="ewz-mini-val" style="color:#ff4d4d;">{ewz_live['mn']:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker)}</div></div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
