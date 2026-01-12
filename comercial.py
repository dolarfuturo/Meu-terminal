import streamlit as st
from streamlit_gsheets import GSheetsConnection
import yfinance as yf
import time
from datetime import datetime, date
import pytz

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. CONEXÃO COM A BASE DE DADOS (GOOGLE SHEETS)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_clientes = conn.read(ttl="1m")
except:
    st.error("ERRO DE CONEXÃO COM BASE DE DADOS")
    st.stop()

# 3. ESTADO GLOBAL
@st.cache_resource
def get_global_vars():
    # Iniciamos com valores padrão estáveis
    return {"ajuste": 5.4000, "ref": 5.4000, "notas": "AGUARDANDO NOTAS DO ADM..."}
v_global = get_global_vars()

# 4. SISTEMA DE LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_info = None

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'] {display:none;}</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:120px;'></div>", unsafe_allow_html=True)
        u_in = st.text_input("USUÁRIO").strip()
        p_in = st.text_input("SENHA", type="password").strip()
        if st.button("ACESSAR TERMINAL"):
            user_db = df_clientes[df_clientes['usuario'] == u_in]
            if not user_db.empty:
                validade_str = str(user_db.iloc[0]['validade']).split(' ')[0]
                validade = datetime.strptime(validade_str, '%Y-%m-%d').date()
                if p_in == str(user_db.iloc[0]['senha']) and str(user_db.iloc[0]['status']) == "ATIVO" and date.today() <= validade:
                    st.session_state.auth = True
                    st.session_state.user_info = {"tipo": str(user_db.iloc[0]['tipo']), "nome": u_in}
                    st.rerun()
                else: st.error("ACESSO NEGADO OU EXPIRADO")
            else: st.error("USUÁRIO NÃO ENCONTRADO")
    st.stop()

