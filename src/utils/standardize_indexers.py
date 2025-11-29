"""
Funções para extração e padronização de indexadores de financiamentos.
"""
import re
import pandas as pd
from typing import Dict, Optional, Tuple
from .indexer_config import (
    INDEXER_PATTERNS, INDEXER_ALIASES, INDEXER_BASE_VALUES,
    SPREAD_PATTERNS, PERIOD_PATTERNS, DEFAULT_PERIOD,
    MISSING_INDICATORS
)


def normalize_text(text: str) -> str:
    """Normaliza texto para processamento."""
    if not text or pd.isna(text):
        return ""
    text = str(text).strip().upper()
    # Remove espaços múltiplos
    text = re.sub(r'\s+', ' ', text)
    return text


def extract_indexer_type(text: str) -> Optional[str]:
    """
    Identifica o tipo de indexador no texto.
    
    Args:
        text: Texto contendo o indexador
        
    Returns:
        Tipo padronizado do indexador ou None se não encontrado
    """
    if not text:
        return None
    
    normalized = normalize_text(text)
    
    # Verifica se é missing
    for missing in MISSING_INDICATORS:
        if missing.upper() in normalized or normalized.strip() == '':
            return None
    
    # Verifica padrões de indexadores (em ordem de especificidade)
    # SOFR e LIBOR primeiro (internacionais)
    if re.search(INDEXER_PATTERNS['SOFR'], normalized, re.IGNORECASE):
        return 'SOFR'
    if re.search(INDEXER_PATTERNS['LIBOR'], normalized, re.IGNORECASE):
        return 'LIBOR'
    
    # TLP/TJLP (verificar antes de IPCA pois pode ter "TLP_IPCA")
    if re.search(INDEXER_PATTERNS['TJLP'], normalized, re.IGNORECASE):
        return 'TLP'
    if re.search(INDEXER_PATTERNS['TLP'], normalized, re.IGNORECASE):
        return 'TLP'
    
    # IGPM e IPC (verificar antes de IPCA)
    if re.search(INDEXER_PATTERNS['IGPM'], normalized, re.IGNORECASE):
        return 'IGPM'
    if re.search(INDEXER_PATTERNS['IPC'], normalized, re.IGNORECASE):
        return 'IPC'
    
    # IPCA
    if re.search(INDEXER_PATTERNS['IPCA'], normalized, re.IGNORECASE):
        return 'IPCA'
    
    # DI (verificar antes de CDI pois pode ter "100% do DI")
    if re.search(INDEXER_PATTERNS['DI'], normalized, re.IGNORECASE):
        return 'DI'
    
    # CDI
    if re.search(INDEXER_PATTERNS['CDI'], normalized, re.IGNORECASE):
        return 'CDI'
    
    # SELIC
    if re.search(INDEXER_PATTERNS['SELIC'], normalized, re.IGNORECASE):
        return 'SELIC'
    
    # TR
    if re.search(INDEXER_PATTERNS['TR'], normalized, re.IGNORECASE):
        return 'TR'
    
    # Pós-fixado
    if re.search(INDEXER_PATTERNS['POS_FIXADO'], normalized, re.IGNORECASE):
        return 'POS_FIXADO'
    
    # Pré-fixado (verificar antes de percentual direto)
    if re.search(INDEXER_PATTERNS['PRE_FIXADO'], normalized, re.IGNORECASE):
        return 'PRE_FIXADO'
    
    # Percentual direto sem indexador (ex: "18,44% a.a.") - tratar como pré-fixado
    from .indexer_config import PERCENT_DIRECT_PATTERN
    if re.search(PERCENT_DIRECT_PATTERN, normalized, re.IGNORECASE):
        return 'PRE_FIXADO'
    
    return None


