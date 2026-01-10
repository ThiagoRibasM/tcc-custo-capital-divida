#!/usr/bin/env python3
"""
Gera relatório de processamento de Kd com estatísticas e metodologia.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, PROJECT_ROOT

DOCS_DIR = PROJECT_ROOT / "docs"

def generate_kd_report():
    """Gera relatório completo de processamento de Kd."""
    
    # Carrega dados
    df = pd.read_csv(CONSOLIDATED_PATH / "kd_calculated.csv")
    
    # Inicia relatório
    report = []
    report.append("# Relatório de Processamento de Kd")
    report.append("")
    report.append("**Data:** 29 de novembro de 2025")
    report.append("**Arquivo processado:** `emp_e_fin_novo_mercado_20250920.xlsx`")
    report.append("")
    report.append("---")
    report.append("")
    
    # 1. Resumo Executivo
    report.append("## 1. Resumo Executivo")
    report.append("")
    total = len(df)
    kd_calculado = df['Kd_Percentual'].notna().sum()
    kd_valido = df['Kd_Valido'].sum()
    taxa_sucesso = (kd_calculado / total) * 100
    taxa_valido = (kd_valido / total) * 100
    
    report.append(f"- **Total de registros processados:** {total:,}")
    report.append(f"- **Kd calculado:** {kd_calculado:,} ({taxa_sucesso:.1f}%)")
    report.append(f"- **Kd válido:** {kd_valido:,} ({taxa_valido:.1f}%)")
    report.append(f"- **Kd não calculado:** {total - kd_calculado:,} ({100-taxa_sucesso:.1f}%)")
    report.append("")
    
    # 2. Metodologia
    report.append("## 2. Metodologia de Cálculo")
    report.append("")
    report.append("### 2.1 Fórmula de Kd")
    report.append("")
    report.append("O Kd (custo de capital de dívida) foi calculado conforme a literatura:")
    report.append("")
    report.append("```")
    report.append("Kd = Indexador_Base + Spread")
    report.append("```")
    report.append("")
    report.append("Onde:")
    report.append("- **Indexador_Base**: Valor de referência do indexador em 2024")
    report.append("- **Spread**: Margem adicional extraída do texto do indexador")
    report.append("")
    report.append("### 2.2 Valores de Referência dos Indexadores (2024)")
    report.append("")
    report.append("| Indexador | Valor Base (% a.a.) | Fonte/Nota |")
    report.append("|-----------|---------------------|------------|")
    report.append("| CDI | 13,65% | Média 2024 |")
    report.append("| DI | 13,65% | Similar ao CDI |")
    report.append("| TLP | 6,50% | Taxa de Longo Prazo (BNDES) |")
    report.append("| TJLP | 6,50% | Taxa antiga, substituída por TLP |")
    report.append("| IPCA | 4,62% | Inflação projetada 2024 |")
    report.append("| TR | 0,01% | Taxa Referencial (quase em desuso) |")
    report.append("| SELIC | 10,50% | Taxa básica de juros |")
    report.append("| Pré-fixado | - | Taxa já é o Kd final |")
    report.append("")
    report.append("### 2.3 Processamento de Indexadores")
    report.append("")
    report.append("1. **Extração de tipo**: Identificação do indexador usando padrões regex")
    report.append("2. **Extração de spread**: Identificação do spread (margem) no texto")
    report.append("3. **Identificação de período**: Verificação se taxa é anual (a.a.) ou mensal (a.m.)")
    report.append("4. **Conversão**: Taxas mensais convertidas para anuais usando `(1 + taxa_mensal)^12 - 1`")
    report.append("5. **Cálculo de Kd**: Aplicação da fórmula Kd = Base + Spread")
    report.append("6. **Validação**: Verificação se Kd está em range razoável (0% a 50% a.a.)")
    report.append("")
    
    # 3. Estatísticas de Padronização
    report.append("## 3. Estatísticas de Padronização")
    report.append("")
    report.append("### 3.1 Distribuição de Indexadores")
    report.append("")
    indexer_counts = df['Indexador_Processado'].value_counts()
    report.append("| Indexador | Quantidade | % do Total |")
    report.append("|-----------|-----------|------------|")
    for idx, count in indexer_counts.items():
        pct = (count / total) * 100
        report.append(f"| {idx} | {count:,} | {pct:.1f}% |")
    report.append("")
    
    # 4. Distribuição de Kd
    report.append("## 4. Distribuição de Kd Calculado")
    report.append("")
    kd_validos = df[df['Kd_Valido'] == True]['Kd_Percentual']
    if len(kd_validos) > 0:
        report.append("### 4.1 Estatísticas Descritivas")
        report.append("")
        report.append("| Estatística | Valor (% a.a.) |")
        report.append("|------------|----------------|")
        report.append(f"| Média | {kd_validos.mean():.2f} |")
        report.append(f"| Mediana | {kd_validos.median():.2f} |")
        report.append(f"| Desvio Padrão | {kd_validos.std():.2f} |")
        report.append(f"| Mínimo | {kd_validos.min():.2f} |")
        report.append(f"| Máximo | {kd_validos.max():.2f} |")
        report.append(f"| Q1 (25%) | {kd_validos.quantile(0.25):.2f} |")
        report.append(f"| Q3 (75%) | {kd_validos.quantile(0.75):.2f} |")
        report.append("")
        
        report.append("### 4.2 Distribuição por Indexador")
        report.append("")
        report.append("| Indexador | Kd Médio | Kd Mediano | Qtd. Calculados |")
        report.append("|----------|----------|------------|-----------------|")
        for indexer in indexer_counts.head(10).index:
            subset = df[df['Indexador_Processado'] == indexer]
            kd_subset = subset[subset['Kd_Percentual'].notna()]['Kd_Percentual']
            if len(kd_subset) > 0:
                report.append(f"| {indexer} | {kd_subset.mean():.2f}% | {kd_subset.median():.2f}% | {kd_subset.count()} |")
        report.append("")
    
    # 5. Casos Especiais
    report.append("## 5. Casos Especiais e Tratamentos")
    report.append("")
    
    # Indexadores não identificados
    nao_id = df[df['Indexador_Processado'] == 'NÃO_IDENTIFICADO']
    report.append(f"### 5.1 Indexadores Não Identificados")
    report.append("")
    report.append(f"Total: {len(nao_id):,} registros ({len(nao_id)/total*100:.1f}%)")
    report.append("")
    report.append("Principais razões:")
    report.append("- Formatos não padronizados")
    report.append("- Indexadores raros ou específicos")
    report.append("- Textos incompletos ou mal formatados")
    report.append("- Múltiplos indexadores no mesmo texto")
    report.append("")
    
    # Kd inválidos
    kd_invalidos = df[df['Kd_Percentual'].notna() & ~df['Kd_Valido']]
    if len(kd_invalidos) > 0:
        report.append(f"### 5.2 Kd Fora do Range Válido")
        report.append("")
        report.append(f"Total: {len(kd_invalidos):,} registros")
        report.append("")
        report.append("Kd inválidos geralmente ocorrem por:")
        report.append("- Spreads extremos (muito altos ou negativos)")
        report.append("- Erros na extração de valores")
        report.append("- Indexadores com valores base incorretos")
        report.append("")
    
    # 6. Qualidade dos Dados
    report.append("## 6. Qualidade dos Dados")
    report.append("")
    
    # Valores consolidados
    valores_validos = df['Valor_Consolidado_2024'].notna().sum()
    valores_zero = (df['Valor_Consolidado_2024'] == 0).sum()
    report.append(f"- **Valores consolidados preenchidos:** {valores_validos:,} ({valores_validos/total*100:.1f}%)")
    report.append(f"- **Valores consolidados = 0:** {valores_zero:,} ({valores_zero/total*100:.1f}%)")
    report.append("")
    
    # 7. Recomendações
    report.append("## 7. Recomendações")
    report.append("")
    report.append("### 7.1 Melhorias na Padronização")
    report.append("")
    report.append("1. **Revisão manual** dos 326 indexadores não identificados")
    report.append("2. **Expansão de padrões regex** para capturar mais variações")
    report.append("3. **Tratamento de casos especiais**: faixas de taxa, múltiplos indexadores")
    report.append("4. **Validação cruzada** com dados de mercado quando disponível")
    report.append("")
    report.append("### 7.2 Uso dos Dados")
    report.append("")
    report.append("1. **Filtrar por Kd válido** para análises principais")
    report.append("2. **Revisar casos extremos** (Kd muito alto ou muito baixo)")
    report.append("3. **Considerar valores consolidados = 0** como financiamentos quitados ou não aplicáveis")
    report.append("4. **Agrupar por tipo de indexador** para análises comparativas")
    report.append("")
    
    # 8. Referências
    report.append("## 8. Referências Metodológicas")
    report.append("")
    report.append("- ASSAF NETO, Alexandre. **Finanças Corporativas e Valor**. 6. ed. São Paulo: Atlas, 2014.")
    report.append("- DAMODARAN, Aswath. **Investment Valuation: Tools and Techniques for Determining the Value of Any Asset**. 3. ed. Hoboken: Wiley, 2012.")
    report.append("")
    report.append("---")
    report.append("")
    report.append("*Relatório gerado automaticamente pelo script `src/utils/generate_kd_report.py`*")
    
    # Salva relatório
    output_file = DOCS_DIR / "kd_processing_report.md"
    output_file.write_text("\n".join(report), encoding='utf-8')
    print(f"✅ Relatório salvo em: {output_file}")
    
    return "\n".join(report)


if __name__ == "__main__":
    generate_kd_report()

