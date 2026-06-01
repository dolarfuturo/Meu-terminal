import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime
import pytz

# Configuração para Tablet
st.set_page_config(layout="wide", page_title="BAIR - TERMINAL DOLLAR", initial_sidebar_state="collapsed")

# --- FUNÇÕES DE PERSISTÊNCIA ---
def salvar_eixos(div_spreed, dol, axis_fut):
    with open("config_axis.txt", "w") as f:
        f.write(f"{div_spreed},{dol},{axis_fut}")

def carregar_eixos():
    if os.path.exists("config_axis.txt"):
        try:
            with open("config_axis.txt", "r") as f:
                dados = f.read().split(",")
                d1 = float(dados[0])
                d2 = float(dados[1])
                d3 = float(dados[2]) if len(dados) > 2 else d2
                return d1, d2, d3
        except: pass
    return 8.0, 5246.0, 5246.0

# --- PERSISTÊNCIA DIÁRIA EM ARQUIVO PARA MAX/MIN DO DOLFUT (SINC RESTRITO: 09:00 ÀS 18:30) ---
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

div_spreed_salvo, eixo_dol_salvo, axis_fut_salvo = carregar_eixos()

if 'market_data' not in st.session_state: st.session_state.market_data = {}
if 'last_p' not in st.session_state: st.session_state.last_p = {}
if 'div_spreed_mem' not in st.session_state: st.session_state.div_spreed_mem = div_spreed_salvo
if 'a_dol_mem' not in st.session_state: st.session_state.a_dol_mem = eixo_dol_salvo
if 'a_fut_mem' not in st.session_state: st.session_state.a_fut_mem = axis_fut_salvo

# Inicializa carregando do arquivo persistente para evitar perdas com F5
max_init, min_init = carregar_historico_dolfut_diario()
if 'dolfut_max_auto' not in st.session_state: st.session_state.dolfut_max_auto = max_init
if 'dolfut_min_auto' not in st.session_state: st.session_state.dolfut_min_auto = min_init

# --- MEMÓRIA ADICIONAL PARA SINALIZAR RUPTURA DE MÁX/MÍN DO SPOT ---
if 'last_spot_max' not in st.session_state: st.session_state.last_spot_max = 0.0
if 'last_spot_min' not in st.session_state: st.session_state.last_spot_min = float('inf')

# --- MEMÓRIA DOS CAMPOS DA CALCULADORA ---
if 'c_spot_fech_val' not in st.session_state: st.session_state.c_spot_fech_val = 0.0
if 'c_du_val' not in st.session_state: st.session_state.c_du_val = 22
if 't_br_val' not in st.session_state: st.session_state.t_br_val = 14.50
if 't_us_val' not in st.session_state: st.session_state.t_us_val = 3.75

