"""
Funções para cálculo de Kd (custo de capital de dívida) baseado em indexadores.
"""
from typing import Optional, Dict, Tuple
from .indexer_config import INDEXER_BASE_VALUES, MIN_Kd, MAX_Kd


def calculate_kd(indexer_type: Optional[str], spread: Optional[float], 
                 period: str = 'a.a.', is_prefixed: bool = False) -> Dict[str, any]:
    """
    Calcula Kd baseado no tipo de indexador e spread.
    
    Args:
        indexer_type: Tipo do indexador (CDI, TLP, IPCA, PRE_FIXADO, etc.)
        spread: Spread em decimal (ex: 0.015 para 1,5%)
        period: Período da taxa ('a.a.' ou 'a.m.')
        is_prefixed: True se é pré-fixado (spread já é o Kd)
        
    Returns:
        Dicionário com:
        - kd_decimal: Kd em decimal (ex: 0.15 para 15%)
        - kd_percentual: Kd em percentual (ex: 15.0)
        - base_value: Valor base do indexador usado
        - spread_used: Spread usado no cálculo
        - is_valid: Se o Kd está em range válido
        - observations: Lista de observações
    """
    result = {
        'kd_decimal': None,
        'kd_percentual': None,
        'base_value': None,
        'spread_used': spread if spread is not None else 0.0,
        'is_valid': False,
        'observations': []
    }
    
    # Caso pré-fixado: spread já é o Kd
    if is_prefixed:
        if spread is not None:
            result['kd_decimal'] = spread
            result['kd_percentual'] = spread * 100
            result['base_value'] = 0.0
            result['spread_used'] = spread
            result['observations'].append('Pré-fixado: taxa é o Kd final')
        else:
            result['observations'].append('Pré-fixado sem taxa identificada')
            return result
    
    # Caso indexador não identificado
    if indexer_type is None:
        result['observations'].append('Indexador não identificado, não é possível calcular Kd')
        return result
    
    # Obtém valor base do indexador
    base_value = INDEXER_BASE_VALUES.get(indexer_type)
    
    if base_value is None:
        result['observations'].append(f'Valor base não disponível para {indexer_type}')
        return result
    
    result['base_value'] = base_value
    
    # Calcula Kd = Base + Spread
    spread_used = spread if spread is not None else 0.0
    result['spread_used'] = spread_used
    
    kd_decimal = base_value + spread_used
    result['kd_decimal'] = kd_decimal
    result['kd_percentual'] = kd_decimal * 100
    
    # Valida range
    if MIN_Kd <= kd_decimal <= MAX_Kd:
        result['is_valid'] = True
    else:
        result['is_valid'] = False
        result['observations'].append(f'Kd fora do range esperado ({MIN_Kd*100:.1f}% - {MAX_Kd*100:.1f}%)')
    
    # Observações adicionais
    if spread is None:
        result['observations'].append(f'Spread não encontrado, assumindo 0% (Kd = {indexer_type} base)')
    
    return result


def validate_kd(kd_decimal: float) -> Tuple[bool, str]:
    """
    Valida se o Kd está em range razoável.
    
    Args:
        kd_decimal: Kd em decimal
        
    Returns:
        Tupla (is_valid, message)
    """
    if kd_decimal < MIN_Kd:
        return False, f'Kd muito baixo ({kd_decimal*100:.2f}% < {MIN_Kd*100:.0f}%)'
    if kd_decimal > MAX_Kd:
        return False, f'Kd muito alto ({kd_decimal*100:.2f}% > {MAX_Kd*100:.0f}%)'
    return True, 'Kd válido'

