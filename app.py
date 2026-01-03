import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Mesa de Câmbio Pro", layout="wide")

st.title("🏦 TERMINAL PROFISSIONAL")

# Lista correta de ativos
tickers = {
    "DÓLAR SPOT": "USDBRL=X",
    "EWZ (BOLSA BR)": "EWZ",
    "DXY INDEX": "DX-Y.NYB",
    "DI 2027": "DI1F27.SA",
    "DI 2031": "DI1F31.SA"
}

try:
    # Busca dados de 5 dias para ter a variação de fechamento
    df = yf.download(list(tickers.values()), period="1d", interval="1d", progress=False)['Close']
    
    # Cálculos de topo
    spot = df["USDBRL=X"].iloc[-1]
    justo = spot * ((1 + 0.1175)**(1/252) / (1 + 0.045)**(1/252))
    ptax = spot * 1.0002
    
    # Exibição das Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("DÓLAR SPOT", f"{spot:.4f}")
    c2.metric("DÓLAR JUSTO", f"{justo:.4f}")
    c3.metric("PTAX EST.", f"{ptax:.4f}")

    st.write("### Variações do Mercado")
    
    # Montagem da Tabela Colorida
    lista_final = []
    for nome, tk in tickers.items():
        serie = df[tk].dropna()
        atual = serie.iloc[-1]
        anterior = serie.iloc[-2]
        var = ((atual - anterior) / anterior) * 100
        
        lista_final.append({
            "ATIVO": nome,
            "ÚLTIMO": f"{atual:.4f}" if "DÓLAR" in nome else f"{atual:.22f}" if "DI" in nome else f"{atual:.2f}",
            "VAR %": f"{var:+.2f}%",
            "FECH. ANT.": f"{anterior:.4f}" if "DÓLAR" in nome else f"{anterior:.2f}"
        })

    st.table(pd.DataFrame(lista_final))
    st.caption(f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")

except Exception as e:
    st.warning("Carregando dados... Clique em atualizar no navegador se demorar.")
