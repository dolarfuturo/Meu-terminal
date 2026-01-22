import streamlit as st
import yfinance as yf
import time

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="TERMINAL FINANCEIRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO GLOBAL (Multiplicadores de Variação)
@st.cache_resource
def get_global_vars():
    return {
        "ajuste": 5.4000, 
        "ref": 5.4000,
        "v_min": 1.0020,   
        "v_jus": 1.0041,   
        "v_max": 1.0100,   
        "notas_mural": "AGUARDANDO ATUALIZAÇÃO...",
        "notas": "MURAL: AGUARDANDO...",
        "notas2": "INFORMATIVO: OPERACIONAL ATIVO"
    }

v_global = get_global_vars()

# 3. CONTROLE DE ACESSO
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_type = None

if not st.session_state.auth:
    st.markdown("<style>.stApp { background-color: #000; } [data-testid='stHeader'], label { display: none !important; } .stButton button { width: 100%; background-color: #222; color: white; border: 1px solid #444; margin-top: 20px; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='height:150px;'></div>", unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="CHAVE DE ACESSO")
        if st.button("ENTRAR"):
            if senha == "admin123":
                st.session_state.auth = True
                st.session_state.user_type = "ADM"
                st.rerun()
            elif senha == "trader123":
                st.session_state.auth = True
                st.session_state.user_type = "USER"
                st.rerun()
    st.stop()

