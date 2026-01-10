#!/usr/bin/env python3
"""
Análise detalhada dos ranges de Kd observados e comparação com literatura.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, PROJECT_ROOT

DOCS_DIR = PROJECT_ROOT / "docs"


def analyze_kd_ranges():
    """Gera análise detalhada dos ranges de Kd."""
    
    # Lê dados
    df_final = pd.read_csv(CONSOLIDATED_PATH / "kd_final_calculados.csv")
    
    print("📊 ANÁLISE DETALHADA DOS RANGES DE Kd")
    print("="*70)
    
    report = []
    report.append("# Análise Detalhada dos Ranges de Kd")
    report.append(f"\n**Data:** {datetime.now().strftime('%d de %B de %Y')}")
    report.append(f"**Total de registros analisados:** {len(df_final)}")
    report.append(f"\n---\n")
    
    # 1. Estatísticas Gerais
    report.append("## 1. Estatísticas Descritivas Gerais\n")
    
    kd_stats = df_final['Kd_Percentual'].describe()
    report.append("| Estatística | Valor (% a.a.) |")
    report.append("|------------|----------------|")
    for stat, value in kd_stats.items():
        report.append(f"| {stat.capitalize()} | {value:.2f} |")
    
    # Percentis adicionais
    percentis = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    report.append("\n### Percentis Adicionais\n")
    report.append("| Percentil | Kd (% a.a.) |")
    report.append("|-----------|-------------|")
    for p in percentis:
        value = df_final['Kd_Percentual'].quantile(p/100)
        report.append(f"| {p}% | {value:.2f} |")
    
    # 2. Distribuição por Faixas
    report.append("\n## 2. Distribuição por Faixas de Kd\n")
    
    faixas = [
        (0, 5, "Muito Baixo (< 5%)"),
        (5, 8, "Baixo (5% - 8%)"),
        (8, 12, "Moderado-Baixo (8% - 12%)"),
        (12, 16, "Moderado (12% - 16%)"),
        (16, 20, "Moderado-Alto (16% - 20%)"),
        (20, 30, "Alto (20% - 30%)"),
        (30, 50, "Muito Alto (30% - 50%)"),
        (50, float('inf'), "Extremo (> 50%)")
    ]
    
    report.append("| Faixa | Quantidade | % do Total | Média Kd |")
    report.append("|-------|-----------|------------|---------|")
    
    for min_val, max_val, label in faixas:
        if max_val == float('inf'):
            mask = df_final['Kd_Percentual'] >= min_val
        else:
            mask = (df_final['Kd_Percentual'] >= min_val) & (df_final['Kd_Percentual'] < max_val)
        
        count = mask.sum()
        pct = (count / len(df_final)) * 100
        if count > 0:
            mean_kd = df_final[mask]['Kd_Percentual'].mean()
            report.append(f"| {label} | {count} | {pct:.1f}% | {mean_kd:.2f}% |")
        else:
            report.append(f"| {label} | 0 | 0.0% | - |")
    
    # 3. Análise por Indexador
    report.append("\n## 3. Análise Detalhada por Indexador\n")
    
    indexadores = df_final['Indexador_Processado'].value_counts().index
    
    for idx in indexadores:
        if idx == 'NÃO_IDENTIFICADO':
            continue
        
        df_idx = df_final[df_final['Indexador_Processado'] == idx]
        
        report.append(f"\n### 3.{indexadores.get_loc(idx) + 1} {idx}\n")
        report.append(f"**Total de registros:** {len(df_idx)}\n")
        
        # Estatísticas
        stats = df_idx['Kd_Percentual'].describe()
        report.append("| Estatística | Valor (% a.a.) |")
        report.append("|------------|----------------|")
        report.append(f"| Média | {stats['mean']:.2f} |")
        report.append(f"| Mediana | {stats['50%']:.2f} |")
        report.append(f"| Desvio Padrão | {stats['std']:.2f} |")
        report.append(f"| Mínimo | {stats['min']:.2f} |")
        report.append(f"| Máximo | {stats['max']:.2f} |")
        report.append(f"| Q1 (25%) | {stats['25%']:.2f} |")
        report.append(f"| Q3 (75%) | {stats['75%']:.2f} |")
        
        # Range interquartil
        iqr = stats['75%'] - stats['25%']
        report.append(f"\n**Range Interquartil (IQR):** {iqr:.2f}%")
        report.append(f"**Limite Inferior (Q1 - 1.5*IQR):** {stats['25%'] - 1.5*iqr:.2f}%")
        report.append(f"**Limite Superior (Q3 + 1.5*IQR):** {stats['75%'] + 1.5*iqr:.2f}%")
        
        # Outliers
        lower_bound = stats['25%'] - 1.5*iqr
        upper_bound = stats['75%'] + 1.5*iqr
        outliers = df_idx[(df_idx['Kd_Percentual'] < lower_bound) | (df_idx['Kd_Percentual'] > upper_bound)]
        report.append(f"\n**Outliers identificados:** {len(outliers)} ({len(outliers)/len(df_idx)*100:.1f}%)")
        
        if len(outliers) > 0:
            report.append("\n| Empresa | Kd (%) | Observação |")
            report.append("|---------|--------|------------|")
            for _, row in outliers.head(10).iterrows():
                empresa = str(row['Empresa'])[:40]
                kd = row['Kd_Percentual']
                obs = str(row['Kd_Observacao_Validacao'])[:50] if pd.notna(row['Kd_Observacao_Validacao']) else ""
                report.append(f"| {empresa} | {kd:.2f} | {obs} |")
    
    # 4. Comparação com Ranges da Literatura
    report.append("\n## 4. Comparação com Ranges da Literatura\n")
    
    report.append("### 4.1 Ranges Típicos por Contexto\n")
    report.append("| Contexto | Range Típico | Observações |")
    report.append("|----------|--------------|-------------|")
    report.append("| Brasil - Mercado Desenvolvido | 8% - 20% | Maioria dos casos |")
    report.append("| Brasil - Taxas Indexadas (CDI/DI) | 12% - 25% | Com spread típico |")
    report.append("| Brasil - Taxas Indexadas (IPCA/TLP) | 6% - 15% | Com spread típico |")
    report.append("| Brasil - Pré-fixado | 5% - 30% | Depende do prazo e risco |")
    report.append("| Mercados Emergentes | 10% - 30% | Maior risco país |")
    report.append("| Mercados Desenvolvidos | 3% - 12% | Taxas de juros mais baixas |")
    
    # 5. Análise de Outliers e Casos Extremos
    report.append("\n## 5. Análise de Outliers e Casos Extremos\n")
    
    # Kd muito baixo (< 5%)
    kd_baixo = df_final[df_final['Kd_Percentual'] < 5]
    report.append(f"\n### 5.1 Kd Muito Baixo (< 5%)\n")
    report.append(f"**Total:** {len(kd_baixo)} registros ({len(kd_baixo)/len(df_final)*100:.1f}%)\n")
    
    if len(kd_baixo) > 0:
        report.append("| Indexador | Quantidade | Kd Médio | Principais Razões |")
        report.append("|-----------|-----------|----------|-------------------|")
        for idx in kd_baixo['Indexador_Processado'].value_counts().index:
            df_sub = kd_baixo[kd_baixo['Indexador_Processado'] == idx]
            count = len(df_sub)
            mean_kd = df_sub['Kd_Percentual'].mean()
            reasons = df_sub['Kd_Observacao_Validacao'].value_counts().head(1).index[0] if len(df_sub['Kd_Observacao_Validacao'].value_counts()) > 0 else "N/A"
            report.append(f"| {idx} | {count} | {mean_kd:.2f}% | {str(reasons)[:50]} |")
    
    # Kd muito alto (> 30%)
    kd_alto = df_final[df_final['Kd_Percentual'] > 30]
    report.append(f"\n### 5.2 Kd Muito Alto (> 30%)\n")
    report.append(f"**Total:** {len(kd_alto)} registros ({len(kd_alto)/len(df_final)*100:.1f}%)\n")
    
    if len(kd_alto) > 0:
        report.append("| Empresa | Indexador | Kd (%) | Spread (%) | Observação |")
        report.append("|---------|-----------|--------|------------|------------|")
        for _, row in kd_alto.head(20).iterrows():
            empresa = str(row['Empresa'])[:30]
            idx = str(row['Indexador_Processado'])
            kd = row['Kd_Percentual']
            spread = row['Spread_Percentual'] if pd.notna(row['Spread_Percentual']) else "N/A"
            obs = str(row['Kd_Observacao_Validacao'])[:40] if pd.notna(row['Kd_Observacao_Validacao']) else ""
            report.append(f"| {empresa} | {idx} | {kd:.2f} | {spread} | {obs} |")
    
    # 6. Análise por Tipo de Financiamento
    report.append("\n## 6. Análise por Tipo de Financiamento\n")
    
    tipos = df_final['Tipo_Financiamento'].value_counts().head(10)
    
    report.append("| Tipo de Financiamento | Quantidade | Kd Médio | Kd Mediano |")
    report.append("|----------------------|-----------|----------|------------|")
    for tipo, count in tipos.items():
        df_tipo = df_final[df_final['Tipo_Financiamento'] == tipo]
        mean_kd = df_tipo['Kd_Percentual'].mean()
        median_kd = df_tipo['Kd_Percentual'].median()
        tipo_str = str(tipo)[:50]
        report.append(f"| {tipo_str} | {count} | {mean_kd:.2f}% | {median_kd:.2f}% |")
    
    # 7. Recomendações
    report.append("\n## 7. Recomendações Baseadas na Análise\n")
    
    # Range recomendado
    q1 = df_final['Kd_Percentual'].quantile(0.25)
    q3 = df_final['Kd_Percentual'].quantile(0.75)
    iqr = q3 - q1
    
    report.append("### 7.1 Range Recomendado para Validação\n")
    report.append(f"- **Range Interquartil (IQR):** {q1:.2f}% - {q3:.2f}%")
    report.append(f"- **Range Conservador (Q1 - 1.5*IQR a Q3 + 1.5*IQR):** {q1 - 1.5*iqr:.2f}% - {q3 + 1.5*iqr:.2f}%")
    report.append(f"- **Range Prático Recomendado:** 5% - 30% a.a.")
    report.append(f"  - Abaixo de 5%: Revisar (possíveis erros ou casos especiais)")
    report.append(f"  - Acima de 30%: Revisar (possíveis erros de conversão ou spreads incorretos)")
    
    report.append("\n### 7.2 Tratamento de Outliers\n")
    report.append("1. **Kd < 5%**: Verificar se é:")
    report.append("   - Taxa TR (normalmente muito baixa)")
    report.append("   - Taxa internacional (USD, EUR)")
    report.append("   - Erro na extração do spread")
    report.append("2. **Kd > 30%**: Verificar se é:")
    report.append("   - Erro na conversão de período (mensal para anual)")
    report.append("   - Spread incorreto ou mal extraído")
    report.append("   - Caso legítimo de alto risco (revisar manualmente)")
    
    report.append("\n### 7.3 Uso dos Dados\n")
    report.append("1. **Para análises principais**: Filtrar Kd entre 5% e 30%")
    report.append("2. **Para análises robustas**: Incluir outliers mas com flags de validação")
    report.append("3. **Para estudos comparativos**: Agrupar por indexador e tipo de financiamento")
    
    # 8. Resumo Executivo
    report.append("\n## 8. Resumo Executivo\n")
    
    report.append(f"- **Total de registros:** {len(df_final)}")
    report.append(f"- **Kd médio:** {df_final['Kd_Percentual'].mean():.2f}% a.a.")
    report.append(f"- **Kd mediano:** {df_final['Kd_Percentual'].median():.2f}% a.a.")
    report.append(f"- **Range observado:** {df_final['Kd_Percentual'].min():.2f}% - {df_final['Kd_Percentual'].max():.2f}%")
    report.append(f"- **Range interquartil:** {q1:.2f}% - {q3:.2f}%")
    report.append(f"- **Registros com Kd < 5%:** {len(kd_baixo)} ({len(kd_baixo)/len(df_final)*100:.1f}%)")
    report.append(f"- **Registros com Kd > 30%:** {len(kd_alto)} ({len(kd_alto)/len(df_final)*100:.1f}%)")
    report.append(f"- **Registros no range recomendado (5% - 30%):** {len(df_final[(df_final['Kd_Percentual'] >= 5) & (df_final['Kd_Percentual'] <= 30)])} ({len(df_final[(df_final['Kd_Percentual'] >= 5) & (df_final['Kd_Percentual'] <= 30)])/len(df_final)*100:.1f}%)")
    
    report.append("\n---")
    report.append(f"\n*Análise gerada automaticamente pelo script `{Path(__file__).name}`*")
    
    # Salva relatório
    output_path = DOCS_DIR / "kd_ranges_analysis.md"
    output_path.write_text("\n".join(report), encoding='utf-8')
    print(f"✅ Análise detalhada salva em: {output_path}")
    
    # Exibe resumo no terminal
    print(f"\n📊 RESUMO DA ANÁLISE:")
    print(f"   Total de registros: {len(df_final)}")
    print(f"   Kd médio: {df_final['Kd_Percentual'].mean():.2f}% a.a.")
    print(f"   Kd mediano: {df_final['Kd_Percentual'].median():.2f}% a.a.")
    print(f"   Range observado: {df_final['Kd_Percentual'].min():.2f}% - {df_final['Kd_Percentual'].max():.2f}%")
    print(f"   Range interquartil: {q1:.2f}% - {q3:.2f}%")
    print(f"   Registros no range 5%-30%: {len(df_final[(df_final['Kd_Percentual'] >= 5) & (df_final['Kd_Percentual'] <= 30)])} ({len(df_final[(df_final['Kd_Percentual'] >= 5) & (df_final['Kd_Percentual'] <= 30)])/len(df_final)*100:.1f}%)")


if __name__ == "__main__":
    analyze_kd_ranges()

