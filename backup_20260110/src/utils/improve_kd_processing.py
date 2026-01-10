#!/usr/bin/env python3
"""
Script para aplicar melhorias na padronização de indexadores e validação de Kd.
"""
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH
from utils.process_kd_pipeline import process_kd_pipeline
from utils.validate_kd import validate_kd_batch, get_extreme_cases_for_review


def filter_calculated_kd_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra registros que tenham Kd calculado e valor consolidado 2024 preenchido.
    
    Args:
        df: DataFrame com dados processados
        
    Returns:
        DataFrame filtrado com apenas registros válidos
    """
    # Filtra por Kd calculado (qualquer valor, não precisa estar no range válido)
    has_kd = df['Kd_Decimal'].notna() | df['Kd_Percentual'].notna()
    
    # Filtra por valor consolidado preenchido e > 0
    has_consolidado = df['Valor_Consolidado_2024'].notna() & (df['Valor_Consolidado_2024'] > 0)
    
    # Aplica ambos os filtros
    df_filtered = df[has_kd & has_consolidado].copy()
    
    return df_filtered


def main():
    """Aplica melhorias e validação."""
    input_file = CONSOLIDATED_PATH / "emp_e_fin_novo_mercado_20250920.xlsx"
    output_file = CONSOLIDATED_PATH / "kd_calculated_improved.csv"
    
    print("="*70)
    print("MELHORIAS NA PADRONIZAÇÃO DE INDEXADORES E VALIDAÇÃO DE Kd")
    print("="*70)
    
    # Processa com melhorias
    df_processed = process_kd_pipeline(input_file, output_file)
    
    # Aplica validação
    print(f"\n🔍 Aplicando validação de casos extremos...")
    df_validated = validate_kd_batch(df_processed)
    
    # Estatísticas de validação
    extreme_high = df_validated['Kd_Extremo_Alto'].sum()
    extreme_low = df_validated['Kd_Extremo_Baixo'].sum()
    needs_review = df_validated['Kd_Revisao_Manual'].sum()
    
    print(f"   Kd extremo alto (>30%): {extreme_high}")
    print(f"   Kd extremo baixo (<5%): {extreme_low}")
    print(f"   Requer revisão manual: {needs_review}")
    
    # Salva versão validada
    df_validated.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 CSV melhorado salvo em: {output_file}")
    
    # Comparação com versão anterior
    print(f"\n📈 COMPARAÇÃO:")
    total = len(df_validated)
    identified = (df_validated['Indexador_Processado'] != 'NÃO_IDENTIFICADO').sum()
    identified_pct = (identified / total) * 100
    print(f"   Taxa de identificação: {identified_pct:.1f}% ({identified}/{total})")
    
    kd_calculated = df_validated['Kd_Decimal'].notna().sum()
    kd_valid = df_validated['Kd_Valido'].sum()
    print(f"   Kd calculado: {kd_calculated} ({kd_calculated/total:.1%})")
    print(f"   Kd válido: {kd_valid} ({kd_valid/total:.1%})")
    
    # Casos para revisão manual
    review_cases = get_extreme_cases_for_review(df_validated)
    if len(review_cases) > 0:
        review_file = CONSOLIDATED_PATH / "kd_manual_review.csv"
        review_cases.to_csv(review_file, index=False, encoding='utf-8')
        print(f"\n📋 {len(review_cases)} casos para revisão manual salvos em: {review_file}")
    
    # Filtra registros com Kd calculado e valor consolidado
    print(f"\n🔍 Filtrando registros com Kd calculado e valor consolidado 2024...")
    df_final = filter_calculated_kd_records(df_validated)
    
    total_before = len(df_validated)
    total_after = len(df_final)
    removed = total_before - total_after
    
    print(f"   Total antes do filtro: {total_before}")
    print(f"   Total após filtro: {total_after}")
    print(f"   Registros removidos: {removed}")
    
    # Salva tabela final
    final_file = CONSOLIDATED_PATH / "kd_final_calculados.csv"
    df_final.to_csv(final_file, index=False, encoding='utf-8')
    print(f"\n💾 Tabela final salva em: {final_file}")
    print(f"   Registros na tabela final: {len(df_final)}")
    
    return df_validated


if __name__ == "__main__":
    main()

