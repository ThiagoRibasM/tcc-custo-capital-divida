#!/usr/bin/env python3
"""
Script para identificar e remover outliers usando método IQR.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, REPORTS_DIR, PROJECT_ROOT


def identify_outliers_iqr(df: pd.DataFrame, column: str = 'Kd_Ponderado') -> pd.DataFrame:
    """
    Identifica outliers usando método IQR.
    
    Args:
        df: DataFrame com dados
        column: Coluna para análise de outliers
        
    Returns:
        DataFrame com coluna 'Is_Outlier' indicando outliers
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    df_result = df.copy()
    df_result['Is_Outlier'] = (df[column] < lower_bound) | (df[column] > upper_bound)
    df_result['IQR_Lower_Bound'] = lower_bound
    df_result['IQR_Upper_Bound'] = upper_bound
    df_result['IQR_Q1'] = Q1
    df_result['IQR_Q3'] = Q3
    df_result['IQR'] = IQR
    
    return df_result, lower_bound, upper_bound, Q1, Q3, IQR


def document_excluded_companies(df_with_outliers: pd.DataFrame, 
                                lower_bound: float, 
                                upper_bound: float,
                                Q1: float,
                                Q3: float,
                                IQR: float) -> Path:
    """
    Documenta empresas excluídas por serem outliers.
    
    Args:
        df_with_outliers: DataFrame com flag de outliers
        lower_bound: Limite inferior IQR
        upper_bound: Limite superior IQR
        Q1, Q3, IQR: Estatísticas IQR
        
    Returns:
        Path do arquivo de documentação criado
    """
    outliers_df = df_with_outliers[df_with_outliers['Is_Outlier'] == True].copy()
    
    report = []
    report.append("# Documentação de Empresas Excluídas por Outliers")
    report.append(f"\n**Data:** {datetime.now().strftime('%d de %B de %Y')}")
    report.append(f"\n---\n")
    
    # Metodologia
    report.append("## Metodologia de Identificação de Outliers\n")
    report.append("Foi utilizado o método **IQR (Interquartile Range)** para identificar outliers:\n")
    report.append(f"- **Q1 (25%):** {Q1:.2f}%")
    report.append(f"- **Q3 (75%):** {Q3:.2f}%")
    report.append(f"- **IQR:** {IQR:.2f}%")
    report.append(f"- **Limite Inferior:** Q1 - 1.5 × IQR = {lower_bound:.2f}%")
    report.append(f"- **Limite Superior:** Q3 + 1.5 × IQR = {upper_bound:.2f}%")
    report.append(f"\n**Critério:** Empresas com Kd_Ponderado < {lower_bound:.2f}% OU > {upper_bound:.2f}% foram consideradas outliers.\n")
    
    # Estatísticas
    total = len(df_with_outliers)
    outliers_count = len(outliers_df)
    normal_count = total - outliers_count
    
    report.append("## Estatísticas de Exclusão\n")
    report.append(f"- **Total de empresas:** {total}")
    report.append(f"- **Empresas excluídas (outliers):** {outliers_count} ({outliers_count/total*100:.1f}%)")
    report.append(f"- **Empresas mantidas:** {normal_count} ({normal_count/total*100:.1f}%)\n")
    
    # Lista de empresas excluídas
    report.append("## Lista de Empresas Excluídas\n")
    
    if len(outliers_df) > 0:
        # Ordena por Kd_Ponderado (decrescente)
        outliers_df_sorted = outliers_df.sort_values('Kd_Ponderado', ascending=False)
        
        report.append("| # | Empresa | Kd Ponderado (%) | Valor Consolidado Médio (R$) | Total Financiamentos | Justificativa |")
        report.append("|---|---------|-------------------|-------------------------------|---------------------|---------------|")
        
        for idx, (_, row) in enumerate(outliers_df_sorted.iterrows(), 1):
            empresa = str(row['Empresa'])[:50]
            kd = row['Kd_Ponderado']
            valor = row['Valor_Consolidado_Media']
            financ = int(row['Total_Financiamentos'])
            
            if kd > upper_bound:
                justificativa = f"Kd muito alto (> {upper_bound:.2f}%)"
            else:
                justificativa = f"Kd muito baixo (< {lower_bound:.2f}%)"
            
            report.append(f"| {idx} | {empresa} | {kd:.2f} | {valor:,.2f} | {financ} | {justificativa} |")
        
        # Análise dos outliers
        report.append("\n### Análise dos Outliers\n")
        
        outliers_high = outliers_df[outliers_df['Kd_Ponderado'] > upper_bound]
        outliers_low = outliers_df[outliers_df['Kd_Ponderado'] < lower_bound]
        
        report.append(f"#### Outliers com Kd Muito Alto (> {upper_bound:.2f}%)\n")
        report.append(f"**Quantidade:** {len(outliers_high)} empresas\n")
        if len(outliers_high) > 0:
            report.append("| Empresa | Kd (%) | Valor Médio (R$) |")
            report.append("|---------|--------|------------------|")
            for _, row in outliers_high.sort_values('Kd_Ponderado', ascending=False).iterrows():
                report.append(f"| {str(row['Empresa'])[:50]} | {row['Kd_Ponderado']:.2f} | {row['Valor_Consolidado_Media']:,.2f} |")
        
        report.append(f"\n#### Outliers com Kd Muito Baixo (< {lower_bound:.2f}%)\n")
        report.append(f"**Quantidade:** {len(outliers_low)} empresas\n")
        if len(outliers_low) > 0:
            report.append("| Empresa | Kd (%) | Valor Médio (R$) |")
            report.append("|---------|--------|------------------|")
            for _, row in outliers_low.sort_values('Kd_Ponderado', ascending=True).iterrows():
                report.append(f"| {str(row['Empresa'])[:50]} | {row['Kd_Ponderado']:.2f} | {row['Valor_Consolidado_Media']:,.2f} |")
    else:
        report.append("Nenhuma empresa foi identificada como outlier.\n")
    
    # Comparação antes/depois
    report.append("\n## Comparação: Antes vs Depois da Remoção\n")
    
    df_normal = df_with_outliers[df_with_outliers['Is_Outlier'] == False]
    
    report.append("### Estatísticas de Kd Ponderado\n")
    report.append("| Estatística | Antes (com outliers) | Depois (sem outliers) | Diferença |")
    report.append("|------------|---------------------|----------------------|-----------|")
    
    stats_before = df_with_outliers['Kd_Ponderado'].describe()
    stats_after = df_normal['Kd_Ponderado'].describe()
    
    for stat in ['mean', '50%', 'std', 'min', 'max']:
        before_val = stats_before[stat]
        after_val = stats_after[stat]
        diff = after_val - before_val
        diff_pct = (diff / before_val) * 100 if before_val != 0 else 0
        
        stat_name = {'mean': 'Média', '50%': 'Mediana', 'std': 'Desvio Padrão', 
                    'min': 'Mínimo', 'max': 'Máximo'}[stat]
        report.append(f"| {stat_name} | {before_val:.2f}% | {after_val:.2f}% | {diff:+.2f}% ({diff_pct:+.1f}%) |")
    
    report.append("\n---")
    report.append(f"\n*Documento gerado automaticamente pelo script `{Path(__file__).name}`*")
    
    # Salva documento
    output_path = REPORTS_DIR / "outliers_excluded.md"
    output_path.write_text("\n".join(report), encoding='utf-8')
    print(f"✅ Documentação de outliers salva em: {output_path}")
    
    return output_path


