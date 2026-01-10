# Relatório de Análise Exploratória de Dados (EDA)

**Data:** 29 de November de 2025
**Total de empresas analisadas:** 129

---

## Resumo Executivo

Este relatório apresenta uma análise exploratória completa dos dados de Kd ponderado por empresa.
Foram geradas **40 visualizações** em formato PNG de alta resolução (300 DPI), organizadas em 10 categorias de análise.

### Estatísticas Principais

- **Kd Ponderado Médio:** 11.76% a.a.
- **Kd Ponderado Mediano:** 11.68% a.a.
- **Desvio Padrão:** 4.50%
- **Range:** 2.82% - 25.87%
- **Valor Consolidado Médio:** R$ 314,414.50
- **Total de Financiamentos Médio:** 4.9

## Tabela de Referência Rápida das Figuras

| # | Nome do Arquivo | Descrição | Categoria |
|---|----------------|-----------|------------|
| 01 | `01_distribuicao_kd_ponderado_histograma.png` | Histograma da distribuição de Kd ponderado | Análise Descritiva Básica |
| 02 | `02_distribuicao_kd_ponderado_boxplot.png` | Boxplot de Kd ponderado | Análise Descritiva Básica |
| 03 | `03_distribuicao_kd_ponderado_violino.png` | Violin plot (distribuição + densidade) | Análise Descritiva Básica |
| 04 | `04_estatisticas_descritivas_tabela.png` | Tabela com estatísticas descritivas | Análise Descritiva Básica |
| 05 | `05_distribuicao_kd_ponderado_qqplot.png` | Q-Q plot para verificar normalidade | Análise Descritiva Básica |
| 06 | `06_distribuicao_empresas_por_faixa_kd.png` | Quantidade de empresas por faixa de Kd | Análise Demográfica |
| 07 | `07_kd_vs_valor_consolidado_scatter.png` | Scatter plot Kd vs Valor Consolidado | Análise Demográfica |
| 08 | `08_kd_vs_total_financiamentos.png` | Kd vs Quantidade de Financiamentos | Análise Demográfica |
| 09 | `09_top_20_empresas_kd_maior.png` | Top 20 empresas com maior Kd | Análise Demográfica |
| 10 | `10_top_20_empresas_kd_menor.png` | Top 20 empresas com menor Kd | Análise Demográfica |
| 11 | `11_distribuicao_indexadores_unicos.png` | Distribuição de indexadores únicos por empresa | Análise Demográfica |
| 12 | `12_distribuicao_tipos_financiamento_unicos.png` | Distribuição de tipos de financiamento únicos | Análise Demográfica |
| 13 | `13_kd_ponderado_vs_kd_medio_simples.png` | Comparação Kd ponderado vs médio simples | Análise de Heterogeneidade |
| 14 | `14_heterogeneidade_kd_desvio_padrao.png` | Análise de heterogeneidade (desvio padrão) | Análise de Heterogeneidade |
| 15 | `15_range_kd_min_max.png` | Range de Kd (min vs max) por empresa | Análise de Heterogeneidade |
| 16 | `16_correlacao_kd_ponderado_desvio.png` | Correlação entre Kd ponderado e desvio padrão | Análise de Heterogeneidade |
| 17 | `17_distribuicao_valor_consolidado_histograma.png` | Distribuição do valor consolidado médio | Análise de Valor Consolidado |
| 18 | `18_kd_vs_valor_consolidado_log.png` | Scatter plot com escala logarítmica | Análise de Valor Consolidado |
| 19 | `19_valor_consolidado_total_vs_kd.png` | Valor consolidado total vs Kd | Análise de Valor Consolidado |
| 20 | `20_distribuicao_valor_por_faixa_kd.png` | Distribuição de valor por faixa de Kd | Análise de Valor Consolidado |
| 21 | `21_identificacao_outliers_boxplot.png` | Boxplot com outliers destacados | Análise de Outliers |
| 22 | `22_outliers_kd_ponderado_scatter.png` | Scatter plot com outliers identificados | Análise de Outliers |
| 23 | `23_casos_extremos_kd_alto.png` | Análise de casos com Kd muito alto (>30%) | Análise de Outliers |
| 24 | `24_casos_extremos_kd_baixo.png` | Análise de casos com Kd muito baixo (<5%) | Análise de Outliers |
| 25 | `25_distribuicao_por_indexador_principal.png` | Distribuição de Kd por indexador mais usado | Análise de Indexadores |
| 26 | `26_kd_vs_quantidade_indexadores.png` | Kd vs quantidade de indexadores únicos | Análise de Indexadores |
| 27 | `27_heatmap_indexadores_unicos_vs_kd.png` | Heatmap de indexadores vs Kd | Análise de Indexadores |
| 28 | `28_comparacao_indexadores_boxplot.png` | Boxplot comparativo por indexador | Análise de Indexadores |
| 29 | `29_kd_vs_tipos_financiamento_unicos.png` | Kd vs quantidade de tipos únicos | Análise de Tipos de Financiamento |
| 30 | `30_distribuicao_tipos_financiamento.png` | Distribuição de tipos de financiamento | Análise de Tipos de Financiamento |
| 31 | `31_correlacao_tipos_vs_kd.png` | Correlação entre tipos únicos e Kd | Análise de Tipos de Financiamento |
| 32 | `32_matriz_correlacao_completa.png` | Matriz de correlação de todas as variáveis numéricas | Matriz de Correlação |
| 33 | `33_correlacao_kd_principais_variaveis.png` | Correlação de Kd com principais variáveis | Matriz de Correlação |
| 34 | `34_clustering_kd_valor_financiamentos.png` | Análise de clusters (K-means) | Análise de Agrupamentos |
| 35 | `35_dendrograma_empresas_similares.png` | Dendrograma de empresas similares | Análise de Agrupamentos |
| 36 | `36_heatmap_empresas_top30.png` | Heatmap das top 30 empresas | Análise de Agrupamentos |
| 37 | `37_teste_normalidade_kd.png` | Testes de normalidade (Shapiro-Wilk, Q-Q plot) | Análise Estatística Avançada |
| 38 | `38_distribuicao_log_kd.png` | Distribuição do log de Kd | Análise Estatística Avançada |
| 39 | `39_analise_residuos_kd.png` | Análise de resíduos (regressão) | Análise Estatística Avançada |
| 40 | `40_sumario_estatistico_completo.png` | Sumário estatístico completo | Análise Estatística Avançada |

