"""
Configuração de valores de referência dos indexadores para cálculo de Kd.
Valores baseados em dados de 2024.
"""
from typing import Dict

# Valores de referência dos indexadores (taxa anual em decimal)
# Baseados em dados de 2024 do Brasil
INDEXER_BASE_VALUES: Dict[str, float] = {
    'CDI': 0.1365,  # ~13,65% a.a. (média 2024)
    'DI': 0.1365,   # Similar ao CDI
    'TLP': 0.0650,  # ~6,50% a.a. (Taxa de Longo Prazo - BNDES)
    'TJLP': 0.0650, # Taxa de Juros de Longo Prazo (antiga, substituída por TLP)
    'IPCA': 0.0462, # ~4,62% a.a. (inflação projetada 2024)
    'TR': 0.0001,   # Taxa Referencial (muito baixa, quase desuso)
    'PRE_FIXADO': None,  # Taxa já é o Kd final, não precisa de base
    'SELIC': 0.1050, # ~10,50% a.a. (taxa básica de juros)
}

# Mapeamento de variações de nomes para tipos padronizados
INDEXER_ALIASES: Dict[str, str] = {
    'CDI': 'CDI',
    'CERTIFICADO DE DEPÓSITO INTERBANCÁRIO': 'CDI',
    'DI': 'DI',
    'DEPÓSITO INTERBANCÁRIO': 'DI',
    'TLP': 'TLP',
    'TAXA DE LONGO PRAZO': 'TLP',
    'TJLP': 'TLP',
    'TAXA DE JUROS DE LONGO PRAZO': 'TLP',
    'IPCA': 'IPCA',
    'IPCA-E': 'IPCA',
    'IGP-M': 'IPCA',  # Usar IPCA como proxy
    'TR': 'TR',
    'TAXA REFERENCIAL': 'TR',
    'PRÉ-FIXADO': 'PRE_FIXADO',
    'PREFIXADO': 'PRE_FIXADO',
    'PRE FIXADO': 'PRE_FIXADO',
    'FIXO': 'PRE_FIXADO',
    'FIXA': 'PRE_FIXADO',
    'SELIC': 'SELIC',
}

# Padrões regex para identificação de indexadores (ordem importa - mais específicos primeiro)
INDEXER_PATTERNS = {
    # SOFR (taxa internacional)
    'SOFR': r'\bSOFR\b',
    # LIBOR
    'LIBOR': r'\bLIBOR\b',
    # TLP/TJLP (verificar antes de IPCA pois pode ter "TLP_IPCA")
    'TLP': r'\bTLP(?:_IPCA)?\b',
    'TJLP': r'\bTJLP\b',
    # IPCA e variações
    'IPCA': r'\bIPCA(?:-E)?\b',
    'IGPM': r'\bIGP[-\s]?M\b',
    'IPC': r'\bIPC\b',
    # DI (verificar antes de CDI pois pode ter "100% do DI")
    'DI': r'\b(?:100%?\s+)?(?:do\s+)?DI\b',
    # CDI
    'CDI': r'\bCDI\b',
    # SELIC
    'SELIC': r'\bSELIC\b',
    # TR
    'TR': r'\bTR\b',
    # Pré-fixado (verificar por último, mas antes de percentual direto)
    'PRE_FIXADO': r'\b(?:pr[ée][\s-]?fixado|prefixado|fixo|fixa|pr[ée])\b',
    # Pós-fixado
    'POS_FIXADO': r'\b(?:p[oó]s[\s-]?fixado|posfixado)\b',
}

# Padrões para extração de spread (ordem importa - mais específicos primeiro)
SPREAD_PATTERNS = [
    # Spread negativo
    r'[-\u2013\u2014]\s*(\d+[.,]\d+)\s*%',  # -1,5% (com diferentes tipos de hífen)
    # Spread positivo com sinal
    r'[+\u002B]\s*(\d+[.,]\d+)\s*%',  # +1,5%
    # Percentual com período anual
    r'(\d+[.,]\d+)\s*%\s*(?:a\.?a\.?|ao\s+ano)',  # 1,5% a.a.
    # Percentual com período mensal
    r'(\d+[.,]\d+)\s*%\s*(?:a\.?m\.?|ao\s+m[êe]s)',  # 1,5% a.m.
    # Faixa de percentual (pega o primeiro valor)
    r'(\d+[.,]\d+)\s*%\s*a\s*\d+[.,]\d+\s*%',  # 5,60% a 9,88%
    # Percentual simples
    r'(\d+[.,]\d+)\s*%',  # 1,5%
    # Percentual sem vírgula/ponto (raro mas possível)
    r'(\d+)\s*%',  # 15%
]

# Padrões para identificação de período
PERIOD_PATTERNS = {
    'a.a.': [r'a\.?a\.?', r'ao\s+ano', r'anual'],
    'a.m.': [r'a\.?m\.?', r'ao\s+m[êe]s', r'mensal'],
}

# Valores padrão quando não especificado
DEFAULT_PERIOD = 'a.a.'  # Assumir anual se não especificado

# Ranges de validação
MIN_Kd = 0.0  # 0%
MAX_Kd = 0.50  # 50% a.a. (limite superior razoável)

# Valores para tratamento de casos especiais
MISSING_INDICATORS = ['não especificado', 'nao especificado', 'não informado', 
                      'nao informado', 'não definido', 'nao definido', 
                      'não há', 'nao ha', 'sem informação', '-', 'nan', 'none']

# Padrões para percentuais diretos (sem indexador explícito) - tratar como pré-fixado
PERCENT_DIRECT_PATTERN = r'^\s*(\d+[.,]\d+)\s*%\s*(?:a\.?a\.?|a\.?m\.?|ao\s+ano|ao\s+m[êe]s)?'

# Indexadores internacionais (valores base aproximados)
INDEXER_BASE_VALUES.update({
    'SOFR': 0.0500,  # ~5,00% a.a. (média 2024)
    'LIBOR': 0.0550,  # ~5,50% a.a. (média 2024)
    'IGPM': 0.0462,  # Similar ao IPCA
    'IPC': 0.0462,   # Similar ao IPCA
    'POS_FIXADO': None,  # Precisa de indexador base
})

