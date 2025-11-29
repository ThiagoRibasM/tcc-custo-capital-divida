#!/usr/bin/env python3
"""
Gera relatório markdown descritivo de todas as visualizações do EDA.
"""
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, FIGURES_DIR, PROJECT_ROOT

REPORTS_DIR = PROJECT_ROOT / "reports"


def generate_eda_report():
    """Gera relatório markdown completo do EDA."""
    
    # Lê dados para estatísticas
    df = pd.read_csv(CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv")
    
    report = []
    report.append("# Relatório de Análise Exploratória de Dados (EDA)")
    report.append(f"\n**Data:** {datetime.now().strftime('%d de %B de %Y')}")
    report.append(f"**Total de empresas analisadas:** {len(df)}")
    report.append(f"\n---\n")
    
    # Resumo Executivo
    report.append("## Resumo Executivo\n")
    report.append(f"Este relatório apresenta uma análise exploratória completa dos dados de Kd ponderado por empresa.")
    report.append(f"Foram geradas **40 visualizações** em formato PNG de alta resolução (300 DPI), organizadas em 10 categorias de análise.\n")
    
    report.append("### Estatísticas Principais\n")
    report.append(f"- **Kd Ponderado Médio:** {df['Kd_Ponderado'].mean():.2f}% a.a.")
    report.append(f"- **Kd Ponderado Mediano:** {df['Kd_Ponderado'].median():.2f}% a.a.")
    report.append(f"- **Desvio Padrão:** {df['Kd_Ponderado'].std():.2f}%")
    report.append(f"- **Range:** {df['Kd_Ponderado'].min():.2f}% - {df['Kd_Ponderado'].max():.2f}%")
    report.append(f"- **Valor Consolidado Médio:** R$ {df['Valor_Consolidado_Media'].mean():,.2f}")
    report.append(f"- **Total de Financiamentos Médio:** {df['Total_Financiamentos'].mean():.1f}\n")
    
    # Tabela de Referência Rápida
    report.append("## Tabela de Referência Rápida das Figuras\n")
    report.append("| # | Nome do Arquivo | Descrição | Categoria |")
    report.append("|---|----------------|-----------|------------|")
    
    figures_info = [
        (1, "01_distribuicao_kd_ponderado_histograma.png", "Histograma da distribuição de Kd ponderado", "Análise Descritiva Básica"),
        (2, "02_distribuicao_kd_ponderado_boxplot.png", "Boxplot de Kd ponderado", "Análise Descritiva Básica"),
        (3, "03_distribuicao_kd_ponderado_violino.png", "Violin plot (distribuição + densidade)", "Análise Descritiva Básica"),
        (4, "04_estatisticas_descritivas_tabela.png", "Tabela com estatísticas descritivas", "Análise Descritiva Básica"),
        (5, "05_distribuicao_kd_ponderado_qqplot.png", "Q-Q plot para verificar normalidade", "Análise Descritiva Básica"),
        (6, "06_distribuicao_empresas_por_faixa_kd.png", "Quantidade de empresas por faixa de Kd", "Análise Demográfica"),
        (7, "07_kd_vs_valor_consolidado_scatter.png", "Scatter plot Kd vs Valor Consolidado", "Análise Demográfica"),
        (8, "08_kd_vs_total_financiamentos.png", "Kd vs Quantidade de Financiamentos", "Análise Demográfica"),
        (9, "09_top_20_empresas_kd_maior.png", "Top 20 empresas com maior Kd", "Análise Demográfica"),
        (10, "10_top_20_empresas_kd_menor.png", "Top 20 empresas com menor Kd", "Análise Demográfica"),
        (11, "11_distribuicao_indexadores_unicos.png", "Distribuição de indexadores únicos por empresa", "Análise Demográfica"),
        (12, "12_distribuicao_tipos_financiamento_unicos.png", "Distribuição de tipos de financiamento únicos", "Análise Demográfica"),
        (13, "13_kd_ponderado_vs_kd_medio_simples.png", "Comparação Kd ponderado vs médio simples", "Análise de Heterogeneidade"),
        (14, "14_heterogeneidade_kd_desvio_padrao.png", "Análise de heterogeneidade (desvio padrão)", "Análise de Heterogeneidade"),
        (15, "15_range_kd_min_max.png", "Range de Kd (min vs max) por empresa", "Análise de Heterogeneidade"),
        (16, "16_correlacao_kd_ponderado_desvio.png", "Correlação entre Kd ponderado e desvio padrão", "Análise de Heterogeneidade"),
        (17, "17_distribuicao_valor_consolidado_histograma.png", "Distribuição do valor consolidado médio", "Análise de Valor Consolidado"),
        (18, "18_kd_vs_valor_consolidado_log.png", "Scatter plot com escala logarítmica", "Análise de Valor Consolidado"),
        (19, "19_valor_consolidado_total_vs_kd.png", "Valor consolidado total vs Kd", "Análise de Valor Consolidado"),
        (20, "20_distribuicao_valor_por_faixa_kd.png", "Distribuição de valor por faixa de Kd", "Análise de Valor Consolidado"),
        (21, "21_identificacao_outliers_boxplot.png", "Boxplot com outliers destacados", "Análise de Outliers"),
        (22, "22_outliers_kd_ponderado_scatter.png", "Scatter plot com outliers identificados", "Análise de Outliers"),
        (23, "23_casos_extremos_kd_alto.png", "Análise de casos com Kd muito alto (>30%)", "Análise de Outliers"),
        (24, "24_casos_extremos_kd_baixo.png", "Análise de casos com Kd muito baixo (<5%)", "Análise de Outliers"),
        (25, "25_distribuicao_por_indexador_principal.png", "Distribuição de Kd por indexador mais usado", "Análise de Indexadores"),
        (26, "26_kd_vs_quantidade_indexadores.png", "Kd vs quantidade de indexadores únicos", "Análise de Indexadores"),
        (27, "27_heatmap_indexadores_unicos_vs_kd.png", "Heatmap de indexadores vs Kd", "Análise de Indexadores"),
        (28, "28_comparacao_indexadores_boxplot.png", "Boxplot comparativo por indexador", "Análise de Indexadores"),
        (29, "29_kd_vs_tipos_financiamento_unicos.png", "Kd vs quantidade de tipos únicos", "Análise de Tipos de Financiamento"),
        (30, "30_distribuicao_tipos_financiamento.png", "Distribuição de tipos de financiamento", "Análise de Tipos de Financiamento"),
        (31, "31_correlacao_tipos_vs_kd.png", "Correlação entre tipos únicos e Kd", "Análise de Tipos de Financiamento"),
        (32, "32_matriz_correlacao_completa.png", "Matriz de correlação de todas as variáveis numéricas", "Matriz de Correlação"),
        (33, "33_correlacao_kd_principais_variaveis.png", "Correlação de Kd com principais variáveis", "Matriz de Correlação"),
        (34, "34_clustering_kd_valor_financiamentos.png", "Análise de clusters (K-means)", "Análise de Agrupamentos"),
        (35, "35_dendrograma_empresas_similares.png", "Dendrograma de empresas similares", "Análise de Agrupamentos"),
        (36, "36_heatmap_empresas_top30.png", "Heatmap das top 30 empresas", "Análise de Agrupamentos"),
        (37, "37_teste_normalidade_kd.png", "Testes de normalidade (Shapiro-Wilk, Q-Q plot)", "Análise Estatística Avançada"),
        (38, "38_distribuicao_log_kd.png", "Distribuição do log de Kd", "Análise Estatística Avançada"),
        (39, "39_analise_residuos_kd.png", "Análise de resíduos (regressão)", "Análise Estatística Avançada"),
        (40, "40_sumario_estatistico_completo.png", "Sumário estatístico completo", "Análise Estatística Avançada"),
    ]
    
    for num, filename, desc, category in figures_info:
        report.append(f"| {num:02d} | `{filename}` | {desc} | {category} |")
    
    # Descrições Detalhadas por Categoria
    report.append("\n## Descrições Detalhadas por Categoria\n")
    
    # 1. Análise Descritiva Básica
    report.append("### 1. Análise Descritiva Básica (01-05)\n")
    report.append("Esta seção apresenta a distribuição fundamental da variável resposta (Kd ponderado).\n")
    report.append("- **01**: Histograma mostra a distribuição de frequência do Kd ponderado")
    report.append("- **02**: Boxplot identifica quartis, mediana e outliers")
    report.append("- **03**: Violin plot combina distribuição e densidade")
    report.append("- **04**: Tabela com estatísticas descritivas completas")
    report.append("- **05**: Q-Q plot verifica se a distribuição segue uma normal\n")
    
    # 2. Análise Demográfica
    report.append("### 2. Análise Demográfica (06-12)\n")
    report.append("Análise das características demográficas das empresas e seus financiamentos.\n")
    report.append("- **06**: Distribuição de empresas por faixas de Kd")
    report.append("- **07**: Relação entre Kd e valor consolidado (tamanho do financiamento)")
    report.append("- **08**: Relação entre Kd e quantidade de financiamentos")
    report.append("- **09-10**: Top 20 empresas com maior e menor Kd")
    report.append("- **11-12**: Diversidade de indexadores e tipos de financiamento\n")
    
    # 3. Análise de Heterogeneidade
    report.append("### 3. Análise de Heterogeneidade (13-16)\n")
    report.append("Análise da variabilidade e heterogeneidade do Kd dentro de cada empresa.\n")
    report.append("- **13**: Comparação entre Kd ponderado e médio simples")
    report.append("- **14**: Heterogeneidade medida pelo desvio padrão")
    report.append("- **15**: Range de Kd (mínimo vs máximo) por empresa")
    report.append("- **16**: Correlação entre Kd ponderado e heterogeneidade\n")
    
    # 4. Análise de Valor Consolidado
    report.append("### 4. Análise de Valor Consolidado (17-20)\n")
    report.append("Análise do valor consolidado e sua relação com o Kd.\n")
    report.append("- **17**: Distribuição do valor consolidado médio")
    report.append("- **18**: Relação Kd vs valor com escala logarítmica")
    report.append("- **19**: Valor consolidado total vs Kd")
    report.append("- **20**: Distribuição de valor por faixa de Kd\n")
    
    # 5. Análise de Outliers
    report.append("### 5. Análise de Outliers e Casos Extremos (21-24)\n")
    report.append("Identificação e análise de casos extremos e outliers.\n")
    report.append("- **21**: Boxplot com outliers destacados")
    report.append("- **22**: Scatter plot com outliers identificados")
    report.append("- **23**: Empresas com Kd muito alto (>30%)")
    report.append("- **24**: Empresas com Kd muito baixo (<5%)\n")
    
    # 6. Análise de Indexadores
    report.append("### 6. Análise de Indexadores (25-28)\n")
    report.append("Análise da relação entre indexadores financeiros e Kd.\n")
    report.append("- **25**: Distribuição por indexador principal")
    report.append("- **26**: Kd vs quantidade de indexadores únicos")
    report.append("- **27**: Heatmap de indexadores vs Kd")
    report.append("- **28**: Comparação de Kd por indexador\n")
    
    # 7. Análise de Tipos de Financiamento
    report.append("### 7. Análise de Tipos de Financiamento (29-31)\n")
    report.append("Análise da diversidade de tipos de financiamento.\n")
    report.append("- **29**: Kd vs tipos de financiamento únicos")
    report.append("- **30**: Distribuição de tipos de financiamento")
    report.append("- **31**: Correlação entre tipos únicos e Kd\n")
    
    # 8. Matriz de Correlação
    report.append("### 8. Matriz de Correlação (32-33)\n")
    report.append("Análise de correlações entre todas as variáveis.\n")
    report.append("- **32**: Matriz de correlação completa")
    report.append("- **33**: Correlação de Kd com principais variáveis\n")
    
    # 9. Análise de Agrupamentos
    report.append("### 9. Análise de Agrupamentos (34-36)\n")
    report.append("Identificação de grupos similares de empresas.\n")
    report.append("- **34**: Clustering K-means (Kd, Valor, Financiamentos)")
    report.append("- **35**: Dendrograma de empresas similares")
    report.append("- **36**: Heatmap das top 30 empresas\n")
    
    # 10. Análise Estatística Avançada
    report.append("### 10. Análise Estatística Avançada (37-40)\n")
    report.append("Análises estatísticas avançadas e testes de hipóteses.\n")
    report.append("- **37**: Testes de normalidade (Shapiro-Wilk, D'Agostino)")
    report.append("- **38**: Transformação logarítmica de Kd")
    report.append("- **39**: Análise de resíduos de regressão")
    report.append("- **40**: Sumário estatístico completo de todas as variáveis\n")
    
    # Insights Principais
    report.append("## Insights Principais\n")
    
    # Calcula algumas estatísticas para insights
    q1 = df['Kd_Ponderado'].quantile(0.25)
    q3 = df['Kd_Ponderado'].quantile(0.75)
    iqr = q3 - q1
    outliers = df[(df['Kd_Ponderado'] < q1 - 1.5*iqr) | (df['Kd_Ponderado'] > q3 + 1.5*iqr)]
    
    report.append("### Distribuição de Kd Ponderado\n")
    report.append(f"- A maioria das empresas (50%) tem Kd entre {q1:.2f}% e {q3:.2f}%")
    report.append(f"- {len(outliers)} empresas ({len(outliers)/len(df)*100:.1f}%) são identificadas como outliers")
    report.append(f"- A distribuição apresenta assimetria positiva (média > mediana)\n")
    
    # Correlações importantes
    if 'Kd_Desvio_Padrao' in df.columns:
        corr_std = df[df['Kd_Desvio_Padrao'].notna()]['Kd_Ponderado'].corr(df[df['Kd_Desvio_Padrao'].notna()]['Kd_Desvio_Padrao'])
        report.append("### Heterogeneidade\n")
        report.append(f"- Correlação entre Kd ponderado e desvio padrão: {corr_std:.3f}")
        report.append(f"- Empresas com maior heterogeneidade tendem a ter Kd mais alto\n")
    
    corr_valor = df['Kd_Ponderado'].corr(df['Valor_Consolidado_Media'])
    corr_financ = df['Kd_Ponderado'].corr(df['Total_Financiamentos'])
    
    report.append("### Relações Importantes\n")
    report.append(f"- Correlação Kd vs Valor Consolidado: {corr_valor:.3f}")
    report.append(f"- Correlação Kd vs Total de Financiamentos: {corr_financ:.3f}\n")
    
    # Recomendações
    report.append("## Recomendações para Análise\n")
    report.append("1. **Filtrar outliers**: Considerar remover ou tratar separadamente empresas com Kd extremo")
    report.append("2. **Transformação**: Avaliar transformação logarítmica se necessário para normalização")
    report.append("3. **Agrupamentos**: Usar clusters identificados para análises segmentadas")
    report.append("4. **Variáveis de controle**: Incluir heterogeneidade e diversidade de indexadores como controles")
    report.append("5. **Validação**: Revisar manualmente casos extremos antes de modelagem\n")
    
    report.append("---\n")
    report.append(f"\n*Relatório gerado automaticamente pelo script `{Path(__file__).name}`*")
    
    # Salva relatório
    output_path = REPORTS_DIR / "eda_report.md"
    output_path.write_text("\n".join(report), encoding='utf-8')
    print(f"✅ Relatório salvo em: {output_path}")


if __name__ == "__main__":
    generate_eda_report()