## Descrições Detalhadas por Categoria

### 1. Análise Descritiva Básica (01-05)

Esta seção apresenta a distribuição fundamental da variável resposta (Kd ponderado).

- **01**: Histograma mostra a distribuição de frequência do Kd ponderado
- **02**: Boxplot identifica quartis, mediana e outliers
- **03**: Violin plot combina distribuição e densidade
- **04**: Tabela com estatísticas descritivas completas
- **05**: Q-Q plot verifica se a distribuição segue uma normal

### 2. Análise Demográfica (06-12)

Análise das características demográficas das empresas e seus financiamentos.

- **06**: Distribuição de empresas por faixas de Kd
- **07**: Relação entre Kd e valor consolidado (tamanho do financiamento)
- **08**: Relação entre Kd e quantidade de financiamentos
- **09-10**: Top 20 empresas com maior e menor Kd
- **11-12**: Diversidade de indexadores e tipos de financiamento

### 3. Análise de Heterogeneidade (13-16)

Análise da variabilidade e heterogeneidade do Kd dentro de cada empresa.

- **13**: Comparação entre Kd ponderado e médio simples
- **14**: Heterogeneidade medida pelo desvio padrão
- **15**: Range de Kd (mínimo vs máximo) por empresa
- **16**: Correlação entre Kd ponderado e heterogeneidade

### 4. Análise de Valor Consolidado (17-20)

Análise do valor consolidado e sua relação com o Kd.

- **17**: Distribuição do valor consolidado médio
- **18**: Relação Kd vs valor com escala logarítmica
- **19**: Valor consolidado total vs Kd
- **20**: Distribuição de valor por faixa de Kd

### 5. Análise de Outliers e Casos Extremos (21-24)

Identificação e análise de casos extremos e outliers.

- **21**: Boxplot com outliers destacados
- **22**: Scatter plot com outliers identificados
- **23**: Empresas com Kd muito alto (>30%)
- **24**: Empresas com Kd muito baixo (<5%)

### 6. Análise de Indexadores (25-28)

Análise da relação entre indexadores financeiros e Kd.

- **25**: Distribuição por indexador principal
- **26**: Kd vs quantidade de indexadores únicos
- **27**: Heatmap de indexadores vs Kd
- **28**: Comparação de Kd por indexador

### 7. Análise de Tipos de Financiamento (29-31)

Análise da diversidade de tipos de financiamento.

- **29**: Kd vs tipos de financiamento únicos
- **30**: Distribuição de tipos de financiamento
- **31**: Correlação entre tipos únicos e Kd

### 8. Matriz de Correlação (32-33)

Análise de correlações entre todas as variáveis.

- **32**: Matriz de correlação completa
- **33**: Correlação de Kd com principais variáveis

### 9. Análise de Agrupamentos (34-36)

Identificação de grupos similares de empresas.

- **34**: Clustering K-means (Kd, Valor, Financiamentos)
- **35**: Dendrograma de empresas similares
- **36**: Heatmap das top 30 empresas

### 10. Análise Estatística Avançada (37-40)

Análises estatísticas avançadas e testes de hipóteses.

- **37**: Testes de normalidade (Shapiro-Wilk, D'Agostino)
- **38**: Transformação logarítmica de Kd
- **39**: Análise de resíduos de regressão
- **40**: Sumário estatístico completo de todas as variáveis

## Insights Principais

### Distribuição de Kd Ponderado

- A maioria das empresas (50%) tem Kd entre 8.05% e 15.22%
- 0 empresas (0.0%) são identificadas como outliers
- A distribuição apresenta assimetria positiva (média > mediana)

### Heterogeneidade

- Correlação entre Kd ponderado e desvio padrão: 0.073
- Empresas com maior heterogeneidade tendem a ter Kd mais alto

### Relações Importantes

- Correlação Kd vs Valor Consolidado: 0.037
- Correlação Kd vs Total de Financiamentos: 0.147

## Recomendações para Análise

1. **Filtrar outliers**: Considerar remover ou tratar separadamente empresas com Kd extremo
2. **Transformação**: Avaliar transformação logarítmica se necessário para normalização
3. **Agrupamentos**: Usar clusters identificados para análises segmentadas
4. **Variáveis de controle**: Incluir heterogeneidade e diversidade de indexadores como controles
5. **Validação**: Revisar manualmente casos extremos antes de modelagem

---


*Relatório gerado automaticamente pelo script `generate_eda_report.py`*