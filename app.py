import streamlit as st
import yfinance as yf

# 1. Configuração de Estilo e Layout Profissional
st.set_page_config(page_title="Terminal Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; color: #ffffff; }
    div[data-testid="stMetricDelta"] { font-size: 20px; }
    [data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Painel de Controle Lateral
with st.sidebar:
    st.header("⚙️ Ajustes")
    frp_ajuste = st.number_input("Ajuste FRP", value=0.0150, format="%.4f", step=0.0001)
    st.info("FRP somado ao Spot para o cálculo do Futuro.")

st.title("🏦 TERMINAL PROFISSIONAL")

# 2. FUNÇÃO MESTRE PARA BUSCAR DADOS (Garante variação mesmo no fim de semana)
def buscar_resumo(ticker, period="7d"):
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        if not df.empty and len(df) >= 2:
            atual = float(df['Close'].iloc[-1])
            anterior = float(df['Close'].iloc[-2])
            variacao = ((atual - anterior) / anterior) * 100
            return atual, variacao
        return None, None
    except:
        return None, None

# 3. BLOCO SUPERIOR: CÂMBIO E BITCOIN
st.subheader("💹 Câmbio & Cripto")
col_spot, col_fut, col_btc = st.columns(3)

# Dólar Spot e Futuro
spot_val, spot_var = buscar_resumo("USDBRL=X")
if spot_val:
    col_spot.metric("DÓLAR SPOT", f"R$ {spot_val:.4f}", f"{spot_var:+.2f}%")
    col_fut.metric("DÓLAR FUTURO", f"R$ {spot_val + frp_ajuste:.4f}", help="Spot + FRP")
else:
    col_spot.error("Dólar: Offline")

# Bitcoin (Sempre ativo)
btc_val, btc_var = buscar_resumo("BTC-USD")
if btc_val:
    # Convertendo aproximado para Real (multiplicado pelo spot)
    btc_brl = btc_val * (spot_val if spot_val else 5.42)
    col_btc.metric("BITCOIN (BRL)", f"R$ {btc_brl:,.0f}", f"{btc_var:+.2f}%")

st.divider()

# 4. BLOCO INFERIOR: JUROS E ÍNDICES
st.subheader("📊 Juros (DI) e Ativos Globais")
c1, c2, c3, c4 = st.columns(4)

# Lista de ativos para busca automática
ativos = [
    ("DI 2027", "DI1F27.SA", c1, "%"),
    ("DI 2029", "DI1F29.SA", c2, "%"),
    ("EWZ (Bolsa BR)", "EWZ", c3, ""),
    ("DXY (Dólar Global)", "DX-Y.NYB", c4, "")
]

for nome, ticker, col, suf in ativos:
    val, var = buscar_resumo(ticker)
    if val:
        col.metric(nome, f"{val:.2f}{suf}", f"{var:+.2f}%")
    else:
        col.info(f"{nome}: Aguardando...")

st.caption("🚀 Terminal atualizado. BTC opera 24h. Outros ativos mostram o último fechamento de sexta-feira.")

