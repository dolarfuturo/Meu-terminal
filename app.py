st.write("### Variações do Mercado")

# Função para buscar cada ativo individualmente (evita travar a tabela toda)
def buscar_variacao(ticker_name, ticker_symbol):
    try:
        # Busca dados de 2 dias para calcular a variação
        data = yf.download(ticker_symbol, period="2d", interval="1d", progress=False)
        if not data.empty and len(data) >= 2:
            atual = data['Close'].iloc[-1]
            anterior = data['Close'].iloc[-2]
            var = ((atual - anterior) / anterior) * 100
            return f"{atual:.2f}", f"{var:+.2f}%"
        return "---", "0.00%"
    except:
        return "Erro", "0.00%"

# Montando a visualização em colunas para ser mais leve que a tabela
col_ewz, col_dxy, col_di = st.columns(3)

val_ewz, var_ewz = buscar_variacao("EWZ", "EWZ")
col_ewz.metric("EWZ (Bolsa BR)", val_ewz, var_ewz)

val_dxy, var_dxy = buscar_variacao("DXY", "DX-Y.NYB")
col_dxy.metric("DXY (Dólar Global)", val_dxy, var_dxy)

val_di, var_di = buscar_variacao("DI 2027", "DI1F27.SA")
col_di.metric("DI 2027", val_di, var_di)