def extract_spread(text: str) -> Optional[float]:
    """
    Extrai o valor do spread do texto.
    
    Args:
        text: Texto contendo o spread
        
    Returns:
        Spread em decimal (ex: 0.015 para 1,5%) ou None se não encontrado
    """
    if not text:
        return None
    
    normalized = normalize_text(text)
    
    # Tenta cada padrão de spread
    for pattern in SPREAD_PATTERNS:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            try:
                # Converte vírgula para ponto
                value_str = match.group(1).replace(',', '.')
                spread = float(value_str) / 100  # Converte % para decimal
                
                # Verifica se é spread negativo (padrão com -)
                if re.search(r'[-\u2013\u2014]\s*' + re.escape(value_str), normalized, re.IGNORECASE):
                    spread = -spread
                
                return spread
            except (ValueError, IndexError):
                continue
    
    # Se não encontrou spread explícito, verifica se é pré-fixado com taxa
    # Ex: "Pré-fixado 6,94% a.a." ou "Pré 9,9%"
    pre_fixado_patterns = [
        r'(?:pr[ée][\s-]?fixado|prefixado|pr[ée])\s*(\d+[.,]\d+)\s*%',
        r'fixo\s*(?:a\s+)?(\d+[.,]\d+)\s*%',
    ]
    for pattern in pre_fixado_patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            try:
                value_str = match.group(1).replace(',', '.')
                spread = float(value_str) / 100
                return spread
            except (ValueError, IndexError):
                continue
    
    # Tenta extrair percentual direto (para pré-fixados sem palavra-chave)
    # Ex: "18,44% a.a."
    percent_direct = re.search(r'^(\d+[.,]\d+)\s*%\s*(?:a\.?a\.?|a\.?m\.?)?', normalized, re.IGNORECASE)
    if percent_direct:
        try:
            value_str = percent_direct.group(1).replace(',', '.')
            spread = float(value_str) / 100
            return spread
        except (ValueError, IndexError):
            pass
    
    return None


def extract_period(text: str) -> str:
    """
    Identifica o período da taxa (anual ou mensal).
    
    Args:
        text: Texto contendo informação do período
        
    Returns:
        'a.a.' para anual, 'a.m.' para mensal, ou DEFAULT_PERIOD
    """
    if not text:
        return DEFAULT_PERIOD
    
    normalized = normalize_text(text)
    
    # Verifica padrões mensais
    for pattern in PERIOD_PATTERNS['a.m.']:
        if re.search(pattern, normalized, re.IGNORECASE):
            return 'a.m.'
    
    # Verifica padrões anuais
    for pattern in PERIOD_PATTERNS['a.a.']:
        if re.search(pattern, normalized, re.IGNORECASE):
            return 'a.a.'
    
    # Se não encontrou, assume anual
    return DEFAULT_PERIOD


def convert_to_annual_rate(monthly_rate: float) -> float:
    """
    Converte taxa mensal para anual usando capitalização composta.
    
    Args:
        monthly_rate: Taxa mensal em decimal (ex: 0.01 para 1%)
        
    Returns:
        Taxa anual em decimal
    """
    return (1 + monthly_rate) ** 12 - 1


def standardize_indexer(indexer_text: str) -> Dict[str, any]:
    """
    Padroniza um indexador extraindo tipo, spread e período.
    
    Args:
        indexer_text: Texto do indexador original
        
    Returns:
        Dicionário com:
        - indexer_type: Tipo padronizado (CDI, TLP, IPCA, etc.) ou None
        - spread: Spread em decimal ou None
        - period: 'a.a.' ou 'a.m.'
        - original_text: Texto original
        - is_prefixed: True se é pré-fixado
        - observations: Lista de observações sobre o processamento
    """
    result = {
        'indexer_type': None,
        'spread': None,
        'period': DEFAULT_PERIOD,
        'original_text': indexer_text,
        'is_prefixed': False,
        'observations': []
    }
    
    if not indexer_text or pd.isna(indexer_text):
        result['observations'].append('Indexador vazio')
        return result
    
    # Extrai tipo
    indexer_type = extract_indexer_type(indexer_text)
    result['indexer_type'] = indexer_type
    
    if indexer_type is None:
        result['observations'].append('Tipo de indexador não identificado')
        return result
    
    # Verifica se é pré-fixado
    if indexer_type == 'PRE_FIXADO':
        result['is_prefixed'] = True
        # Para pré-fixado, o spread é na verdade a taxa total
        spread = extract_spread(indexer_text)
        if spread is not None:
            result['spread'] = spread
            result['observations'].append('Pré-fixado: spread contém taxa total')
        else:
            result['observations'].append('Pré-fixado sem taxa identificada')
        return result
    
    # Extrai spread
    spread = extract_spread(indexer_text)
    result['spread'] = spread
    
    if spread is None:
        result['observations'].append('Spread não identificado, assumindo 0')
        result['spread'] = 0.0
    
    # Extrai período
    period = extract_period(indexer_text)
    result['period'] = period
    
    # Se spread é mensal, converte para anual
    if period == 'a.m.' and spread is not None:
        original_spread = spread
        spread = convert_to_annual_rate(spread)
        result['spread'] = spread
        result['observations'].append(f'Spread convertido de mensal ({original_spread*100:.2f}%) para anual ({spread*100:.2f}%)')
    
    return result