# 5. CSS DO TERMINAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .t-header { text-align: center; padding: 20px 0 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .t-title { color: #555; font-size: 13px; letter-spacing: 4px; }
    .t-bold { color: #fff; font-weight: 900; }
    .s-container { text-align: center; padding: 10px 0; margin-bottom: 5px; }
    .s-text { font-size: 12px; font-weight: 700; letter-spacing: 2px; }
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 22px 15px; border-bottom: 1px solid #111; }
    .d-label { font-size: 11px; color: #FFFFFF; font-weight: 900; width: 40%; }
    .sub-grid { display: flex; gap: 15px; justify-content: flex-end; width: 60%; }
    .sub-item { text-align: center; min-width: 70px; }
    .sub-l { font-size: 8px; color: #888; display: block; margin-bottom: 2px; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    .d-value { font-size: 26px; text-align: right; font-family: 'Chakra Petch'; font-weight: 700; }
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    .f-bar { position: fixed; bottom: 0; left: 0; width: 100%; height: 140px; background: #050505; border-top: 1px solid #222; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; }
    .f-notes { font-family: 'Chakra Petch'; font-size: 11px; color: #ffff99; margin-bottom: 8px; text-transform: uppercase; text-align: center; }
    .f-arrows { font-size: 16px; margin: 5px 0; letter-spacing: 8px; }
    .f-line { width: 85%; height: 1px; background: rgba(255,255,255,0.1); }
    .tk-wrap { width: 100%; overflow: hidden; white-space: nowrap; display: flex; margin-top: 8px; }
    .tk-move { display: inline-block; animation: slide 40s linear infinite; }
    .tk-item { padding-right: 50px; display: inline-block; font-family: 'Chakra Petch'; font-size: 13px; color: #fff; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# 6. MOTOR DE DADOS ANTI-DISTORÇÃO
def get_market():
    try:
        br_tz = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(br_tz)
        hora = agora.hour
        d = {}
        
        # 1. MOEDAS (Forex é mais estável)
        for t in ["BRL=X", "EURUSD=X"]:
            inf = yf.Ticker(t).fast_info
            d[t] = {"p": inf['last_price'], "v": ((inf['last_price'] - inf['previous_close']) / inf['previous_close']) * 100}
        
        # 2. ÍNDICES (Lógica para evitar distorção de Pre-Market)
        for t in ["DX-Y.NYB", "EWZ"]:
            tick = yf.Ticker(t)
            # Pegamos o 'info' para ter acesso ao Bid/Ask e Pre-Market real
            inf = tick.info
            prev_c = inf.get('regularMarketPreviousClose') or inf.get('previousClose')
            
            # Se estamos antes da abertura oficial de NY (11:30h)
            if 8 <= hora < 11.5:
                # Prioridade para o BID (Oferta real) em vez do último negócio (que pode ser 1 cota)
                cp = inf.get('bid') or inf.get('preMarketPrice') or inf.get('regularMarketPrice')
            else:
                cp = inf.get('regularMarketPrice') or inf.get('lastPrice')
            
            # Validação: se o preço vier zerado ou absurdo, usamos o fast_info
            if not cp or cp <= 0:
                cp = tick.fast_info['last_price']
                
            var_pct = ((cp - prev_c) / prev_c) * 100 if cp and prev_c else 0.0
            d[t] = {"p": cp, "v": var_pct}
            
        # Spread = Variação DXY - Variação EWZ
        spr_val = d["DX-Y.NYB"]["v"] - d["EWZ"]["v"]
        return d, spr_val
    except Exception as e:
        return None, 0.0

# 7. LOOP PRINCIPAL
ui_area = st.empty()
while True:
    m_data, spr = get_market()
    if m_data:
        spot = m_data["BRL=X"]["p"]
        # FÓRMULA DE JUSTO RECALIBRADA
        justo = round((spot + 0.0310) * 2000) / 2000
        
        # Paridade Global (Usa o Ajuste do ADM + Spread do Mercado)
        # Sincronizamos para que o spread não distorça o preço justo de forma irrealista
        paridade_global = v_global["ajuste"] * (1 + (spr/100))
        
        diff = spot - justo
        if diff < -0.0015: msg, clr, arr = "● DOLAR BARATO", "#00aa55", "▲ ▲ ▲ ▲ ▲"
        elif diff > 0.0015: msg, clr, arr = "● DOLAR CARO", "#aa3333", "▼ ▼ ▼ ▼ ▼"
        else: msg, clr, arr = "● DOLAR NEUTRO", "#aaaa00", "◄ ◄ ◄ ► ► ►"
            
        with ui_area.container():
            if st.session_state.user_info["tipo"] == "ADM":
                with st.expander("PAINEL ADM"):
                    with st.form("adm_form"):
                        # Usamos colunas para facilitar a edição no telemóvel
                        c1, c2 = st.columns(2)
                        v_global["ajuste"] = c1.number_input("PARIDADE (AJUSTE)", value=v_global["ajuste"], format="%.4f", step=0.0001)
                        v_global["ref"] = c2.number_input("REF INST", value=v_global["ref"], format="%.4f", step=0.0001)
                        v_global["notas"] = st.text_input("MURAL DE NOTAS", value=v_global["notas"])
                        if st.form_submit_button("SALVAR"): st.rerun()

            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="s-container" style="border-bottom: 2px solid {clr}77"><div class="s-text" style="color:{clr}">{msg}</div></div>', unsafe_allow_html=True)
            
            # EXIBIÇÃO DOS VALORES CALCULADOS
            st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{paridade_global:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value c-equi">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((spot+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{justo:.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((spot+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="d-row" style="border-bottom:none;"><div class="d-label">REF. INSTITUCIONAL</div><div class="sub-grid"><div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{(round((v_global["ref"]+0.0220)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{(round((v_global["ref"]+0.0310)*2000)/2000):.4f}</span></div><div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{(round((v_global["ref"]+0.0420)*2000)/2000):.4f}</span></div></div></div>', unsafe_allow_html=True)

            # TICKER RODAPÉ
            def f_tk(t, n):
                try:
                    v = m_data[t]['v']
                    p_f = f"{m_data[t]['p']:.4f}" if n == "SPOT" else f"{m_data[t]['p']:.2f}"
                    c = '#00aa55' if v >= 0 else '#aa3333'
                    return f"<span class='tk-item'><b>{n}</b> {p_f} <span style='color:{c}'>({v:+.2f}%)</span></span>"
                except: return ""

            btk = f"{f_tk('BRL=X','SPOT')} {f_tk('DX-Y.NYB','DXY')} {f_tk('EWZ','EWZ')} {f_tk('EURUSD=X','EURUSD')} <span class='tk-item'><b>SPREAD</b> {spr:+.2f}%</span>"
            st.markdown(f'<div class="f-bar"><div class="f-notes">{v_global["notas"]}</div><div class="f-line"></div><div class="f-arrows" style="color:{clr}">{arr}</div><div class="f-line"></div><div class="tk-wrap"><div class="tk-move">{btk*3}</div></div></div>', unsafe_allow_html=True)
    time.sleep(2)
