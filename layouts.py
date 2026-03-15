import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

# ... (Mantenha suas funções de calcular_eixo_automatico, calcular_k97_total, fetch_data e a Sidebar aqui) ...

# --- FUNÇÃO PARA DESENHAR O GRID HTML/CSS (O SEGREDO DO VISUAL) ---
def desenhar_grid_principal(dados_ativos):
    """
    Recebe um dicionário com os dados formatados e gera o HTML da tabela.
    dados_ativos = {
        'SPOT': {'price': '5.2150', 'close': '5.2000', 'var': '+0.29', 'cor': '#00f2ff'},
        'DOLFUT': {...},
        ...
    }
    """
    
    # Início da Tabela com Estilo CSS para o Grid
    html_table = """
    <style>
        .terminal-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'monospace';
            font-size: 14px;
            color: #ffffff;
            border: 1px solid #333; /* Borda externa */
        }
        .terminal-table th {
            background-color: #000000; /* Fundo do Cabeçalho Preto */
            color: #888; /* Texto do Cabeçalho Cinza */
            text-align: left;
            padding: 8px;
            border: 1px solid #333; /* Linhas do Grid */
            text-transform: uppercase;
        }
        .terminal-table td {
            background-color: #1a1a1a; /* Fundo das Células Cinza Escuro */
            padding: 8px;
            border: 1px solid #333; /* Linhas do Grid */
            vertical-align: middle;
        }
        /* Alinhamento à direita para colunas numéricas */
        .terminal-table td:nth-child(n+2), 
        .terminal-table th:nth-child(n+2) {
            text-align: right;
        }
        /* Estilo para a coluna Asset (primeira) */
        .terminal-table td:first-child {
            font-weight: bold;
            color: #ffffff;
        }
    </style>
    <table class="terminal-table">
        <thead>
            <tr>
                <th>Asset</th>
                <th>Price</th>
                <th>Close</th>
                <th>Open</th>
                <th>Max</th>
                <th>Min</th>
                <th>Var</th>
            </tr>
        </thead>
        <tbody>
    """
    
    # Preenchimento Dinâmico das Linhas (Blocks)
    for ativo, info in dados_ativos.items():
        html_table += f"""
            <tr>
                <td>{ativo}</td>
                <td style="color: #ffffff; font-size: 16px;">{info['price']}</td>
                <td>{info['close']}</td>
                <td>{info['open']}</td>
                <td>{info['max']}</td>
                <td>{info['min']}</td>
                <td style="color: {info['cor']}; font-weight: bold;">{info['var']}%</td>
            </tr>
        """
        
    # Fechamento da Tabela
    html_table += """
        </tbody>
    </table>
    """
    
    return html_table

# --- ÁREA PRINCIPAL DE EXIBIÇÃO (ONDE O GRID É CHAMADO) ---
# Simulando os dados capturados para demonstração do layout
# Na sua versão real, você preencherá este dicionário com os dados do yfinance e K97
dados_para_exibir = {
    'SPOT': {'price': '5.2150', 'close': '5.1980', 'open': '5.1980', 'max': '5.2210', 'min': '5.1950', 'var': '+0.33', 'cor': '#00f2ff'},
    'DOLFUT': {'price': '5.228.50', 'close': '5.210.00', 'open': '5.212.00', 'max': '5.235.00', 'min': '5.208.00', 'var': '+0.35', 'cor': '#00f2ff'},
    'DXY': {'price': '104.520', 'close': '104.600', 'open': '104.605', 'max': '104.710', 'min': '104.480', 'var': '-0.08', 'cor': '#ff4d4d'},
    'EWZ': {'price': '31.85', 'close': '32.10', 'open': '32.05', 'max': '32.15', 'min': '31.78', 'var': '-0.78', 'cor': '#ff4d4d'},
    'K97 SINTETICO': {'price': '5.219.50', 'close': '5.219.50', 'open': 'EIXO', 'max': '5.255.10', 'min': '5.183.90', 'var': '0.00', 'cor': '#ffffff'} # Exemplo do seu K97 integrado
}

# Título do Terminal (BAIR - TERMINAL DOLAR)
st.markdown("<h1 style='text-align: center; color: #ffffff; font-family: monospace;'>BAIR - TERMINAL DOLAR</h1>", unsafe_allow_html=True)

# Chamada da função para desenhar o Grid
html_do_grid = desenhar_grid_principal(dados_para_exibir)
st.markdown(html_do_grid, unsafe_allow_html=True)

# ... (Mantenha o st.rerun() e time.sleep() no final) ...