# --- CSS ORIGINAL ---
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
    .bar-wrapper-full { background: #0a141a; padding: 6px; border: 1.5px solid #ffffff; border-radius: 4px; text-align: center; margin-top: 5px; }
    .force-scale { display: flex; justify-content: space-between; font-size: 8px; font-family: monospace; color: #AAA; margin-bottom: 2px; padding: 0 5px; }
    .force-container-dual { background: #111; height: 10px; width: 100%; border-radius: 2px; position: relative; overflow: hidden; display: flex; border: 1px solid #444; }
    .center-line { position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: #fff; z-index: 10; }
    .bar-side { width: 50%; height: 100%; position: relative; background: #050a0e; }
    .fill-green { background: #00ff88; float: right; height: 100%; transition: width 0.4s; }
    .fill-red { background: #ff4d4d; float: left; height: 100%; transition: width 0.4s; }
    .sinal-indicator { font-size: 11px; font-weight: 900; line-height: 1; margin-top: 4px; }
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.1; } }
    .ticker-wrapper { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; border-top: 1.5px solid #ffffff; border-bottom: 1.5px solid #ffffff; padding: 4px 0; overflow: hidden; white-space: nowrap; margin-top: 8px; }
    .ticker-text { display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'monospace'; font-size: 12px; font-weight: bold; color: #fff; }
    @keyframes marquee { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .txt-green { color: #00ff88 !important; }
    .txt-yellow { color: #ffff00 !important; }
    .txt-red { color: #ff4d4d !important; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
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

# --- CÁLCULOS K97 ---
def calcular_k97_total(spreed_do_dia, p_ewz_atual, eixo_dol, spot_data, us10y_data):
    try:
        if not spot_data or p_ewz_atual == 0 or not us10y_data: return None
        dolar_medio = (spot_data['mx'] + spot_data['mn']) / 2
        fraja_val = spot_data['at'] + spreed_do_dia
        dxy_data = fetch("DX-Y.NYB")
        v_dxy = ((dxy_data['at'] / dxy_data['cl']) - 1) if dxy_data['cl'] > 0 else 0
        ewz_ref = st.session_state.market_data.get("EWZ", {}).get('cl', 1)
        v_ewz = ((p_ewz_atual / ewz_ref) - 1) if ewz_ref > 0 else 0
        
        # --- AJUSTE REGISTRADO: Variação internacional para DOLFUT e DOLB3 ---
        calc_variacoes_pct = (v_dxy * 0.7) - (v_ewz * 0.3)
        
        # --- MODIFICAÇÃO SOLICITADA: Preço Justo (vivo_val) partindo estritamente do FECHAMENTO DO SPOT (cl) ---
        vivo_val = spot_data['cl'] * (1 + calc_variacoes_pct) 
        
        # --- AJUSTE REGISTRADO: Novo Axis Dinâmico e Degraus pelo FRP ---
        axis_dinamico = dolar_medio + spreed_do_dia
        
        spreed_t = spot_data['mx'] - spot_data['mn']
        spreed_50 = spreed_t / 2
        v_spreed_calc = spreed_t / 2
        
        alvo_low = spot_data['mn'] + spreed_do_dia
        alvo_high = spot_data['mx'] + spreed_do_dia
        
        max_original, min_original = axis_dinamico + (spreed_t * 0.75), axis_dinamico - (spreed_t * 0.25)
        
        # --- MODIFICAÇÃO SOLICITADA: Barra de força ancorada puramente na distância em relação ao PREÇO JUSTO (vivo_val) ---
        diff = spot_data['at'] - vivo_val
        p_v, p_r = 0, 0
        seta_txt, seta_cor, piscando = "", "#000000", False
        if v_spreed_calc > 0:
            calculo_pct = (abs(diff) / (v_spreed_calc * 5.0)) * 100 
            if diff < 0: p_v = min(100, calculo_pct)
            else: p_r = min(100, calculo_pct)
        if p_v >= 100: seta_txt, seta_cor, piscando = "▲ REGIÃO DE COMPRA", "#00ff88", True
        elif p_r >= 100: seta_txt, seta_cor, piscando = "▼ REGIÃO DE VENDA", "#ff4d4d", True
        v_spot_pct = ((spot_data['at'] / spot_data['cl']) - 1) if spot_data['cl'] > 0 else 0
        
        # --- AJUSTE REGISTRADO: Preço do DOLFUT ancorado no Axis Dinâmico ---
        dolfut_atual_calc = axis_dinamico * (1 + calc_variacoes_pct)
        
        # --- AJUSTE EXCLUSIVO: RASTREAMENTO RESTRITO AO HORÁRIO COM PERSISTÊNCIA REAL NO DISCO ---
        tz_sp = pytz.timezone('America/Sao_Paulo')
        now_br = datetime.now(tz_sp)
        
        # Faz a leitura do arquivo para sincronizar caso outra thread/sessão tenha atualizado
        f_max, f_min = carregar_historico_dolfut_diario()
        if f_max != float('-inf'): st.session_state.dolfut_max_auto = max(st.session_state.dolfut_max_auto, f_max)
        if f_min != float('inf'): st.session_state.dolfut_min_auto = min(st.session_state.dolfut_min_auto, f_min)
        
        # Verifica se estamos rigorosamente dentro do intervalo de tempo (09:00 às 18:30)
        if (now_br.hour > 9 or (now_br.hour == 9 and now_br.minute >= 0)) and (now_br.hour < 18 or (now_br.hour == 18 and now_br.minute <= 30)):
            mudou = False
            if dolfut_atual_calc > st.session_state.dolfut_max_auto:
                st.session_state.dolfut_max_auto = dolfut_atual_calc
                mudou = True
            if dolfut_atual_calc < st.session_state.dolfut_min_auto:
                st.session_state.dolfut_min_auto = dolfut_atual_calc
                mudou = True
            if mudou:
                salvar_historico_dolfut_diario(st.session_state.dolfut_max_auto, st.session_state.dolfut_min_auto)
        else:
            # Fora do horário, se o arquivo diário não existir ou for de outro dia, força inicialização com o valor atual
            if st.session_state.dolfut_max_auto == float('-inf') or st.session_state.dolfut_min_auto == float('inf'):
                st.session_state.dolfut_max_auto = dolfut_atual_calc
                st.session_state.dolfut_min_auto = dolfut_atual_calc
                salvar_historico_dolfut_diario(dolfut_atual_calc, dolfut_atual_calc)

        return {
            "vivo": vivo_val, 
            "vivo_pct": calc_variacoes_pct * 100, 
            "dolfut_calc": dolfut_atual_calc, 
            "fraja": fraja_val, 
            "medio": dolar_medio, 
            "axis_central": axis_dinamico,
            "max_fut_1": axis_dinamico + spreed_do_dia,
            "max_fut_2": axis_dinamico + (spreed_do_dia * 2),
            "max_fut_3": axis_dinamico + (spreed_do_dia * 3),
            "max_fut_4": axis_dinamico + (spreed_do_dia * 4),
            "max_fut_5": axis_dinamico + (spreed_do_dia * 5),
            "min_fut_1": axis_dinamico - spreed_do_dia,
            "min_fut_2": axis_dinamico - (spreed_do_dia * 2),
            "min_fut_3": axis_dinamico - (spreed_do_dia * 3),
            "min_fut_4": axis_dinamico - (spreed_do_dia * 4),
            "min_fut_5": axis_dinamico - (spreed_do_dia * 5),
            "v_v": calc_variacoes_pct * 100, 
            "v_spot": v_spot_pct * 100, 
            "spreed": spreed_50, 
            "p_v": p_v, 
            "p_r": p_r, 
            "seta": seta_txt, 
            "seta_cor": seta_cor, 
            "piscando": piscando, 
            "max_grade": st.session_state.dolfut_max_auto, 
            "min_grade": st.session_state.dolfut_min_auto, 
            "alvo_low": alvo_low, 
            "alvo_high": alvo_high, 
            "spreed_t": spreed_t
        }
    except: return None

# --- SIDEBAR COM CALCULADORA DE JUROS MEMORIZADA ---
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
    i_dol = st.number_input("AXIS DOLFUT:", value=st.session_state.a_dol_mem, format="%.2f")
    i_fut = st.number_input("AXIS FUT (DOLB3 VAR):", value=st.session_state.a_fut_mem, format="%.2f")
    if st.button("SALVAR CONFIGURAÇÕES"):
        st.session_state.div_spreed_mem, st.session_state.a_dol_mem, st.session_state.a_fut_mem = i_div, i_dol, i_fut
        salvar_eixos(i_div, i_dol, i_fut)
        st.success("Salvo!"); time.sleep(0.5); st.rerun()

div_s, a_dol, a_fut = st.session_state.div_spreed_mem, st.session_state.a_dol_mem, st.session_state.a_fut_mem
placeholder = st.empty()

# --- LOOP PRINCIPAL ---
while True:
    tz_sp, tz_ny, tz_ld, tz_utc = pytz.timezone('America/Sao_Paulo'), pytz.timezone('America/New_York'), pytz.timezone('Europe/London'), pytz.utc
    spot_live, ewz_live, us10y_live = fetch("USDBRL=X"), fetch("EWZ"), fetch("^TNX")
    now = datetime.now()
    with placeholder.container():
        st.markdown(f'''<div class="header-container"><h1 class="main-title"><span class="bair-blue">BAIR</span><span class="terminal-gold"> - TERMINAL DOLLAR</span></h1><div class="clock-row"><span class="clock-item">🇧🇷 BR: <span class="br-green">{now.astimezone(tz_sp).strftime("%H:%M:%S")}</span></span><span class="clock-item">🇺🇸 NY: <span class="white-time">{now.astimezone(tz_ny).strftime("%H:%M:%S")}</span></span><span class="clock-item">🇬🇧 LDN: <span class="white-time">{now.astimezone(tz_ld).strftime("%H:%M:%S")}</span></span><span class="clock-item">🌐 UTC: <span class="utc-gold">{now.astimezone(tz_utc).strftime("%H:%M:%S")}</span></span></div><div class="date-container">📅 {now.astimezone(tz_sp).strftime("%d/%m/%Y")}</div></div>''', unsafe_allow_html=True)
        res = calcular_k97_total(div_s, ewz_live['at'] if ewz_live else 0, a_dol, spot_live, us10y_live)
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
                
                # --- MODIFICAÇÃO SOLICITADA: Seta baseada exclusivamente se o SPOT PRICE está ACIMA ou ABAIXO da Média do Dólar ---
                if spot_live and spot_live['at'] > res['medio']:
                    seta_spread, cor_seta_spread = ("▲", "#00ff88")
                else:
                    seta_spread, cor_seta_spread = ("▼", "#ff4d4d")
                    
                for lbl, sym in outros.items():
                    d = fetch(sym)
                    if d:
                        f = ".4f" if lbl in ["DOLSPOT", "GBP/USD", "JPY/USD", "EUR/USD"] else (".3f" if lbl=="US10Y" else ".2f")
                        p_v = d['at']/1000 if lbl == "DOLSPOT" else d['at']
                        l_a = st.session_state.last_p.get(lbl, p_v); cl_a = "f-up" if p_v > l_a else "f-dn" if p_v < l_a else ""; st.session_state.last_p[lbl] = p_v
                        var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                        
                        # --- MODIFICAÇÃO SOLICITADA: Piscar Max ou Min do DOLSPOT no momento exato do rompimento intraday ---
                        cl_max = ""
                        cl_min = ""
                        if lbl == "DOLSPOT":
                            if st.session_state.last_spot_max > 0 and d['mx'] > st.session_state.last_spot_max:
                                cl_max = "f-up"
                            if st.session_state.last_spot_min < float('inf') and d['mn'] < st.session_state.last_spot_min:
                                cl_min = "f-dn"
                            
                            st.session_state.last_spot_max = d['mx']
                            st.session_state.last_spot_min = d['mn']
                            
                        html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col {cl_a}'>{p_v:{f}}</td><td>{(d['cl']/1000 if lbl=='DOLSPOT' else d['cl']):{f}}</td><td>{(d['op']/1000 if lbl=='DOLSPOT' else d['op']):{f}}</td><td class='{cl_max}'>{(d['mx']/1000 if lbl=='DOLSPOT' else d['mx']):{f}}</td><td class='{cl_min}'>{(d['mn']/1000 if lbl=='DOLSPOT' else d['mn']):{f}}</td><td style='color:{("#00ff00" if var >= 0 else "#ff4d4d")}; font-weight:bold;'>{var:+.2f}%</td></tr>"
                        ticker_items.append(f"{lbl}: <span style='color:{("#00ff00" if var >= 0 else "#ff4d4d")};'>{var:+.2f}%</span>")
                st.markdown(html + "</tbody></table></div>", unsafe_allow_html=True)
                st.markdown(f'''<div class="bar-wrapper-full"><div class="force-scale"><span>100%</span><span>50%</span><span>0%</span><span>50%</span><span>100%</span></div><div class="force-container-dual"><div class="center-line"></div><div class="bar-side"><div class="fill-green" style="width: {res["p_v"]}%;"></div></div><div class="bar-side"><div class="fill-red" style="width: {res["p_r"]}%;"></div></div></div><div style="display: flex; justify-content: space-between; align-items: center; font-size: 10px; font-family: monospace; color: #AAA; margin-top: 2px; padding: 0 2px;"><span>LOW: {res['alvo_low']:.2f}</span><span style="color:{cor_seta_spread}; font-size: 14px; font-weight: bold;">{seta_spread}</span><span>HIGH: {res['alvo_high']:.2f}</span></div><div class="sinal-indicator {"blink" if res["piscando"] else ""}" style="color:{res["seta_cor"]};">{res["seta"]}</div></div>''', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="section-title">CÁLCULOS</div>', unsafe_allow_html=True)
                st.markdown(f'''<div class="calc-panel"><div class="calc-row txt-green"><span>MAX FUT 5</span> <span>{res['max_fut_5']:.2f}</span></div><div class="calc-row txt-yellow"><span>MAX FUT 4</span> <span>{res['max_fut_4']:.2f}</span></div><div class="calc-row txt-green"><span>MAX FUT 3</span> <span>{res['max_fut_3']:.2f}</span></div><div class="calc-row txt-yellow"><span>MAX FUT 2</span> <span>{res['max_fut_2']:.2f}</span></div><div class="calc-row txt-green"><span>MAX FUT 1</span> <span>{res['max_fut_1']:.2f}</span></div><div style="text-align:center; padding: 4px; color: #00f2ff; font-size: 10px; font-weight: bold; border-top:1px solid #444; border-bottom:1px solid #444;">AXIS: {res['axis_central']:.2f}</div><div class="calc-row txt-green"><span>MIN FUT 1</span> <span>{res['min_fut_1']:.2f}</span></div><div class="calc-row txt-yellow"><span>MIN FUT 2</span> <span>{res['min_fut_2']:.2f}</span></div><div class="calc-row txt-green"><span>MIN FUT 3</span> <span>{res['min_fut_3']:.2f}</span></div><div class="calc-row txt-yellow"><span>MIN FUT 4</span> <span>{res['min_fut_4']:.2f}</span></div><div class="calc-row txt-green" style="border-bottom: none;"><span>MIN FUT 5</span> <span>{res['min_fut_5']:.2f}</span></div></div>''', unsafe_allow_html=True)
                st.markdown(f'''<div class="calc-panel"><div class="calc-row" style="border-bottom:none; padding-bottom:0px;"><span style="color:#ffffff;">PREÇO JUSTO</span> <span style="color:#00f2ff;">{res['vivo']:.2f}</span></div><div style="text-align:right; font-size:9px; padding-right:6px; color:{("#00ff00" if res['vivo_pct'] >= 0 else "#ff4d4d")}; font-weight:bold; margin-bottom:4px;">{res['vivo_pct']:+.2f}%</div><div class="calc-row"><span style="color:#ffff00;">MÉDIA DOLAR</span> <span style="color:#00f2ff;">{res['medio']:.2f}</span></div><div class="calc-row"><span style="color:#d4a017;">DOLB3</span> <span style="color:#ffffff;">{res['fraja']:.2f}</span></div><div class="calc-row"><span style="color:#ff4d4d;">SPREAD M</span> <span style="color:#00f2ff;">{res['spreed']:.2f}</span></div><div class="calc-row" style="border-bottom: none;"><span style="color:#00BFFF;">SPREAD T</span> <span style="color:#ffffff;">{res['spreed_t']:.2f}</span></div></div>''', unsafe_allow_html=True)
            st.markdown(f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)}</div></div>', unsafe_allow_html=True)
        else: st.warning("Aguardando inicialização dos dados do mercado...")
    time.sleep(5)
