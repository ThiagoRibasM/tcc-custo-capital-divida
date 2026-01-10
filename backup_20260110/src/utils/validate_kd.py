"""
Módulo para validação e tratamento de casos extremos de Kd.
"""
import pandas as pd
from typing import Dict, List, Tuple
from .indexer_config import MIN_Kd, MAX_Kd
from math import pow


def identify_extreme_kd(kd_percentual: float, indexer_type: str, spread: float, 
                        period: str, is_prefixed: bool) -> Dict[str, any]:
    """
    Identifica se Kd é extremo e sugere correções.
    
    Args:
        kd_percentual: Kd em percentual
        indexer_type: Tipo do indexador
        spread: Spread usado
        period: Período original
        is_prefixed: Se é pré-fixado
        
    Returns:
        Dicionário com flags e sugestões
    """
    result = {
        'is_extreme_high': False,
        'is_extreme_low': False,
        'suspected_error': False,
        'suggested_correction': None,
        'reason': '',
        'needs_manual_review': False
    }
    
    if pd.isna(kd_percentual):
        return result
    
    kd_decimal = kd_percentual / 100
    
    # Kd muito alto (> 30%)
    if kd_decimal > 0.30:
        result['is_extreme_high'] = True
        result['needs_manual_review'] = True
        
        # Verifica possíveis causas
        if period == 'a.m.' and not is_prefixed:
            result['suspected_error'] = True
            result['reason'] = 'Possível erro na conversão de taxa mensal para anual'
            # Se spread foi convertido de mensal, pode estar duplicado
            spread_decimal = spread if spread is not None else 0
            if spread_decimal > 0.5:  # Spread > 50% anual é suspeito
                result['suggested_correction'] = 'Reverificar conversão mensal para anual'
        elif spread > 0.20:  # Spread > 20%
            result['reason'] = 'Spread muito alto, verificar se não é erro de parsing'
            result['suggested_correction'] = 'Validar spread extraído'
        else:
            result['reason'] = 'Kd muito alto, pode ser correto mas necessita validação'
    
    # Kd muito baixo (< 5%)
    elif kd_decimal < 0.05:
        result['is_extreme_low'] = True
        
        # Verifica possíveis causas
        if indexer_type == 'TR':
            result['reason'] = 'TR tem valor base muito baixo (0,01%), Kd baixo é esperado'
            result['needs_manual_review'] = False  # TR baixo é normal
        elif indexer_type == 'IPCA' and spread is not None and spread < 0:
            result['reason'] = 'Spread negativo aplicado, verificar se está correto'
            result['needs_manual_review'] = True
        elif is_prefixed and kd_decimal < 0.03:
            result['reason'] = 'Pré-fixado muito baixo, pode ser taxa internacional (USD, EUR)'
            result['needs_manual_review'] = True
        else:
            result['reason'] = 'Kd muito baixo, verificar valores base do indexador'
            result['needs_manual_review'] = True
    
    # Kd fora do range válido mas não extremo
    elif kd_decimal < MIN_Kd or kd_decimal > MAX_Kd:
        result['needs_manual_review'] = True
        result['reason'] = f'Kd fora do range esperado ({MIN_Kd*100:.0f}% - {MAX_Kd*100:.0f}%)'
    
    return result


def validate_kd_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida Kd em lote e adiciona flags.
    
    Args:
        df: DataFrame com colunas Kd_Percentual, Indexador_Processado, Spread_Percentual, etc.
        
    Returns:
        DataFrame com colunas adicionais de validação
    """
    df_validated = df.copy()
    
    # Adiciona colunas de validação
    df_validated['Kd_Extremo_Alto'] = False
    df_validated['Kd_Extremo_Baixo'] = False
    df_validated['Kd_Suspeito_Erro'] = False
    df_validated['Kd_Revisao_Manual'] = False
    df_validated['Kd_Observacao_Validacao'] = ''
    
    for idx, row in df_validated.iterrows():
        if pd.isna(row.get('Kd_Percentual')):
            continue
        
        validation = identify_extreme_kd(
            kd_percentual=row.get('Kd_Percentual'),
            indexer_type=row.get('Indexador_Processado'),
            spread=row.get('Spread_Percentual') / 100 if pd.notna(row.get('Spread_Percentual')) else None,
            period=row.get('Periodo_Original', 'a.a.'),
            is_prefixed=row.get('Indexador_Processado') == 'PRE_FIXADO'
        )
        
        df_validated.at[idx, 'Kd_Extremo_Alto'] = validation['is_extreme_high']
        df_validated.at[idx, 'Kd_Extremo_Baixo'] = validation['is_extreme_low']
        df_validated.at[idx, 'Kd_Suspeito_Erro'] = validation['suspected_error']
        df_validated.at[idx, 'Kd_Revisao_Manual'] = validation['needs_manual_review']
        df_validated.at[idx, 'Kd_Observacao_Validacao'] = validation['reason']
    
    return df_validated


def get_extreme_cases_for_review(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna casos extremos que precisam revisão manual.
    
    Args:
        df: DataFrame validado
        
    Returns:
        DataFrame filtrado com casos para revisão
    """
    # Filtra casos que precisam revisão
    review_cases = df[
        (df['Kd_Revisao_Manual'] == True) |
        (df['Kd_Extremo_Alto'] == True) |
        (df['Kd_Extremo_Baixo'] == True)
    ].copy()
    
    return review_cases

