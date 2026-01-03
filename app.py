st.write("### Variações do Mercado")

def buscar_var(label, ticker):
    try:
        # Busca 5 dias para garantir que pegamos o último fechamento útil
        d = yf.download(ticker, period="5d", interval="1d", progress=False)
        if len(d) >= 2:
            atual = d['Close'].iloc[-1]
            anterior = d['Close'].iloc[-2]
            variacao = ((atual - anterior) / anterior) * 100
            st.metric(label, f"{atual:.2f}", f"{variacao:+.2f}%")
        else:
            st.write(f"Sem dados para {label}")
    except:
        st.write(f"Erro em {label}")

c1, c2, c3 = st.columns(3)
with c1: buscar_var("EWZ (Bolsa BR)", "EWZ")
with c2: buscar_var("DXY (Dólar)", "DX-Y.NYB")
with c3: buscar_var("S&P 500", "^GSPC")