def main():
    """Função principal."""
    print("="*70)
    print("IDENTIFICAÇÃO E REMOÇÃO DE OUTLIERS")
    print("="*70)
    
    # Carrega dados
    input_file = CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv"
    print(f"\n📖 Carregando dados de: {input_file.name}")
    df = pd.read_csv(input_file)
    print(f"   ✅ {len(df)} empresas carregadas")
    
    # Identifica outliers
    print(f"\n🔍 Identificando outliers usando método IQR...")
    df_with_outliers, lower_bound, upper_bound, Q1, Q3, IQR = identify_outliers_iqr(df, 'Kd_Ponderado')
    
    outliers_count = df_with_outliers['Is_Outlier'].sum()
    normal_count = len(df_with_outliers) - outliers_count
    
    print(f"   Q1: {Q1:.2f}%")
    print(f"   Q3: {Q3:.2f}%")
    print(f"   IQR: {IQR:.2f}%")
    print(f"   Limite inferior: {lower_bound:.2f}%")
    print(f"   Limite superior: {upper_bound:.2f}%")
    print(f"   Outliers identificados: {outliers_count} ({outliers_count/len(df)*100:.1f}%)")
    print(f"   Empresas mantidas: {normal_count} ({normal_count/len(df)*100:.1f}%)")
    
    # Documenta empresas excluídas
    print(f"\n📝 Documentando empresas excluídas...")
    doc_path = document_excluded_companies(df_with_outliers, lower_bound, upper_bound, Q1, Q3, IQR)
    
    # Remove outliers
    df_without_outliers = df_with_outliers[df_with_outliers['Is_Outlier'] == False].copy()
    df_without_outliers = df_without_outliers.drop(columns=['Is_Outlier', 'IQR_Lower_Bound', 
                                                           'IQR_Upper_Bound', 'IQR_Q1', 'IQR_Q3', 'IQR'])
    
    # Salva CSV sem outliers
    output_file = CONSOLIDATED_PATH / "kd_ponderado_por_empresa_sem_outliers.csv"
    df_without_outliers.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 CSV sem outliers salvo em: {output_file}")
    print(f"   Empresas no arquivo: {len(df_without_outliers)}")
    
    # Salva também lista de empresas excluídas em CSV para referência
    outliers_csv = REPORTS_DIR / "outliers_excluded_list.csv"
    df_outliers_only = df_with_outliers[df_with_outliers['Is_Outlier'] == True][
        ['Empresa', 'Kd_Ponderado', 'Valor_Consolidado_Media', 'Total_Financiamentos']
    ].copy()
    df_outliers_only.to_csv(outliers_csv, index=False, encoding='utf-8')
    print(f"💾 Lista de outliers em CSV: {outliers_csv}")
    
    return df_without_outliers, df_outliers_only


if __name__ == "__main__":
    main()

