import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime
import pytz

# =============================================================================
# # BLOCO 1: CONFIGURAÇÃO DE AMBIENTE E ESTILIZAÇÃO VISUAL (CSS)
# =============================================================================
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container { padding-top: 3.5rem !important; padding-bottom: 0rem !important; max-width: 98% !important; }
    .stApp { background-color: #050a0e !important; }
    [data-testid="column"] { display: flex; flex-direction: column; justify-content: flex-start; gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { gap: 12px !important; margin-bottom: 0px !important; }
    .header-container { text-align: center; padding: 10px 0px; border-bottom: 2px solid #FFD700; background-color: #050a0e; margin-bottom: 8px; position: relative; }
    .main-title { margin: 0px; line-height: 1.2; font-size: 28px; font-family: monospace; padding-bottom: 5px; }
    .bair-blue { color: #00BFFF; font-weight: bold; }
    .terminal-gold { color: #FFD700; font-weight: bold; }
    .clock-row { display: flex; justify-content: center; gap: 15px; padding: 2px 0; font-weight: bold; font-size: 11px; font-family: monospace; }
    .clock-item { color: #AAA; }
    .br-green { color: #00ff00; }
    .white-time { color: #ffffff; }
    .utc-gold { color: #FFD700; }
    .date-container { position: absolute; bottom: 5px; right: 10px; font-family: monospace; font-size: 11px; font-weight: bold; color: #ffffff; }
    .section-title { border: 1px solid #ffffff; color: #00f2ff; text-align: center; font-weight: bold; font-family: monospace; padding: 2px; margin-bottom: 5px; text-transform: uppercase; font-size: 11px; }
    .main-grid { border: 1.5px solid #ffffff; border-radius: 4px; overflow: hidden; font-family: 'monospace'; background-color: #0d1b22; margin-bottom: 0px; }
    .terminal-table { width: 100%; border-collapse: collapse; color: #e0e0e0; }
    .terminal-table th { background-color: #0a141a; color: #d4a017; border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 10px; text-transform: uppercase; }
    .terminal-table td { border: 1px solid #ffffff; padding: 4px; text-align: center; font-size: 12px; }
    .asset-name { font-size: 12px; color: #fff; text-align: left; font-weight: bold; padding-left: 8px; }
    .price-col { font-weight: bold; color: #ffffff !important; }
    .f-up { background-color: #00ff00aa !important; }
    .f-dn { background-color: #ff0000aa !important; }
    .calc-panel { border: 1.5px solid #ffffff; border-radius: 4px; padding: 4px; background: #0a141a; font-family: monospace; margin-bottom: 4px; margin-top: 8px; }
    .calc-row { display: flex; justify-content: space-between; padding: 2px 6px; border-bottom: 1px solid #444; font-size: 10px; font-weight: bold; align-items: center; }
    
    /* Customizações da Barra de Força */
    .bar-wrapper-full { background: #0a141a; padding: 6px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; margin-top: 5px; font-family: monospace; }
    .force-scale-top { display: flex; justify-content: space-between; font-size: 9px; font-weight: bold; color: #ffffff; margin-bottom: 2px; padding: 0 2px; }
    .force-scale-bottom { display: flex; justify-content: space-between; font-size: 9px; font-weight: bold; color: #00BFFF; margin-top: 2px; padding: 0 2px; }
    .force-container-dual { background: #111; height: 16px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #ffffff; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; display: flex; align-items: center; justify-content: flex-start; padding-left: 5px; font-size: 10px; font-weight: bold; white-space: nowrap; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; display: flex; align-items: center; justify-content: flex-end; padding-right: 5px; font-size: 10px; font-weight: bold; white-space: nowrap; }
    .txt-interno-tom-vermelho { color: #ff4d4d !important; } 
    .txt-interno-tom-verde { color: #00ff88 !important; }
    .sinal-indicator { font-size: 18px; font-weight: bold; line-height: 1; margin-top: 4px; }
    
    /* Novo Termômetro Segmentado */
    .therm-container { display: flex; width: 100%; height: 40px; margin-top: 5px; border: 1px solid #ffffff; background: #000; }
    .therm-seg { flex: 1; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold; background: #1a1a1a; color: #555; border-right: 1px solid #333; transition: all 0.2s; text-align: center; }
    .active-bf { background: #8B0000 !important; color: #fff !important; box-shadow: 0 0 15px #FF0000; border: 1px solid #ff4d4d; z-index: 1; }
    .active-b { background: #CC4D00 !important; color: #fff !important; box-shadow: 0 0 15px #FF8C00; border: 1px solid #ff8c00; z-index: 1; }
    .active-n { background: #404040 !important; color: #fff !important; box-shadow: 0 0 15px #ffffff; border: 1px solid #fff; z-index: 1; }
    .active-a { background: #006600 !important; color: #fff !important; box-shadow: 0 0 15px #00FF00; border: 1px solid #00ff88; z-index: 1; }
    .active-af { background: #004d00 !important; color: #fff !important; box-shadow: 0 0 15px #008000; border: 1px solid #00ff00; z-index: 1; }
    
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .txt-green { color: #00ff88 !important; }
    .txt-yellow { color: #ffff00 !important; }
    .txt-red { color: #ff4d4d !important; }
    .txt-cyan { color: #00f2ff !important; }
    .txt-white { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# # BLOCO 2: MEMÓRIA DA SESSÃO E PERSISTÊNCIA DE DADOS (ARQUIVOS)
# =============================================================================
def salvar_eixos(div_spreed, max_madr=0.0, min_madr=0.0):
    with open("config_axis.txt", "w") as f:
        f.write(f"{div_spreed},{max_madr},{min_madr}")

def carregar_eixos():
    if os.path.exists("config_axis.txt"):
        try:
            with open("config_axis.txt", "r") as f:
                parts = f.read().split(",")
                return float(parts[0]), float(parts[1]) if len(parts) > 1 else 0.0, float(parts[2]) if len(parts) > 2 else 0.0
        except: pass
    return 8.0, 0.0, 0.0

def carregar_historico_dolfut_diario():
    data_hoje = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
    if os.path.exists("dolfut_history.txt"):
        try:
            with open("dolfut_history.txt", "r") as f:
                conteudo = f.read().split(",")
                if conteudo[0] == data_hoje:
                    return float(conteudo[1]), float(conteudo[2])
        except: pass
    return float('-inf'), float('inf')

def salvar_historico_dolfut_diario(mx, mn):
    data_hoje = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d")
    try:
        with open("dolfut_history.txt", "w") as f:
            f.write(f"{data_hoje},{mx},{mn}")
    except: pass

div_spreed_salvo, max_madr_salvo, min_madr_salvo = carregar_eixos()

if 'market_data' not in st.session_state: st.session_state.market_data = {}
if 'last_p' not in st.session_state: st.session_state.last_p = {}
if 'div_spreed_mem' not in st.session_state: st.session_state.div_spreed_mem = div_spreed_salvo
if 'max_madr_mem' not in st.session_state: st.session_state.max_madr_mem = max_madr_salvo
if 'min_madr_mem' not in st.session_state: st.session_state.min_madr_mem = min_madr_salvo

max_init, min_init = carregar_historico_dolfut_diario()
if 'dolfut_max_auto' not in st.session_state: st.session_state.dolfut_max_auto = max_init
if 'dolfut_min_auto' not in st.session_state: st.session_state.dolfut_min_auto = min_init

if 'last_spot_max' not in st.session_state: st.session_state.last_spot_max = 0.0
if 'last_spot_min' not in st.session_state: st.session_state.last_spot_min = float('inf')

if 'c_spot_fech_val' not in st.session_state: st.session_state.c_spot_fech_val = 0.0
if 'c_du_val' not in st.session_state: st.session_state.c_du_val = 22
if 't_br_val' not in st.session_state: st.session_state.t_br_val = 14.25
if 't_us_val' not in st.session_state: st.session_state.t_us_val = 3.75

# =============================================================================
# # BLOCO 3: CONEXÃO COM API E MOTOR DE CAPTURA DE DADOS
# =============================================================================
def fetch(s):
    fallback = {"at": 0.0, "cl": 1.0, "op": 0.0, "mx": 0.0, "mn": 0.0}
    try:
        t = yf.Ticker(s)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        if s == "^TNX":
            info = t.fast_info
            d = t.history(period="1d", interval="1m")
            if d.empty: return st.session_state.market_data.get(s, fallback)
            data = {"at": float(info.last_price), "cl": float(info.previous_close if info.previous_close else d['Open'].iloc[0]), "op": float(d['Open'].iloc[0]), "mx": float(d['High'].max()), "mn": float(d['Low'].min())}
        else:
            d = t.history(period="1d", interval="1m", prepost=True)
            if d.empty: return st.session_state.market_data.get(s, fallback)
            ref_close = t.info.get('previousClose')
            if not ref_close: ref_close = d['Open'].iloc[0]
            if s == "EWZ":
                d_hist = t.history(period="3d", interval="1m", prepost=True)
                if not d_hist.empty:
                    d_hist.index = d_hist.index.tz_convert(tz_sp)
                    unique_dates = sorted(list(set(d_hist.index.date)))
                    data_anterior = unique_dates[-2] if len(unique_dates) > 1 else unique_dates[0]
                    f_21h = d_hist.between_time('05:00', '21:00').loc[d_hist.index.date == data_anterior]
                    if not f_21h.empty: ref_close = f_21h['Close'].iloc[-1]
            m = 1000 if s == "USDBRL=X" else 1
            data = {"at": float(d['Close'].iloc[-1] * m), "cl": float(ref_close * m), "op": float(d['Open'].iloc[0] * m), "mx": float(d['High'].max() * m), "mn": float(d['Low'].min() * m)}
        st.session_state.market_data[s] = data
        return data
    except: return st.session_state.market_data.get(s, fallback)

# =============================================================================
# # BLOCO 4: NÚCLEO MATEMÁTICO CENTRAL E CÁLCULOS DO K97
# =============================================================================
def calcular_k97_total(spreed_do_dia, spot_data, ewz_data):
    try:
        if not spot_data or not ewz_data: return None
        
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        spreed_t = spot_data['mx'] - spot_data['mn']
        spreed_50 = spreed_t / 2
        
        fraja_val = spot_data['at'] + spreed_do_dia
        
        dxy_data = fetch("DX-Y.NYB")
        v_dxy = ((dxy_data['at'] / dxy_data['cl']) - 1) if dxy_data['cl'] > 0 else 0
        ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
        # Manter a lógica original de cálculo aqui
        v_ewz = ((ewz_data['at'] / ewz_ref) - 1) if ewz_ref > 0 else 0
        
        calc_variacoes_pct = (v_dxy) - (v_ewz)
        
        vivo_val = spot_data['cl'] * (1 + calc_variacoes_pct) 
        axis_dinamico = dolar_medio + spreed_do_dia
        passo_fixo = spreed_50 / 4
        
        alvo_low = spot_data['mn'] + spreed_do_dia
        alvo_high = spot_data['mx'] + spreed_do_dia
        
        mx_adm = st.session_state.max_madr_mem
        mn_adm = st.session_state.min_madr_mem
        bloco_vol = mx_adm - mn_adm if mx_adm > mn_adm else 0.0
        
        gatilho_c = spot_data['mn'] + passo_fixo
        gatilho_v = spot_data['mx'] - passo_fixo
        distancia_base_calc = abs(spot_data['mn'] - gatilho_c)
        
        if spot_data['at'] >= gatilho_v:
            ind_val = spot_data['at'] - gatilho_v
            cor_ind = "#ff4d4d"
        elif spot_data['at'] <= gatilho_c:
            ind_val = spot_data['at'] - gatilho_c
            cor_ind = "#00ff88"
        else:
            ind_val = 0.0
            cor_ind = "#00f2ff"
        
        p_c3_v = (dolar_medio * (1 - 0.0105)) + spreed_do_dia
        p_c2_v = (dolar_medio * (1 - 0.0070)) + spreed_do_dia
        p_c1_v = (dolar_medio * (1 - 0.0035)) + spreed_do_dia
        p_v1_v = (dolar_medio * (1 + 0.0035)) + spreed_do_dia
        p_v2_v = (dolar_medio * (1 + 0.0070)) + spreed_do_dia
        p_v3_v = (dolar_medio * (1 + 0.0105)) + spreed_do_dia
        
        diff_media = spot_data['at'] - dolar_medio
        pct_afastamento = (diff_media / dolar_medio) * 100 if dolar_medio > 0 else 0
        
        if spot_data['at'] >= dolar_medio:
            seta_txt = "▲"
            seta_cor = "#00ff88"
        else:
            seta_txt = "▼"
            seta_cor = "#ff4d4d"
            
        p_v, p_r = 0, 0
        if diff_media < 0:
            p_v = min(100.0, (abs(pct_afastamento) / 1.05) * 100)
        else:
            p_r = min(100.0, (pct_afastamento / 1.05) * 100)
            
        v_spot_pct = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        dolfut_atual_calc = axis_dinamico * (1 + calc_variacoes_pct)
        
        tz_sp = pytz.timezone('America/Sao_Paulo')
        now_br = datetime.now(tz_sp)
        
        f_max, f_min = carregar_historico_dolfut_diario()
        if f_max != float('-inf'): st.session_state.dolfut_max_auto = max(st.session_state.dolfut_max_auto, f_max)
        if f_min != float('inf'): st.session_state.dolfut_min_auto = min(st.session_state.dolfut_min_auto, f_min)
        
        if (now_br.hour > 9 or (now_br.hour == 9 and now_br.minute >= 0)) and (now_br.hour < 18 or (now_br.hour == 18 and now_br.minute <= 30)):
            mudou = False
            if dolfut_atual_calc > st.session_state.dolfut_max_auto:
                st.session_state.dolfut_max_auto = dolfut_atual_calc
                mudou = True
            if dolfut_atual_calc < st.session_state.dolfut_min_auto:
                st.session_state.dolfut_min_auto = dolfut_atual_calc
                mudou = True
            if mudou: salvar_historico_dolfut_diario(st.session_state.dolfut_max_auto, st.session_state.dolfut_min_auto)
        else:
            if st.session_state.dolfut_max_auto == float('-inf') or st.session_state.dolfut_min_auto == float('inf'):
                st.session_state.dolfut_max_auto = dolfut_atual_calc
                st.session_state.dolfut_min_auto = dolfut_atual_calc
                salvar_historico_dolfut_diario(dolfut_atual_calc, dolfut_atual_calc)

        return {
            "white": vivo_val, "vivo_pct": calc_variacoes_pct * 100, "dolfut_calc": dolfut_atual_calc, "fraja": fraja_val, 
            "medio": dolar_medio, "axis_central": axis_dinamico,
            "max_fut_1": axis_dinamico + passo_fixo, "max_fut_1_b": axis_dinamico + (passo_fixo * 2),
            "max_fut_2": axis_dinamico + (passo_fixo * 3), "max_fut_2_b": axis_dinamico + (passo_fixo * 4),
            "min_fut_1": axis_dinamico - passo_fixo, "min_fut_1_b": axis_dinamico - (passo_fixo * 2),
            "min_fut_2": axis_dinamico - (passo_fixo * 3), "min_fut_2_b": axis_dinamico - (passo_fixo * 4),
            "v_v": calc_variacoes_pct * 100, "v_spot": v_spot_pct * 100, "spreed": spreed_50, 
            "p_v": p_v, "p_r": p_r, "seta": seta_txt, "seta_cor": seta_cor, 
            "max_grade": st.session_state.dolfut_max_auto, "min_grade": st.session_state.dolfut_min_auto, 
            "alvo_low": alvo_low, "alvo_high": alvo_high, "spreed_t": spreed_t, "passo_fixo": passo_fixo,
            "gatilho_c": gatilho_c, "gatilho_v": gatilho_v, "ind_val": ind_val, "cor_ind": cor_ind,
            "bloco_vol": bloco_vol, "mx_adm": mx_adm, "mn_adm": mn_adm, "distancia_base_calc": distancia_base_calc,
            "p_c3_v": p_c3_v, "p_c2_v": p_c2_v, "p_c1_v": p_c1_v, "p_v1_v": p_v1_v, "p_v2_v": p_v2_v, "p_v3_v": p_v3_v,
            "pct_afastamento": pct_afastamento
        }
    except: return None

# =============================================================================
# # BLOCO 5: CONTROLES OPERACIONAIS FINANCEIROS (SIDEBAR / ADM)
# =============================================================================
with st.sidebar:
    st.markdown("### 🧮 CALCULADORA DE JUROS (FRP)")
    with st.expander("CALCULAR SPREED", expanded=False):
        c_spot_fech = st.number_input("FECH SPOT:", value=st.session_state.c_spot_fech_val, format="%.3f")
        c_du = st.number_input("DIAS ÚTEIS (DU):", value=st.session_state.c_du_val, step=1)
        t_br = st.number_input("JUROS BRL (%):", value=st.session_state.t_br_val, format="%.2f")
        t_us = st.number_input("JUROS USD (%):", value=st.session_state.t_us_val, format="%.2f")
        
        st.session_state.c_spot_fech_val = c_spot_fech
        st.session_state.c_du_val = c_du
        st.session_state.t_br_val = t_br
        st.session_state.t_us_val = t_us
        
        if c_spot_fech > 0:
            spreed_calc = c_spot_fech * ((t_br / 100) - (t_us / 100)) * (c_du / 252)
            st.markdown(f"""
            <div style="background:#0d1b22; padding:8px; border:1px solid #FFD700; font-family:monospace; text-align:center;">
                <span style="color:#AAA; font-size:10px;">SPREED (REGRA DE BOLSO)</span><br>
                <span style="color:#00ff88; font-size:18px; font-weight:bold;">{spreed_calc:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("USAR ESTE SPREED NO ADM"):
                st.session_state.div_spreed_mem = spreed_calc
                st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ PAINEL ADM")
    i_div = st.number_input("FRP (PARA JUSTO):", value=st.session_state.div_spreed_mem, format="%.2f")
    
    i_max_madr = st.number_input("MAX MADRUGADA:", value=st.session_state.max_madr_mem, format="%.2f")
    i_min_madr = st.number_input("MIN MADRUGADA:", value=st.session_state.min_madr_mem, format="%.2f")
    
    if st.button("SALVAR CONFIGURAÇÕES"):
        st.session_state.div_spreed_mem = i_div
        st.session_state.max_madr_mem = i_max_madr
        st.session_state.min_madr_mem = i_min_madr
        salvar_eixos(i_div, i_max_madr, i_min_madr)
        st.success("Salvo!"); time.sleep(0.5); st.rerun()

div_s = st.session_state.div_spreed_mem
placeholder = st.empty()

# =============================================================================
# # BLOCO 6: INTERFACE DO TERMINAL E ITERAÇÃO DE MERCADO (LOOP 5S)
# =============================================================================
while True:
    tz_sp, tz_ny, tz_ld, tz_utc = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London'), pytz.utc
    spot_live, ewz_live, us10y_live = fetch("USDBRL=X"), fetch("EWZ"), fetch("^TNX")
    now = datetime.now()
    
    with placeholder.container():
        st.markdown(f'''<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1><div class="clock-row"><span class="clock-item">🇧🇷 BR: <span class="br-green">{now.astimezone(tz_sp).strftime("%H:%M:%S")}</span></span><span class="clock-item">🇺🇸 NY: <span class="white-time">{now.astimezone(tz_ny).strftime("%H:%M:%S")}</span></span><span class="clock-item">🇬🇧 LDN: <span class="white-time">{now.astimezone(tz_ld).strftime("%H:%M:%S")}</span></span><span class="clock-item">🌐 UTC: <span class="utc-gold">{now.astimezone(tz_utc).strftime("%H:%M:%S")}</span></span></div><div class="date-container">📅 {now.astimezone(tz_sp).strftime("%d/%m/%Y")}</div></div>''', unsafe_allow_html=True)
        
        res = calcular_k97_total(div_s, spot_live, ewz_live)
        if res:
            c1, c2 = st.columns([2.8, 1.2])
            with c1:
                st.markdown('<div class="section-title">MONITORAMENTO DA GRADE PRINCIPAL</div>', unsafe_allow_html=True)
                html = """<div class="main-grid"><table class="terminal-table"><thead><tr><th>Ativo</th><th>Price</th><th>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr></thead><tbody>"""
                
                v_f, d_c = res['v_v'], res['dolfut_calc']
                l_df = st.session_state.last_p.get('DF', d_c/1000); cl_df = "f-up" if (d_c/1000) > l_df else "f-dn" if (d_c/1000) < l_df else ""; st.session_state.last_p['DF'] = d_c/1000
                html += f"<tr><td class='asset-name'>DOLFUT</td><td class='price-col {cl_df}' style='background-color:rgba({('0,255,0' if v_f >= 0 else '255,0,0')}, 0.1);'>{(d_c/1000):.4f}</td><td>{(res['axis_central']/1000):.4f}</td><td>{(res['axis_central']/1000):.4f}</td><td>{(res['max_grade']/1000):.4f}</td><td>{(res['min_grade']/1000):.4f}</td><td style='color:{("#00ff00" if v_f >= 0 else "#ff4d4d")}; font-weight:bold;'>{v_f:+.2f}%</td></tr>"
                
                ticker_items = [f"DOLFUT: <span style='color:{("#00ff00" if v_f >= 0 else "#ff4d4d")};'>{v_f:+.2f}%</span>"]
                outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F", "US10Y": "^TNX"}
                
                for lbl, sym in outros.items():
                    d = st.session_state.market_data.get(sym, fetch(sym))
                    if d:
                        f = ".4f" if lbl in ["DOLSPOT", "GBP/USD", "JPY/USD", "EUR/USD"] else (".3f" if lbl=="US10Y" else ".2f")
                        p_v = d['at']/1000 if lbl == "DOLSPOT" else d['at']
                        l_a = st.session_state.last_p.get(lbl, p_v); cl_a = "f-up" if p_v > l_a else "f-dn" if p_v < l_a else ""; st.session_state.last_p[lbl] = p_v
                        var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                        
                        # Inversão para o EWZ na tabela
                        if lbl == "EWZ":
                            var = -var
                            
                        cl_max = "f-up" if lbl == "DOLSPOT" and st.session_state.last_spot_max > 0 and d['mx'] > st.session_state.last_spot_max else ""
                        cl_min = "f-dn" if lbl == "DOLSPOT" and st.session_state.last_spot_min < float('inf') and d['mn'] < st.session_state.last_spot_min else ""
                        if lbl == "DOLSPOT":
                            st.session_state.last_spot_max, st.session_state.last_spot_min = d['mx'], d['mn']
                            
                        html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col {cl_a}'>{p_v:{f}}</td><td>{(d['cl']/1000 if lbl=='DOLSPOT' else d['cl']):{f}}</td><td>{(d['op']/1000 if lbl=='DOLSPOT' else d['op']):{f}}</td><td class='{cl_max}'>{(d['mx']/1000 if lbl=='DOLSPOT' else d['mx']):{f}}</td><td class='{cl_min}'>{(d['mn']/1000 if lbl=='DOLSPOT' else d['mn']):{f}}</td><td style='color:{("#00ff00" if var >= 0 else "#ff4d4d")}; font-weight:bold;'>{var:+.2f}%</td></tr>"
                        ticker_items.append(f"{lbl}: <span style='color:{("#00ff00" if var >= 0 else "#ff4d4d")};'>{var:+.2f}%</span>")
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
                
                # --- PROCESSAMENTO DOS VALORES INTERNOS DA BARRA DE FORÇA ---
                p_v_val = "{:.1f}".format(res['p_v'])
                p_r_val = "{:.1f}".format(res['p_r'])
                c3_val = "{:.4f}".format(res['p_c3_v'] / 1000)
                c2_val = "{:.4f}".format(res['p_c2_v'] / 1000)
                c1_val = "{:.4f}".format(res['p_c1_v'] / 1000)
                v1_val = "{:.4f}".format(res['p_v1_v'] / 1000)
                v2_val = "{:.4f}".format(res['p_v2_v'] / 1000)
                v3_val = "{:.4f}".format(res['p_v3_v'] / 1000)
                sinal_txt = res["seta"] if res["seta"] else "&nbsp;"
                
                var_da_barra_txt = "{:+.2f}%".format(res['pct_afastamento'])
                conteudo_verde = f'<span class="txt-interno-tom-vermelho">{var_da_barra_txt}</span>' if res['p_v'] > 0 else "&nbsp;"
                conteudo_vermelho = f'<span class="txt-interno-tom-verde">{var_da_barra_txt}</span>' if res['p_r'] > 0 else "&nbsp;"

                render_barra = (
                    '<div class="bar-wrapper-full">'
                    '    <div class="force-scale-top">'
                    '        <span style="color:#00ff88; width:15%; text-align:left;">-1.05%</span>'
                    '        <span style="color:#00ff88; width:15%; text-align:left;">-0.70%</span>'
                    '        <span style="color:#00ff88; width:15%; text-align:left;">-0.35%</span>'
                    '        <span style="color:#ffffff; width:10%; text-align:center;">0</span>'
                    '        <span style="color:#ff4d4d; width:15%; text-align:right;">+0.35%</span>'
                    '        <span style="color:#ff4d4d; width:15%; text-align:right;">+0.70%</span>'
                    '        <span style="color:#ff4d4d; width:15%; text-align:right;">+1.05%</span>'
                    '    </div>'
                    '    <div class="force-container-dual">'
                    '        <div class="center-line"></div>'
                    '        <div class="bar-side">'
                    '            <div class="fill-green" style="width: ' + p_v_val + '%;">' + conteudo_verde + '</div>'
                    '        </div>'
                    '        <div class="bar-side">'
                    '            <div class="fill-red" style="width: ' + p_r_val + '%;">' + conteudo_vermelho + '</div>'
                    '        </div>'
                    '    </div>'
                    '    <div class="force-scale-bottom">'
                    '        <span style="width:15%; text-align:left;">' + c3_val + '</span>'
                    '        <span style="width:15%; text-align:left;">' + c2_val + '</span>'
                    '        <span style="width:15%; text-align:left;">' + c1_val + '</span>'
                    '        <span style="color:#ffffff; width:10%; text-align:center;">&nbsp;</span>'
                    '        <span style="width:15%; text-align:right;">' + v1_val + '</span>'
                    '        <span style="width:15%; text-align:right;">' + v2_val + '</span>'
                    '        <span style="width:15%; text-align:right;">' + v3_val + '</span>'
                    '    </div>'
                    '    <div class="sinal-indicator" style="color:' + res["seta_cor"] + '; min-height:18px;">'
                    '        ' + sinal_txt + ''
                    '    </div>'
                    '</div>'
                )
                
                st.markdown(render_barra, unsafe_allow_html=True)
                
                # --- NOVO TERMÔMETRO SEGMENTADO COM PONTEIRO ---
                def get_var(sym):
                    d = st.session_state.market_data.get(sym)
                    if d and d.get('cl', 0) > 0:
                        v = ((d['at'] / d['cl']) - 1) * 100
                        return v
                    return 0.0

                # Cálculo de Correlação (EWZ invertido como solicitado na fórmula)
                v_dxy = get_var("DX-Y.NYB")
                v_ewz = -get_var("EWZ") # Inversão aplicada na fonte
                v_us10y = get_var("^TNX")
                
                media_term = (v_dxy + v_ewz + v_us10y) / 3
                
                # Cores dos blocos com novos limites
                c_bf, c_b, c_n, c_a, c_af = "", "", "", "", ""
                if media_term <= -0.50: c_bf = "active-bf"       # Baixa Forte
                elif media_term < -0.25: c_b = "active-b"        # Baixa
                elif media_term <= 0.25: c_n = "active-n"        # Neutro
                elif media_term < 0.50: c_a = "active-a"         # Alta
                else: c_af = "active-af"                         # Alta Forte
                
                # Cálculo do ponteiro (Range fixo em -1.0 a 1.0 para sensibilidade)
                p_min, p_max = -1.0, 1.0
                pos_percent = ((media_term - p_min) / (p_max - p_min)) * 100
                pos_percent = max(0, min(100, pos_percent)) 
                
                therm_html = f'''
                <div style="position: relative; width: 100%; margin-top: 5px;">
                    <div class="therm-container">
                        <div class="therm-seg {c_bf}">BAIXA<br>FORTE</div>
                        <div class="therm-seg {c_b}">BAIXA</div>
                        <div class="therm-seg {c_n}">NEUTRO</div>
                        <div class="therm-seg {c_a}">ALTA</div>
                        <div class="therm-seg {c_af}">ALTA<br>FORTE</div>
                    </div>
                    <div style="position: absolute; bottom: -8px; left: {pos_percent}%; transform: translateX(-50%); 
                                width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; 
                                border-bottom: 12px solid #ffffff; transition: left 0.5s ease-in-out;">
                    </div>
                </div>
                '''
                st.markdown(therm_html, unsafe_allow_html=True)
                # ----------------------------------
            
            with c2:
                # Coluna de cálculos
                st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                st.markdown(f'''<div class="calc-panel"><div class="calc-row txt-green"><span>MX F2</span> <span>{res['max_fut_2_b']:.1f}</span></div><div class="calc-row txt-yellow"><span>MD F2</span> <span>{res['max_fut_2']:.1f}</span></div><div class="calc-row txt-green"><span>MX F1</span> <span>{res['max_fut_1_b']:.1f}</span></div><div class="calc-row txt-yellow"><span>MD F1</span> <span>{res['max_fut_1']:.1f}</span></div><div style="text-align:center; padding: 4px; color: #00f2ff; font-size: 9px; font-weight: bold; border-top:1px solid #444; border-bottom:1px solid #444;">AXIS: {res['axis_central']:.1f}</div><div class="calc-row txt-yellow"><span>MD F1</span> <span>{res['min_fut_1']:.1f}</span></div><div class="calc-row txt-green"><span>MN F1</span> <span>{res['min_fut_1_b']:.1f}</span></div><div class="calc-row txt-yellow"><span>MD F2</span> <span>{res['min_fut_2']:.1f}</span></div><div class="calc-row txt-green" style="border-bottom: none;"><span>MN F2</span> <span>{res['min_fut_2_b']:.1f}</span></div></div>''', unsafe_allow_html=True)
                
                st.markdown(f'''<div class="calc-panel"><div class="calc-row" style="border-bottom:none; padding-bottom:0px;"><span style="color:#ffffff;">PREÇO JUSTO</span> <span style="color:#00f2ff;">{res['white']:.2f}</span></div><div style="text-align:right; font-size:9px; padding-right:6px; color:{("#00ff00" if res['vivo_pct'] >= 0 else "#ff4d4d")}; font-weight:bold; margin-bottom:4px;">{res['vivo_pct']:+.2f}%</div><div class="calc-row"><span style="color:#ffff00;">MÉDIA DOLAR</span> <span style="color:#00f2ff;">{res['medio']:.2f}</span></div><div class="calc-row"><span style="color:#d4a017;">DOLB3</span> <span style="color:#ffffff;">{res['fraja']:.2f}</span></div><div class="calc-row"><span style="color:#ff4d4d;">SPREAD M</span> <span style="color:#00f2ff;">{res['spreed']:.2f}</span></div><div class="calc-row" style="border-bottom: none;"><span style="color:#00BFFF;">SPREAD T</span> <span style="color:#ffffff;">{res['spreed_t']:.2f}</span></div></div>''', unsafe_allow_html=True)
                
                st.markdown(f'''<div class="calc-panel" style="text-align:center; border: 1.5px solid {res['cor_ind']}; padding-bottom:6px;">
                    <div style="color:#AAA; font-size:10px; font-weight:bold; text-transform:uppercase;">INDICADOR REVERSÃO</div>
                    <div style="color:{res['cor_ind']}; font-size:22px; font-weight:bold; margin-top:2px; margin-bottom:2px;">{res['ind_val']:+.2f}</div>
                    <div style="color:#ffffff; font-size:10px; font-weight:bold; font-family:monospace; margin-bottom:4px;">DIST. BASE (MÍN À BASE): {res['distancia_base_calc']:.2f} pts</div>
                    <div style="display:flex; justify-content:space-between; border-top:1px solid #333; padding-top:4px; font-size:9px; font-weight:bold; padding-left:4px; padding-right:4px;">
                        <span style="color:#00ff88;">GAT. COMPRA: <span style="color:#fff;">{res['gatilho_c']:.2f}</span></span>
                        <span style="color:#ff4d4d;">GAT. VENDA: <span style="color:#ffffff;">{res['gatilho_v']:.2f}</span></span>
                    </div>
                </div>''', unsafe_allow_html=True)
            
            st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)}</div></div>', unsafe_allow_html=True)
            
    time.sleep(5)
