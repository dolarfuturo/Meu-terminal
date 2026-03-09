# --- MOTOR DE CÁLCULOS K97 ---

def calcular_eixo_diario(max_periodo, min_periodo):
    """
    Regra: Eixo = (MAX + MIN) / 2 
    Referente ao intervalo das 11:30 às 18:00 BRT.
    """
    return (max_periodo + min_periodo) / 2

def calcular_preco_ajustado_dolar(eixo_ativo, eixo_ewz, price_ewz_atual):
    """
    Fórmula: Price = eixo * (eixo_EWZ / price_ewz - 1) * 100 / 2.
    Aplica-se para SPOT e DOLFUT.
    """
    try:
        # Cálculo do desvio do EWZ em relação ao seu próprio eixo
        desvio_ewz = (eixo_ewz / price_ewz_atual) - 1
        
        # Resultado do preço baseado na variação do EWZ (considerando Pre-market 6h)
        return eixo_ativo * desvio_ewz * 100 / 2
    except ZeroDivisionError:
        return eixo_ativo

def calcular_variacao_operacional(valor_atual, eixo_referencia):
    """
    Regra: As variações partem SEMPRE do eixo, não do fechamento.
    """
    if eixo_referencia == 0:
        return 0.0
    return ((valor_atual / eixo_referencia) - 1) * 100

def calcular_limites_volatilidade(eixo, percentual_desvio):
    """
    Regra: Cálculos de volatilidade, MAX e MIN partem do eixo.
    Ex: Para alvo de 1%, percentual_desvio = 0.01
    """
    return eixo * (1 + percentual_desvio)

# --- EXEMPLO DE EXECUÇÃO DO MOTOR ---

# 1. Definição dos Eixos (obtidos entre 11:30 e 18:00 do dia anterior)
eixo_dolar = 5.4200 
eixo_ewz = 32.20

# 2. Captura do mercado atual (EWZ desde às 06:00 BRT)
market_price_ewz = 32.10 

# 3. Processamento do Preço Justo
preco_spot_no_grade = calcular_preco_ajustado_dolar(eixo_dolar, eixo_ewz, market_price_ewz)

# 4. Processamento da Variação da Grade
variacao_spot = calcular_variacao_operacional(preco_spot_no_grade, eixo_dolar)
