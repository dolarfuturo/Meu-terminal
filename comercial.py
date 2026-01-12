import streamlit as st
import yfinance as yf
import time

# 1. SETUP
st.set_page_config(page_title="TERMINAL PRO", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def vars_terminal():
    return {
        "pari_ref": 5.4000, 
        "inst_ref": 5.4000,
        "mural_txt": "AGUARDANDO ATUALIZAÇÃO...",
        "rodape_1": "MURAL ATIVO",
        "rodape_2": "SISTEMA OPERACIONAL"
    }

v = vars_terminal()

# 2. LOGIN (SIMPLIFICADO PARA TESTE)
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
        pwd = st.text_input("CHAVE", type="password")
        if st.button("ACESSAR"):
            if pwd in ["admin123", "trader123"]:
                st.session_state.logado = True
                st.rerun()
    st.stop()

# 3. CSS (FORÇANDO O NOVO LAYOUT)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;700&family=Orbitron:wght@400;900&display=swap');
    [data-testid="stHeader"], .stAppDeployButton, footer, label { display: none !important; }
    .stApp { background-color: #000; color: #fff; font-family: 'Orbitron', sans-serif; }
    .block-container { padding: 0rem !important; }
    
    .header-top { text-align: center; padding: 20px 0; border-bottom: 1px solid #222; }
    .header-bold { color: #fff; font-weight: 900; letter-spacing: 3px; }
    
    .box-sinal { text-align: center; padding: 12px 0; margin-bottom: 5px; border-bottom: 2px solid #333; }
    .txt-sinal { font-size: 14px; font-weight: 900; letter-spacing: 2px; }
    
    .linha-dado { display: flex; justify-content: space-between; align-items: center; padding: 18px 15px; border-bottom: 1px solid #111; }
    .label-dado { font-size: 11px; color: #FFFFFF; font-weight: 900; }
    .valor-dado { font-size: 26px; font-family: 'Chakra Petch'; font-weight: 700; }
    
    .grid-correcao { display: flex; gap: 15px; justify-content: flex-end; }
    .item-v { font-size: 16px; font-family: 'Chakra Petch'; font-weight: 700; color: #ffff00; }
    
    .alerta-micro { text-align: right; padding-right: 15px; font-size: 10px; font-family: 'Chakra Petch'; font-weight: 700; margin-top: -5px; margin-bottom: 15px; }
    
    .mural-box { background: #050505; border-top: 1px solid #111; padding: 20px; min-height: 100px; }
    .mural-content { font-family: 'Chakra Petch'; font-size: 13px; color: #999; }
    
    .footer-terminal { position: fixed; bottom: 0; left: 0; width: 100%; height: 140px; background: #050505; border-top: 1px solid #222; text-align: center; z-index: 100; }
</style>
""", unsafe_allow_html=True)

def get_data(ticker):
    try:
        d = yf.download(ticker, period="1d", interval="1m", progress=False)
        l = float(d['Close'].iloc[-1])
        p = float(yf.Ticker(ticker).fast_info.previous_close)
        return {"last": l, "var": ((l-p)/p*100)}
    except: return {"last": 0.0, "var": 0.0}

ui = st.empty()
while True:
    dxy = get_data("DX-Y.NYB")
    ewz = get_data("EWZ")
    dol = get_data("BRL=X")
    
    if dol["last"] > 0:
        preco_atual = dol["last"]
        spread_global = dxy["var"] - ewz["var"]
        
        # CÁLCULOS NOVOS
        val_paridade = v["pari_ref"] * (1 + (spread_global/100))
        val_equilibrio = round((v["inst_ref"] + 0.0220) * 2000) / 2000
        
        # 1. TENDÊNCIA MACRO (PRECIFICAÇÃO)
        if preco_atual < (val_paridade - 0.0015): 
            txt_m, cor_m = "● PRECIFICAÇÃO DE ALTA", "#00ff00"
        elif preco_atual > (val_paridade + 0.0015): 
            txt_m, cor_m = "● PRECIFICAÇÃO DE BAIXA", "#ff3333"
        else: 
            txt_m, cor_m = "● PRECIFICAÇÃO NEUTRA", "#ffff00"
            
        # 2. SINAL MICRO (PONTOS)
        pts_diff = (preco_atual - val_equilibrio) * 1000
        if pts_diff >= 22: mic_t, mic_c = "MICRO: MUITO CARO (+22)", "#ff0000"
        elif pts_diff >= 11: mic_t, mic_c = "MICRO: CARO (+11)", "#ff6600"
        elif pts_diff <= -22: mic_t, mic_c = "MICRO: MUITO BARATO (-22)", "#00ff00"
        elif pts_diff <= -11: mic_t, mic_c = "MICRO: BARATO (-11)", "#00cc66"
        else: mic_t, mic_c = "MICRO: ESTÁVEL", "#666666"

        with ui.container():
            # HEADER
            st.markdown(f'<div class="header-top"><div class="header-bold">TERMINAL DOLAR PRO</div></div>', unsafe_allow_html=True)
            
            # TENDÊNCIA MACRO
            st.markdown(f'<div class="box-sinal" style="border-color:{cor_m}77"><div class="txt-sinal" style="color:{cor_m}">{txt_m}</div></div>', unsafe_allow_html=True)
            
            # DADOS
            st.markdown(f'<div class="linha-dado"><div class="label-dado">PARIDADE GLOBAL</div><div class="valor-dado" style="color:#cc9900">{val_paridade:.4f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="linha-dado"><div class="label-dado">PREÇO EQUILÍBRIO</div><div class="valor-dado" style="color:#00cccc">{val_equilibrio:.4f}</div></div>', unsafe_allow_html=True)

            # REGIÃO DE CORREÇÃO (SÓ NÚMEROS)
            st.markdown(f"""
            <div class="linha-dado" style="border-bottom:none; padding-bottom:5px;">
                <div class="label-dado" style="opacity:0.6;">REGIÃO DE CORREÇÃO</div>
                <div class="grid-correcao">
                    <div class="item-v">{(val_equilibrio - 0.0220):.4f}</div>
                    <div class="item-v">{(val_equilibrio - 0.0110):.4f}</div>
                    <div class="item-v">{(val_equilibrio + 0.0110):.4f}</div>
                    <div class="item-v">{(val_equilibrio + 0.0220):.4f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ALERTA MICRO DISCRETO
            st.markdown(f'<div class="alerta-micro" style="color:{mic_c}">{mic_t}</div>', unsafe_allow_html=True)

            # MURAL
            st.markdown(f'<div class="mural-box"><div style="font-size:9px; color:#444; margin-bottom:8px;">MORNING CALL & AGENDA</div><div class="mural-content">{v["mural_txt"].replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)

            # RODAPÉ
            st.markdown(f'<div class="footer-terminal"><br><div style="color:#ffff99; font-size:11px;">{v["rodape_1"]}</div><div style="color:#555; font-size:10px;">{v["rodape_2"]}</div></div>', unsafe_allow_html=True)
            
    time.sleep(2)
