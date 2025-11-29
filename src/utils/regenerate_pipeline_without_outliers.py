#!/usr/bin/env python3
"""
Regenera todo o pipeline de CSVs removendo empresas que são outliers.
"""
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, REPORTS_DIR
from utils.remove_outliers import identify_outliers_iqr
from utils.improve_kd_processing import main as improve_kd_main
from utils.calculate_weighted_kd_by_company import main as calculate_weighted_kd_main


def get_outlier_companies() -> set:
    """
    Retorna conjunto de empresas identificadas como outliers.
    
    Returns:
        Set com nomes das empresas outliers
    """
    outliers_file = REPORTS_DIR / "outliers_excluded_list.csv"
    if outliers_file.exists():
        df_outliers = pd.read_csv(outliers_file)
        return set(df_outliers['Empresa'].unique())
    return set()


def filter_final_calculated_by_outliers():
    """
    Filtra kd_final_calculados.csv removendo empresas outliers.
    """
    print("\n🔄 Filtrando kd_final_calculados.csv removendo outliers...")
    
    # Carrega dados finais
    input_file = CONSOLIDATED_PATH / "kd_final_calculados.csv"
    df_final = pd.read_csv(input_file)
    print(f"   Total antes: {len(df_final)} registros")
    
    # Obtém lista de empresas outliers
    outlier_companies = get_outlier_companies()
    print(f"   Empresas outliers a remover: {len(outlier_companies)}")
    
    if len(outlier_companies) > 0:
        # Filtra removendo empresas outliers
        df_filtered = df_final[~df_final['Empresa'].isin(outlier_companies)].copy()
        print(f"   Total depois: {len(df_filtered)} registros")
        print(f"   Registros removidos: {len(df_final) - len(df_filtered)}")
        
        # Salva CSV filtrado
        output_file = CONSOLIDATED_PATH / "kd_final_calculados_sem_outliers.csv"
        df_filtered.to_csv(output_file, index=False, encoding='utf-8')
        print(f"   ✅ CSV salvo em: {output_file}")
        
        return df_filtered
    else:
        print("   ⚠️  Nenhuma empresa outlier encontrada para remover")
        return df_final


def regenerate_weighted_kd_without_outliers():
    """
    Regenera kd_ponderado_por_empresa.csv usando apenas dados sem outliers.
    """
    print("\n🔄 Regenerando kd_ponderado_por_empresa.csv sem outliers...")
    
    # Usa o CSV final sem outliers como entrada
    input_file = CONSOLIDATED_PATH / "kd_final_calculados_sem_outliers.csv"
    
    if not input_file.exists():
        print(f"   ⚠️  Arquivo {input_file.name} não encontrado. Usando kd_final_calculados.csv e filtrando...")
        input_file = CONSOLIDATED_PATH / "kd_final_calculados.csv"
        df = pd.read_csv(input_file)
        outlier_companies = get_outlier_companies()
        if len(outlier_companies) > 0:
            df = df[~df['Empresa'].isin(outlier_companies)].copy()
            # Salva temporariamente
            temp_file = CONSOLIDATED_PATH / "kd_final_calculados_sem_outliers.csv"
            df.to_csv(temp_file, index=False, encoding='utf-8')
            input_file = temp_file
    
    # Importa e executa função de cálculo ponderado
    from utils.calculate_weighted_kd_by_company import calculate_weighted_kd
    
    # Carrega dados do CSV sem outliers
    df = pd.read_csv(input_file)
    print(f"   Registros carregados: {len(df)}")
    
    # Calcula Kd ponderado
    df_weighted = calculate_weighted_kd(df)
    
    # Salva como arquivo principal (substitui o original)
    output_file = CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv"
    
    # Salva como arquivo principal (substitui o original)
    output_file = CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv"
    df_weighted.to_csv(output_file, index=False, encoding='utf-8')
    print(f"   ✅ CSV salvo em: {output_file}")
    print(f"   Empresas no arquivo: {len(df_weighted)}")
    
    return df_weighted


def main():
    """Função principal que regenera todo o pipeline."""
    print("="*70)
    print("REGENERAÇÃO DO PIPELINE SEM OUTLIERS")
    print("="*70)
    
    # 1. Filtra kd_final_calculados.csv
    df_final_filtered = filter_final_calculated_by_outliers()
    
    # 2. Regenera kd_ponderado_por_empresa.csv
    df_weighted = regenerate_weighted_kd_without_outliers()
    
    print("\n" + "="*70)
    print("✅ PIPELINE REGENERADO SEM OUTLIERS!")
    print(f"   Empresas no arquivo final: {len(df_weighted)}")
    print("="*70)
    
    return df_weighted


if __name__ == "__main__":
    main()

