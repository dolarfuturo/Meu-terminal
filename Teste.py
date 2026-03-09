import datetime

# --- MOTOR DE CÁLCULOS K97 - CORE ENGINE ---
# Data: 2026-03-08

def get_eixo(max_val, min_val):
    """
    Calcula o ponto médio âncora.
    Regra: Eixo = (MAX + MIN) / 2
    Referente ao intervalo 11:30 - 18:00 BRT.
    """
    return (max_val + min_val) / 2

def get_variacao_operacional(preco_atual, eixo_ref):
    """
    Regra: Variações partem sempre do Eixo, não do fechamento.
    """
    if eixo_ref == 0: return 0.0
    return ((preco_atual / eixo_ref) - 1) * 100

def get_fair_price_dolar(eixo_ativo, eixo_ewz, price_ewz_atual):
    """
    Fórmula de Arbitragem: eixo * (eixo_EWZ / price_ewz - 1) * 100 / 2.
    Aplicável a SPOT e DOLFUT.
    """
    try:
        # Mede o desvio do EWZ (desde o pré-market das 06:00 BRT)
        desvio_ewz = (eixo_ewz / price_ewz_atual) - 1
        return eixo_ativo * desvio_ewz * 100 / 2
    except ZeroDivisionError:
        return eixo_ativo

def get_volatilidade_alvo(eixo, perc_desvio):
    """
    Regra: MAX e MIN calculadas partindo do eixo conforme o ativo anda.
    """
    return eixo * (1 + (perc_desvio / 100))

# --- BLOCO DE TESTE (CI/CD GITHUB) ---
if __name__ == "__main__":
    # Dados de Exemplo (Anotações do Usuário)
    EIXO_DOLAR_ONTEM = 5.4200 
    EIXO_EWZ_ONTEM = 32.20
    
    # Simulação: EWZ no Pré-Market (06:00 BRT)
    PRECO_EWZ_AGORA = 32.10 
    
    # 1. Calculando Preço Justo (Motor)
    preco_justo = get_fair_price_dolar(EIXO_DOLAR_ONTEM, EIXO_EWZ_ONTEM, PRECO_EWZ_AGORA)
    
    # 2. Calculando Variação sobre o Eixo
    var_percentual = get_variacao_operacional(preco_justo, EIXO_DOLAR_ONTEM)
    
    # 3. Calculando Alvo Operacional (Ex: 1% do Eixo)
    alvo_1_percento = get_volatilidade_alvo(EIXO_DOLAR_ONTEM, 1.0)

    # Output Técnico
    print(f"--- K97 MOTOR TEST ---")
    print(f"Eixo Ref: {EIXO_DOLAR_ONTEM}")
    print(f"Preço Justo (Arbitragem EWZ): {preco_justo:.4f}")
    print(f"Variação vs Eixo: {var_percentual:.2f}%")
    print(f"Alvo Volatilidade (1%): {alvo_1_percento:.4f}")
