#!/usr/bin/env python3
"""
Gera relatório de melhorias na padronização de indexadores e validação de Kd.
"""
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, PROJECT_ROOT

DOCS_DIR = PROJECT_ROOT / "docs"


def generate_improvements_report():
    """Gera relatório de melhorias."""
    
    # Lê dados melhorados
    df_improved = pd.read_csv(CONSOLIDATED_PATH / "kd_calculated_improved.csv")
    
    # Tenta ler dados anteriores para comparação
    df_previous = None
    try:
        df_previous = pd.read_csv(CONSOLIDATED_PATH / "kd_calculated.csv")
    except:
        pass
    
    report_content = []
    report_content.append("# Relatório de Melhorias na Padronização de Indexadores e Validação de Kd")
    report_content.append(f"\n**Data:** {datetime.now().strftime('%d de %B de %Y')}")
    report_content.append(f"\n---\n")
    
    # 1. Resumo Executivo
    report_content.append("## 1. Resumo Executivo\n")
    total = len(df_improved)
    identified = (df_improved['Indexador_Processado'] != 'NÃO_IDENTIFICADO').sum()
    identified_pct = (identified / total) * 100
    kd_calculated = df_improved['Kd_Decimal'].notna().sum()
    kd_valid = df_improved['Kd_Valido'].sum()
    
    report_content.append(f"- **Total de registros:** {total}")
    report_content.append(f"- **Indexadores identificados:** {identified} ({identified_pct:.1f}%)")
    report_content.append(f"- **Kd calculado:** {kd_calculated} ({kd_calculated/total:.1%})")
    report_content.append(f"- **Kd válido:** {kd_valid} ({kd_valid/total:.1%})")
    
    if df_previous is not None:
        prev_identified = (df_previous['Indexador_Processado'] != 'NÃO_IDENTIFICADO').sum()
        prev_pct = (prev_identified / len(df_previous)) * 100
        improvement = identified_pct - prev_pct
        report_content.append(f"\n### Melhoria na Taxa de Identificação")
        report_content.append(f"- **Antes:** {prev_pct:.1f}% ({prev_identified}/{len(df_previous)})")
        report_content.append(f"- **Depois:** {identified_pct:.1f}% ({identified}/{total})")
        report_content.append(f"- **Melhoria:** +{improvement:.1f} pontos percentuais")
    
    # 2. Padrões Adicionados
    report_content.append("\n## 2. Padrões Adicionados\n")
    report_content.append("### 2.1 Novos Indexadores Identificados")
    new_indexers = ['SOFR', 'LIBOR', 'IGPM', 'IPC', 'POS_FIXADO']
    report_content.append("\nOs seguintes indexadores foram adicionados à detecção:")
    for idx in new_indexers:
        count = (df_improved['Indexador_Processado'] == idx).sum()
        if count > 0:
            report_content.append(f"- **{idx}**: {count} ocorrências")
    
    report_content.append("\n### 2.2 Melhorias nos Padrões Regex")
    report_content.append("\n1. **Detecção de Pré-fixado melhorada**:")
    report_content.append("   - Captura variações: 'Pré', 'Pré-fixado', 'Pré fixado', 'Fixo', 'Fixa'")
    report_content.append("   - Detecta percentuais diretos sem palavra-chave (ex: '18,44% a.a.')")
    
    report_content.append("\n2. **Extração de Spread melhorada**:")
    report_content.append("   - Captura spreads negativos (ex: 'CDI - 0,5%')")
    report_content.append("   - Trata faixas de percentual (ex: '5,60% a 9,88%') - usa primeiro valor")
    report_content.append("   - Melhor tratamento de formatos alternativos (vírgula, ponto)")
    
    report_content.append("\n3. **Indexadores Internacionais**:")
    report_content.append("   - SOFR (Secured Overnight Financing Rate)")
    report_content.append("   - LIBOR (London Interbank Offered Rate)")
    
    # 3. Distribuição de Indexadores
    report_content.append("\n## 3. Distribuição de Indexadores\n")
    indexer_counts = df_improved['Indexador_Processado'].value_counts()
    indexer_pct = df_improved['Indexador_Processado'].value_counts(normalize=True) * 100
    
    report_content.append("\n| Indexador | Quantidade | % do Total |")
    report_content.append("|-----------|-----------|------------|")
    for idx, count in indexer_counts.items():
        report_content.append(f"| {idx} | {count} | {indexer_pct[idx]:.1f}% |")
    
    # 4. Validação de Casos Extremos
    report_content.append("\n## 4. Validação de Casos Extremos\n")
    extreme_high = df_improved['Kd_Extremo_Alto'].sum()
    extreme_low = df_improved['Kd_Extremo_Baixo'].sum()
    needs_review = df_improved['Kd_Revisao_Manual'].sum()
    
    report_content.append(f"\n- **Kd extremo alto (>30%):** {extreme_high} registros")
    report_content.append(f"- **Kd extremo baixo (<5%):** {extreme_low} registros")
    report_content.append(f"- **Requer revisão manual:** {needs_review} registros")
    
    # Exemplos de casos extremos
    if extreme_high > 0:
        report_content.append("\n### 4.1 Exemplos de Kd Extremo Alto")
        df_high = df_improved[df_improved['Kd_Extremo_Alto'] == True].head(5)
        report_content.append("\n| Empresa | Indexador | Kd (%) | Observação |")
        report_content.append("|---------|-----------|--------|------------|")
        for _, row in df_high.iterrows():
            empresa = str(row['Empresa'])[:30]
            indexador = str(row['Indexador_Processado'])
            kd = f"{row['Kd_Percentual']:.2f}" if pd.notna(row['Kd_Percentual']) else "N/A"
            obs = str(row['Kd_Observacao_Validacao'])[:40] if pd.notna(row['Kd_Observacao_Validacao']) else ""
            report_content.append(f"| {empresa} | {indexador} | {kd} | {obs} |")
    
    if extreme_low > 0:
        report_content.append("\n### 4.2 Exemplos de Kd Extremo Baixo")
        df_low = df_improved[df_improved['Kd_Extremo_Baixo'] == True].head(5)
        report_content.append("\n| Empresa | Indexador | Kd (%) | Observação |")
        report_content.append("|---------|-----------|--------|------------|")
        for _, row in df_low.iterrows():
            empresa = str(row['Empresa'])[:30]
            indexador = str(row['Indexador_Processado'])
            kd = f"{row['Kd_Percentual']:.2f}" if pd.notna(row['Kd_Percentual']) else "N/A"
            obs = str(row['Kd_Observacao_Validacao'])[:40] if pd.notna(row['Kd_Observacao_Validacao']) else ""
            report_content.append(f"| {empresa} | {indexador} | {kd} | {obs} |")
    
    # 5. Indexadores Não Identificados
    report_content.append("\n## 5. Indexadores Não Identificados\n")
    nao_id = df_improved[df_improved['Indexador_Processado'] == 'NÃO_IDENTIFICADO']
    report_content.append(f"\nTotal: {len(nao_id)} registros ({len(nao_id)/total:.1%})")
    
    if len(nao_id) > 0:
        report_content.append("\n### 5.1 Top 20 Indexadores Não Identificados Mais Frequentes")
        # Precisa ler dados originais para ver indexadores originais
        try:
            df_orig = pd.read_excel(CONSOLIDATED_PATH / "emp_e_fin_novo_mercado_20250920.xlsx")
            df_merged = nao_id.merge(df_orig[['indexador']], left_index=True, right_index=True, how='left')
            top_nao_id = df_merged['indexador'].value_counts().head(20)
            
            report_content.append("\n| Indexador Original | Frequência |")
            report_content.append("|-------------------|------------|")
            for idx, (val, count) in enumerate(top_nao_id.items(), 1):
                val_str = str(val)[:60] if pd.notna(val) else "NaN"
                report_content.append(f"| {val_str} | {count} |")
        except:
            report_content.append("\n*Não foi possível carregar indexadores originais para análise.*")
    
    # 6. Recomendações
    report_content.append("\n## 6. Recomendações\n")
    report_content.append("\n### 6.1 Melhorias Adicionais Sugeridas")
    report_content.append("\n1. **Revisão manual dos indexadores não identificados**:")
    report_content.append(f"   - {len(nao_id)} registros ainda não identificados")
    report_content.append("   - Focar nos mais frequentes para identificar novos padrões")
    
    report_content.append("\n2. **Validação de casos extremos**:")
    report_content.append(f"   - Revisar {needs_review} casos que requerem validação manual")
    report_content.append("   - Verificar se conversões de período estão corretas")
    report_content.append("   - Validar spreads extremos")
    
    report_content.append("\n3. **Tratamento de casos especiais**:")
    report_content.append("   - Variação cambial (VC, v.c.)")
    report_content.append("   - Múltiplos indexadores no mesmo campo")
    report_content.append("   - Moedas estrangeiras (USD, EUR, Dólar, Euro)")
    
    report_content.append("\n### 6.2 Próximos Passos")
    report_content.append("\n1. Revisar manualmente os casos em `kd_manual_review.csv`")
    report_content.append("2. Expandir padrões regex baseado nos indexadores não identificados mais frequentes")
    report_content.append("3. Validar valores base dos indexadores internacionais (SOFR, LIBOR)")
    report_content.append("4. Implementar tratamento para variação cambial")
    
    report_content.append("\n---")
    report_content.append(f"\n*Relatório gerado automaticamente pelo script `{Path(__file__).name}`*")
    
    # Salva relatório
    output_path = DOCS_DIR / "kd_improvements_report.md"
    output_path.write_text("\n".join(report_content), encoding='utf-8')
    print(f"✅ Relatório salvo em: {output_path}")


if __name__ == "__main__":
    generate_improvements_report()

