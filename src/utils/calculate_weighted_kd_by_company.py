#!/usr/bin/env python3
"""
Calcula Kd ponderado por empresa e gera CSV agregado.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH


def calculate_weighted_kd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula Kd ponderado por empresa e outras métricas agregadas.
    
    Args:
        df: DataFrame com dados de Kd por financiamento
        
    Returns:
        DataFrame agregado por empresa
    """
    print("🔄 Calculando Kd ponderado por empresa...")
    
    # Garante que temos as colunas necessárias
    required_cols = ['Empresa', 'Kd_Percentual', 'Valor_Consolidado_2024']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas faltando: {missing_cols}")
    
    # Remove registros sem Kd ou valor consolidado
    df_clean = df[
        df['Kd_Percentual'].notna() & 
        df['Valor_Consolidado_2024'].notna() & 
        (df['Valor_Consolidado_2024'] > 0)
    ].copy()
    
    print(f"   Registros válidos: {len(df_clean)} de {len(df)}")
    
    # Agrupa por empresa
    grouped = df_clean.groupby('Empresa')
    
    results = []
    
    for empresa, group_df in grouped:
        # Kd ponderado: Σ(Kd_i × Valor_i) / Σ(Valor_i)
        kd_weighted = np.average(
            group_df['Kd_Percentual'], 
            weights=group_df['Valor_Consolidado_2024']
        )
        
        # Média do valor consolidado
        valor_medio = group_df['Valor_Consolidado_2024'].mean()
        
        # Total de financiamentos
        total_financiamentos = len(group_df)
        
        # Valor consolidado total
        valor_total = group_df['Valor_Consolidado_2024'].sum()
        
        # Kd médio simples (sem ponderação)
        kd_medio_simples = group_df['Kd_Percentual'].mean()
        
        # Desvio padrão do Kd
        kd_desvio_padrao = group_df['Kd_Percentual'].std()
        
        # Kd mínimo e máximo
        kd_min = group_df['Kd_Percentual'].min()
        kd_max = group_df['Kd_Percentual'].max()
        
        # Quantidade de indexadores únicos
        indexadores_unicos = group_df['Indexador_Processado'].nunique()
        
        # Quantidade de tipos de financiamento únicos
        tipos_unicos = group_df['Tipo_Financiamento'].nunique()
        
        # Lista de indexadores usados (para referência)
        indexadores_lista = ', '.join(group_df['Indexador_Processado'].unique())
        
        results.append({
            'Empresa': empresa,
            'Kd_Ponderado': kd_weighted,
            'Valor_Consolidado_Media': valor_medio,
            'Total_Financiamentos': total_financiamentos,
            'Valor_Consolidado_Total': valor_total,
            'Kd_Medio_Simples': kd_medio_simples,
            'Kd_Desvio_Padrao': kd_desvio_padrao,
            'Kd_Min': kd_min,
            'Kd_Max': kd_max,
            'Indexadores_Unicos': indexadores_unicos,
            'Tipos_Financiamento_Unicos': tipos_unicos,
            'Indexadores_Usados': indexadores_lista
        })
    
    df_result = pd.DataFrame(results)
    
    # Ordena por Kd ponderado (decrescente)
    df_result = df_result.sort_values('Kd_Ponderado', ascending=False).reset_index(drop=True)
    
    print(f"✅ {len(df_result)} empresas processadas")
    
    return df_result


def main():
    """Função principal."""
    # Lê dados finais
    input_file = CONSOLIDATED_PATH / "kd_final_calculados.csv"
    
    if not input_file.exists():
        print(f"❌ Erro: Arquivo '{input_file}' não encontrado.")
        sys.exit(1)
    
    print(f"📖 Carregando dados de: {input_file.name}")
    df = pd.read_csv(input_file)
    print(f"   ✅ {len(df)} registros carregados")
    
    # Calcula Kd ponderado por empresa
    df_aggregated = calculate_weighted_kd(df)
    
    # Salva CSV
    output_file = CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv"
    df_aggregated.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 CSV salvo em: {output_file}")
    
    # Estatísticas
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total de empresas: {len(df_aggregated)}")
    print(f"   Kd ponderado médio: {df_aggregated['Kd_Ponderado'].mean():.2f}%")
    print(f"   Kd ponderado mediano: {df_aggregated['Kd_Ponderado'].median():.2f}%")
    print(f"   Kd ponderado mínimo: {df_aggregated['Kd_Ponderado'].min():.2f}%")
    print(f"   Kd ponderado máximo: {df_aggregated['Kd_Ponderado'].max():.2f}%")
    print(f"   Valor consolidado total médio: R$ {df_aggregated['Valor_Consolidado_Media'].mean():,.2f}")
    print(f"   Total de financiamentos médio: {df_aggregated['Total_Financiamentos'].mean():.1f}")
    
    # Top 10 empresas por Kd ponderado
    print(f"\n📈 TOP 10 EMPRESAS POR Kd PONDERADO:")
    top10 = df_aggregated.head(10)
    for idx, row in top10.iterrows():
        print(f"   {idx+1:2d}. {row['Empresa'][:50]:<50} Kd: {row['Kd_Ponderado']:6.2f}% | Financ: {row['Total_Financiamentos']:2d}")
    
    return df_aggregated


if __name__ == "__main__":
    main()

