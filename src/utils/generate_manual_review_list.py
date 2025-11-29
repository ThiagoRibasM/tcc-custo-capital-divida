#!/usr/bin/env python3
"""
Gera lista de indexadores não identificados para revisão manual.
"""
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, PROJECT_ROOT

DOCS_DIR = PROJECT_ROOT / "docs"


def generate_manual_review_list():
    """Gera lista de indexadores para revisão manual."""
    
    # Lê dados melhorados
    df_improved = pd.read_csv(CONSOLIDATED_PATH / "kd_calculated_improved.csv")
    
    # Lê dados originais
    df_orig = pd.read_excel(CONSOLIDATED_PATH / "emp_e_fin_novo_mercado_20250920.xlsx")
    
    # Merge para pegar indexadores originais
    df_merged = df_improved.copy()
    df_merged['indexador_original'] = df_orig['indexador'].values
    
    # Filtra não identificados
    nao_id = df_merged[df_merged['Indexador_Processado'] == 'NÃO_IDENTIFICADO'].copy()
    
    # Filtra casos extremos (já tem indexador_original do merge anterior)
    extreme_cases = df_merged[
        (df_merged['Kd_Revisao_Manual'] == True) |
        (df_merged['Kd_Extremo_Alto'] == True) |
        (df_merged['Kd_Extremo_Baixo'] == True)
    ].copy()
    
    report_content = []
    report_content.append("# Lista de Revisão Manual - Indexadores e Casos Extremos")
    report_content.append(f"\n**Data:** {datetime.now().strftime('%d de %B de %Y')}")
    report_content.append(f"\n---\n")
    
    # 1. Indexadores Não Identificados
    report_content.append("## 1. Indexadores Não Identificados\n")
    report_content.append(f"\nTotal: {len(nao_id)} registros\n")
    
    if len(nao_id) > 0:
        # Top 50 mais frequentes
        top_nao_id = nao_id['indexador_original'].value_counts().head(50)
        
        report_content.append("### Top 50 Indexadores Não Identificados Mais Frequentes\n")
        report_content.append("\n| # | Indexador Original | Frequência |")
        report_content.append("|---|-------------------|------------|")
        for idx, (val, count) in enumerate(top_nao_id.items(), 1):
            val_str = str(val)[:70] if pd.notna(val) else "NaN"
            report_content.append(f"| {idx} | {val_str} | {count} |")
    
    # 2. Casos Extremos de Kd
    report_content.append("\n## 2. Casos Extremos de Kd para Validação\n")
    report_content.append(f"\nTotal: {len(extreme_cases)} registros\n")
    
    if len(extreme_cases) > 0:
        # Agrupa por tipo de extremo
        report_content.append("### 2.1 Kd Extremo Alto (>30%)\n")
        df_high = extreme_cases[extreme_cases['Kd_Extremo_Alto'] == True].head(20)
        report_content.append("\n| Empresa | Indexador | Kd (%) | Spread (%) | Observação |")
        report_content.append("|---------|-----------|--------|------------|------------|")
        for _, row in df_high.iterrows():
            empresa = str(row['Empresa'])[:30]
            indexador = str(row['Indexador_Processado'])
            kd = f"{row['Kd_Percentual']:.2f}" if pd.notna(row['Kd_Percentual']) else "N/A"
            spread = f"{row['Spread_Percentual']:.2f}" if pd.notna(row['Spread_Percentual']) else "N/A"
            obs = str(row['Kd_Observacao_Validacao'])[:50] if pd.notna(row['Kd_Observacao_Validacao']) else ""
            report_content.append(f"| {empresa} | {indexador} | {kd} | {spread} | {obs} |")
        
        report_content.append("\n### 2.2 Kd Extremo Baixo (<5%)\n")
        df_low = extreme_cases[extreme_cases['Kd_Extremo_Baixo'] == True].head(20)
        report_content.append("\n| Empresa | Indexador | Kd (%) | Spread (%) | Observação |")
        report_content.append("|---------|-----------|--------|------------|------------|")
        for _, row in df_low.iterrows():
            empresa = str(row['Empresa'])[:30]
            indexador = str(row['Indexador_Processado'])
            kd = f"{row['Kd_Percentual']:.2f}" if pd.notna(row['Kd_Percentual']) else "N/A"
            spread = f"{row['Spread_Percentual']:.2f}" if pd.notna(row['Spread_Percentual']) else "N/A"
            obs = str(row['Kd_Observacao_Validacao'])[:50] if pd.notna(row['Kd_Observacao_Validacao']) else ""
            report_content.append(f"| {empresa} | {indexador} | {kd} | {spread} | {obs} |")
    
    # 3. Sugestões de Tratamento
    report_content.append("\n## 3. Sugestões de Tratamento\n")
    report_content.append("\n### 3.1 Padrões Comuns nos Não Identificados\n")
    report_content.append("\n1. **Percentuais diretos sem indexador**: Tratar como pré-fixado")
    report_content.append("2. **Variação cambial**: Adicionar tratamento específico")
    report_content.append("3. **Moedas estrangeiras**: Identificar e tratar separadamente")
    report_content.append("4. **Múltiplos indexadores**: Extrair o primeiro ou mais comum")
    report_content.append("5. **Formatos alternativos**: Expandir regex para capturar variações")
    
    report_content.append("\n### 3.2 Casos Extremos\n")
    report_content.append("\n1. **Kd muito alto**: Verificar conversão de período mensal para anual")
    report_content.append("2. **Kd muito baixo**: Validar se spread negativo foi aplicado corretamente")
    report_content.append("3. **TR com Kd baixo**: Normal, TR tem valor base muito baixo")
    report_content.append("4. **Pré-fixados internacionais**: Taxas podem ser corretas mas baixas")
    
    report_content.append("\n---")
    report_content.append(f"\n*Lista gerada automaticamente pelo script `{Path(__file__).name}`*")
    
    # Salva relatório
    output_path = DOCS_DIR / "manual_review_indexers.md"
    output_path.write_text("\n".join(report_content), encoding='utf-8')
    print(f"✅ Lista de revisão manual salva em: {output_path}")


if __name__ == "__main__":
    generate_manual_review_list()