# 4. CSS DO TERMINAL (Ajustado para evitar tela preta por sobreposição)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, [data-testid="stToolbar"], footer, [data-testid="stSidebar"], label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    
    .t-header { text-align: center; padding: 15px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .t-title { color: #555; font-size: 12px; letter-spacing: 3px; }
    .t-bold { color: #fff; font-weight: 900; }
    
    .s-container { text-align: center; padding: 10px 0; }
    .s-text { font-size: 34px; font-weight: 700; font-family: 'Chakra Petch'; color: #ffffff; }
    .var-style { font-size: 18px; margin-left: 10px; }
    
    .d-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; border-bottom: 1px solid #111; min-height: 70px; }
    .d-label { font-size: 10px; color: #eee; font-weight: 900; letter-spacing: 1px; }
    .d-value { font-size: 24px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .sub-grid { display: flex; gap: 20px; }
    .sub-item { text-align: center; display: flex; flex-direction: column; }
    .sub-l { font-size: 8px; color: #666; margin-bottom: 2px; text-transform: uppercase; }
    .sub-v { font-size: 18px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .c-pari { color: #cc9900; } .c-equi { color: #00cccc; } 
    .c-max { color: #00cc66; } .c-min { color: #cc3333; } .c-jus { color: #0066cc; }
    .v-peq { color: #ffff00; font-size: 16px; font-weight: 700; font-family: 'Chakra Petch'; }
    .v-extra { color: #ffff00; opacity: 0.4; font-size: 11px; font-family: 'Chakra Petch'; }

    .f-bar { position: fixed; bottom: 0; width: 100%; background: #050505; border-top: 1px solid #222; padding: 10px 0; z-index: 100; }
    .tk-wrap { overflow: hidden; white-space: nowrap; width: 100%; margin-top: 5px; }
    .tk-move { display: inline-block; animation: slide 30s linear infinite; }
    .tk-item { padding-right: 40px; font-size: 12px; font-family: 'Chakra Petch'; }
    @keyframes slide { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

def get_clean_data(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        last, prev = info.last_price, info.previous_close
        var = ((last - prev) / prev * 100) if prev != 0 else 0
        return {"last": last, "var": var}
    except:
        return {"last": 0.0, "var": 0.0}

# 6. RENDERIZAÇÃO PRINCIPAL (Sem fragmento para testar estabilidade)
d_m = get_clean_data("DX-Y.NYB")
e_m = get_clean_data("EWZ")
s_m = get_clean_data("BRL=X")

if s_m["last"] > 0:
    spot, v_spot = s_m["last"], s_m["var"]
    cor_v = "#00cc66" if v_spot >= 0 else "#cc3333"
    spr = d_m["var"] - e_m["var"]
    paridade = v_global["ajuste"] * (1 + (spr/100))
    
    # Cálculos de Referência
    ref_min = round((v_global["ref"] * v_global["v_min"]) * 2000) / 2000
    ref_jus = round((v_global["ref"] * v_global["v_jus"]) * 2000) / 2000
    ref_max = round((v_global["ref"] * v_global["v_max"]) * 2000) / 2000
    
    # Preço Justo sobre o SPOT
    justo_atual = round((spot * v_global["v_jus"]) * 2000) / 2000

    # Header e Spot
    st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="s-container"><div class="s-text">{spot:.4f} <span class="var-style" style="color:{cor_v}">{v_spot:+.2f}%</span></div></div>', unsafe_allow_html=True)

    # Linhas de Dados
    st.markdown(f'<div class="d-row"><div class="d-label">PARIDADE GLOBAL</div><div class="d-value c-pari">{paridade:.4f}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="d-row"><div class="d-label">EQUILÍBRIO</div><div class="d-value c-equi">{ref_min:.4f}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="d-row"><div class="d-label">PREÇO JUSTO (SPOT)</div><div class="d-value c-jus">{justo_atual:.4f}</div></div>', unsafe_allow_html=True)

    # REF Institucional
    st.markdown(f"""
    <div class="d-row">
        <div class="d-label">REF. INSTITUCIONAL</div>
        <div class="sub-grid">
            <div class="sub-item"><span class="sub-l">MIN</span><span class="sub-v c-min">{ref_min:.4f}</span></div>
            <div class="sub-item"><span class="sub-l">JUSTO</span><span class="sub-v c-jus">{ref_jus:.4f}</span></div>
            <div class="sub-item"><span class="sub-l">MAX</span><span class="sub-v c-max">{ref_max:.4f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Regiões de Correção
    st.markdown(f"""
    <div class="d-row" style="border-bottom:none;">
        <div class="d-label" style="opacity:0.5;">REGIÃO DE CORREÇÃO</div>
        <div class="sub-grid">
            <div class="sub-item"><span class="v-peq">{(ref_min * 0.9980):.4f}</span><span class="v-extra">{(ref_min * 0.9960):.4f}</span></div>
            <div class="sub-item"><span class="v-peq">{(ref_min * 1.0020):.4f}</span><span class="v-extra">{(ref_min * 1.0040):.4f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mural de Notas
    st.markdown(f'<div style="padding:20px; color:#666; font-size:12px; border-top:1px solid #111;">{v_global["notas_mural"]}</div>', unsafe_allow_html=True)

    # Rodapé Ticker
    tk_cnt = f"SPOT {spot:.4f} | DXY {d_m['last']:.2f} ({d_m['var']:+.2f}%) | EWZ {e_m['last']:.2f} ({e_m['var']:+.2f}%) | SPREAD {spr:+.2f}%"
    st.markdown(f'<div class="f-bar"><div class="tk-wrap"><div class="tk-move">{tk_cnt} &nbsp;&nbsp;&nbsp; {tk_cnt}</div></div></div>', unsafe_allow_html=True)

# PAINEL ADM
if st.session_state.user_type == "ADM":
    with st.expander("⚙️ CONFIGURAÇÕES"):
        with st.form("adm"):
            v_global["ajuste"] = st.number_input("Paridade", value=v_global["ajuste"], format="%.4f")
            v_global["ref"] = st.number_input("Ref Institucional", value=v_global["ref"], format="%.4f")
            v_global["v_min"] = st.number_input("Variação Min (Ex: 1.002)", value=v_global["v_min"], format="%.4f")
            v_global["v_jus"] = st.number_input("Variação Justo (Ex: 1.004)", value=v_global["v_jus"], format="%.4f")
            v_global["v_max"] = st.number_input("Variação Max (Ex: 1.01)", value=v_global["v_max"], format="%.4f")
            v_global["notas_mural"] = st.text_area("Notas Mural", value=v_global["notas_mural"])
            if st.form_submit_button("ATUALIZAR"): st.rerun()

time.sleep(1)
st.rerun()
