"""
Configuração para extração de dados financeiros dos PDFs.
Define indicadores prioritários, configurações de chunking e prompts.
"""
from typing import List, Dict

# Indicadores financeiros prioritários para extração
FINANCIAL_INDICATORS = {
    "balanco_patrimonial": [
        "Ativo_Total",
        "Passivo_Total",
        "Patrimonio_Liquido",
        "Divida_Total",
        "Divida_Curto_Prazo",
        "Divida_Longo_Prazo",
        "Caixa_Equivalentes",
        "Ativo_Circulante",
        "Passivo_Circulante",
        "Ativo_Nao_Circulante",
        "Passivo_Nao_Circulante",
    ],
    "dre": [
        "Receita_Liquida",
        "Lucro_Bruto",
        "EBITDA",
        "Lucro_Operacional",
        "Lucro_Liquido",
        "Despesas_Financeiras",
        "Receitas_Financeiras",
    ],
    "metadados": [
        "Data_Referencia",
    ]
}

# Configurações de chunking
CHUNKING_CONFIG = {
    "max_pages": 15,  # Máximo de páginas por PDF
    "max_tokens_per_chunk": 8000,  # Tokens por chunk
    "sections_to_find": ["Balanço Patrimonial", "Demonstração do Resultado", "DRE", "Balanço"],
}

# Ranges esperados para validação (valores em milhões de R$)
VALIDATION_RANGES = {
    "Ativo_Total": (1, 1000000),  # 1 milhão a 1 trilhão
    "Passivo_Total": (1, 1000000),
    "Patrimonio_Liquido": (-100000, 1000000),  # Pode ser negativo
    "Receita_Liquida": (1, 500000),
    "Lucro_Liquido": (-50000, 100000),  # Pode ser negativo
}

# Prompt template para extração
EXTRACTION_PROMPT_TEMPLATE = """Você é um especialista em análise de demonstrações financeiras. 
Extraia os seguintes dados financeiros do texto fornecido de uma DFP (Demonstração Financeira Padronizada) brasileira.

INSTRUÇÕES:
1. Extraia APENAS os valores numéricos (sem formatação, sem pontos, sem vírgulas, apenas números)
2. Todos os valores devem estar em milhares de reais (R$ mil)
3. Se um valor não for encontrado, retorne null
4. Retorne APENAS um JSON válido, sem texto adicional

DADOS A EXTRAIR:
- Ativo_Total: Ativo Total do Balanço Patrimonial
- Passivo_Total: Passivo Total do Balanço Patrimonial  
- Patrimonio_Liquido: Patrimônio Líquido
- Divida_Total: Soma de todas as dívidas (empréstimos, financiamentos, debêntures)
- Divida_Curto_Prazo: Dívidas com vencimento até 12 meses
- Divida_Longo_Prazo: Dívidas com vencimento após 12 meses
- Caixa_Equivalentes: Caixa e equivalentes de caixa
- Ativo_Circulante: Ativo Circulante
- Passivo_Circulante: Passivo Circulante
- Ativo_Nao_Circulante: Ativo Não Circulante
- Passivo_Nao_Circulante: Passivo Não Circulante
- Receita_Liquida: Receita Líquida de Vendas/Serviços
- Lucro_Bruto: Lucro Bruto
- EBITDA: EBITDA (se disponível, caso contrário null)
- Lucro_Operacional: Lucro Operacional (EBIT)
- Lucro_Liquido: Lucro Líquido do Período
- Despesas_Financeiras: Despesas Financeiras (juros, variação cambial, etc.)
- Receitas_Financeiras: Receitas Financeiras
- Data_Referencia: Data de referência do balanço (formato: DD/MM/YYYY)

IMPORTANTE:
- Procure pelos valores consolidados (não individuais)
- Valores devem ser do exercício de 2024
- Se houver múltiplos valores, use o mais recente ou consolidado

Retorne APENAS o JSON, sem markdown, sem explicações:
"""

# Modelo LLM a usar
LLM_MODEL = "gpt-4o-mini"  # Mais barato e suficiente para extração estruturada
LLM_TEMPERATURE = 0.1  # Baixa temperatura para respostas mais consistentes

def get_all_indicators() -> List[str]:
    """Retorna lista completa de todos os indicadores."""
    all_indicators = []
    for category in FINANCIAL_INDICATORS.values():
        all_indicators.extend(category)
    return all_indicators

def get_extraction_prompt() -> str:
    """Retorna o prompt de extração formatado."""
    return EXTRACTION_PROMPT_TEMPLATE

