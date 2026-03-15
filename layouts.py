import streamlit as st
import yfinance as yf
import time
from datetime import datetime, time as dt_time
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLAR")

# --- CSS: ESTILIZAÇÃO REFINADA ---
st.markdown("""
<style>
    .stApp { background-color: #050a0e !important; }
    .main-grid { border: 2.5px solid #ffffff; border-radius: 8px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 10px; text-align: center; font-size: 13px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 12px; text-align: center; font-size: 15px; }
    .asset-name { font-size: 17px; color: #fff; text-align: left; font-weight: bold; padding-left: 15px; }
    .price-col { color: #00f2ff !important; font-weight: bold; }
    .header-bair { display: flex; justify-content: space-between; align-items: center; padding: 10px; color: #00f2ff; font-weight: bold; }
    .bair-text { font-size: 42px; letter-spacing: 2px; } 
    .terminal-text { font-size: 26px; color: #d4a017; }
    .clock-container { display: flex; gap: 20px; color: #888; font-family: 'monospace'; font-size: 12px; }
    .clock-box { text-align: center; border: 1px solid #ffffff; padding: 5px; border-radius: 4px; background: #0a141a; }
    .clock-time { color: #fff; font-size: 16px; display: block; }
    .calc-panel { border: 2.5px solid #ffffff; border-radius: 8px; padding: 10px; background: #0a141a; font-family: monospace; margin-bottom: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 6px 8px; border-bottom: 1px solid #444; font-size: 14px; font-weight: bold; }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 8px 0; overflow: hidden; white-space: nowrap; margin-top: 20px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 45s linear infinite; font-family: 'monospace'; font-size: 14px; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .monitor-bar { background: #0a141a; border: 2px solid #ffffff; padding: 8px; text-align: center; color: #00f2ff; font-weight: bold; font-family: monospace; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# --- NOVO MOTOR DE DADOS COM FILTRO DE JANELA ---
def fetch_operacional(symbol):
    try:
        # Puxa 1m para garantir que pegamos a máxima real dentro do horário
        d = yf.Ticker(symbol).history(period="1d", interval="1m", prepost=False)
        if d.empty: return None
        
        # Converte para SP e filtra 10:30 - 17:00
        d.index = d.index.tz_convert('America/Sao_Paulo')
        d_op = d.between_time(dt_time(10, 30), dt_time(17, 0))
        
        if d_op.empty:
            return {"at": d['Close'].iloc[-1], "cl": d['Close'].iloc[0], "mx": d['High'].max(), "mn": d['Low'].min()}
            
        return {
            "at": d['Close'].iloc[-1],        # Último preço
            "cl": d['Close'].iloc[0],         # Fechamento anterior (referência de variação)
            "mx": d_op['High'].max(),         # MAX SÓ ENTRE 10:30 e 17:00
            "mn": d_op['Low'].min()           # MIN SÓ ENTRE 10:30 e 17:00
        }
    except: return None

# --- SIDEBAR / PAINEL ADM ---
ewz_ref_data = fetch_operacional("EWZ")
mx_ref = ewz_ref_data['mx'] if ewz_ref_data else 38.10
mn_ref = ewz_ref_data['mn'] if ewz_ref_data else 37.60
eixo_sugerido = (mx_ref + mn_ref) / 2

with st.sidebar:
    st.markdown("### ⚙️ PAINEL ADM")
    with st.form("ajuste_eixo"):
        e_ewz = st.number_input("EIXO EWZ:", value=float(eixo_sugerido), format="%.2f")
        e_dol = st.number_input("EIXO DOLFUT:", value=5246.00, format="%.2f")
        salvar = st.form_submit_button("SALVAR VARIÁVEIS")
    st.divider()
    st.write(f"**REF MAX (10:30-17h):** {mx_ref:.2f}")
    st.write(f"**REF MIN (10:30-17h):** {mn_ref:.2f}")

# --- CÁLCULOS ---
def calcular_k97(eixo_ewz, ewz_atual, mx_ewz, mn_ewz, eixo_dol):
    v_at = ((eixo_ewz / ewz_atual) - 1) * 100 / 1.5
    d_vivo = eixo_dol * (1 + (v_at / 100))
    v_mx = ((eixo_ewz / mx_ewz) - 1) * 100 / 1.5
    v_mn = ((eixo_ewz / mn_ewz) - 1) * 100 / 1.5
    a_mx, a_mn = eixo_dol * (1 + (v_mn / 100)), eixo_dol * (1 + (v_mx / 100))
    return {
        "vivo": d_vivo, "max": a_mx, "min": a_mn,
        "fraja": eixo_dol * (1 + (((eixo_ewz / ewz_atual) - 1) * 100 / 4.5 / 100)),
        "medio": eixo_dol * (1 + (((eixo_ewz / ((mx_ewz + mn_ewz) / 2)) - 1) * 100 / 100)),
        "v_at": v_at, "v_med": ((eixo_ewz / ((mx_ewz + mn_ewz) / 2)) - 1) * 100,
        "p75_up": (e_dol + (a_mx - e_dol)*0.75), "p50_up": (e_dol + a_mx) / 2, "p25_up": (e_dol + (a_mx - e_dol)*0.25),
        "p75_dn": (e_dol + (a_mn - e_dol)*0.75), "p50_dn": (e_dol + a_mn) / 2, "p25_dn": (e_dol + (a_mn - e_dol)*0.25)
    }

# --- UI ---
tz_sp = pytz.timezone('America/Sao_Paulo')
st.markdown(f"""<div class="header-bair"><div><span class="bair-text">BAIR</span> - <span class="terminal-text">TERMINAL DOLAR</span></div><div class="clock-container"><div class="clock-box">BRASÍLIA<span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M')}</span></div><div class="clock-box">NEW YORK<span class="clock-time">{datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M')}</span></div><div class="clock-box">LONDRES<span class="clock-time">{datetime.now(pytz.timezone('Europe/London')).strftime('%H:%M')}</span></div></div></div>""", unsafe_allow_html=True)

if ewz_ref_data:
    res = calcular_k97(e_ewz, ewz_ref_data['at'], mx_ref, mn_ref, e_dol)
    st.columns([3, 1])[0].markdown('<div class="monitor-bar">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
    st.columns([3, 1])[1].markdown('<div class="monitor-bar">CÁLCULOS DE PROJEÇÕES</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c1:
        # Tabela com filtro operacional em todos os ativos
        html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
        v_var = ((res['vivo'] / e_dol) - 1) * 100
        v_cor = "#00ff00" if v_var >= 0 else "#ff0000"
        html += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col'>{(res['vivo']/1000):.4f}</td><td>{(e_dol/1000):.4f}</td><td>{(e_dol/1000):.4f}</td><td>{(res['max']/1000):.4f}</td><td>{(res['min']/1000):.4f}</td><td style='color:{v_cor}; font-weight:bold;'>{v_var:+.2f}%</td></tr>"
        
        cfg = {"SPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GOLD": "GC=F", "BRENT": "BZ=F"}
        t_items = [f"<span style='color:#fff;'>DOLFUT:</span> <span style='color:{v_cor};'>{v_var:+.2f}%</span>"]
        for l, s in cfg.items():
            d = fetch_operacional(s)
            if d:
                f = ".3f" if l == "GOLD" else (".4f" if l == "SPOT" else ".2f")
                v = ((d['at']/d['cl'])-1)*100
                c = "#00ff00" if v >= 0 else "#ff0000"
                html += f"<tr><td class='asset-name'>{l}</td><td class='price-col'>{d['at']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{c}; font-weight:bold;'>{v:+.2f}%</td></tr>"
                t_items.append(f"<span style='color:#fff;'>{l}:</span> <span style='color:{c};'>{v:+.2f}%</span>")
        st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="calc-panel"><div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div><div class="calc-row" style="color:#ff7675;"><span>75% UP</span> <span>{res['p75_up']:.2f}</span></div><div class="calc-row" style="color:#fab1a0;"><span>50% UP</span> <span>{res['p50_up']:.2f}</span></div><div class="calc-row" style="color:#ffeaa7;"><span>25% UP</span> <span>{res['p25_up']:.2f}</span></div><div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 16px;">EIXO: {e_dol:.2f}</div><div class="calc-row" style="color:#ffeaa7;"><span>25% DN</span> <span>{res['p25_dn']:.2f}</span></div><div class="calc-row" style="color:#81ecec;"><span>50% DN</span> <span>{res['p50_dn']:.2f}</span></div><div class="calc-row" style="color:#55efc4;"><span>75% DN</span> <span>{res['p75_dn']:.2f}</span></div><div class="calc-row" style="color:#00ff88;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="calc-panel" style="border-color: #d4a017;"><div class="calc-row" style="color:#00f2ff;"><span>MÉDIA DOLFUT</span> <span>{res['medio']:.2f}</span></div><div class="calc-row" style="color:{("#00ff00" if res['v_med'] >= 0 else "#ff0000")}; font-size:12px;"><span>VAR MÉDIA</span> <span>{res['v_med']:+.2f}%</span></div><div class="calc-row" style="color:#d4a017; border-bottom: none;"><span>PREÇO JUSTO</span> <span>{res['fraja']:.2f}</span></div></div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(t_items)} • {" • ".join(t_items)}</div></div>', unsafe_allow_html=True)

time.sleep(2)
st.rerun()
