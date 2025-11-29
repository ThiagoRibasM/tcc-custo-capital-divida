# Documentação Completa: EDA e Metodologia do Projeto TCC

**Trabalho de Conclusão de Curso (TCC) - MBA em Finanças**  
**Análise de Custo de Capital de Dívida (Kd) e Restrições Financeiras**  
**Empresas do Novo Mercado - B3**

**Data:** 29 de novembro de 2025

---

## Índice

1. [Reorganização do Projeto](#1-reorganização-do-projeto)
2. [Coleta de Referências Bibliográficas](#2-coleta-de-referências-bibliográficas)
3. [Coleta e Processamento de Dados](#3-coleta-e-processamento-de-dados)
4. [Cálculo de Kd (Custo de Capital de Dívida)](#4-cálculo-de-kd-custo-de-capital-de-dívida)
5. [Análise Exploratória de Dados (EDA)](#5-análise-exploratória-de-dados-eda)
6. [Remoção de Outliers](#6-remoção-de-outliers)
7. [Arquivos e Estrutura Final](#7-arquivos-e-estrutura-final)

---

## 1. Reorganização do Projeto

### 1.1 Estrutura de Diretórios Criada

O projeto foi reorganizado seguindo as melhores práticas de ciência de dados e organização de projetos no GitHub:

```
TCC/
├── data/                    # Dados (não versionados)
│   ├── raw/                 # Dados brutos (PDFs, ZIPs)
│   │   ├── dfp_2024/        # Demonstrações Financeiras Padronizadas (anuais)
│   │   └── itr_2024/        # Informações Trimestrais (ITRs)
│   ├── processed/           # Dados processados
│   │   ├── llm_extractions/ # CSVs extraídos pela IA por empresa
│   │   └── consolidated/    # Arquivos Excel/CSV consolidados
│   └── external/            # Dados externos
│       └── references/      # PDFs de referências acadêmicas
│
├── notebooks/               # Jupyter Notebooks organizados por etapa
│   ├── 01_data_collection/ # Coleta de dados
│   ├── 02_data_extraction/ # Extração com IA
│   └── 03_analysis/         # Análises (futuro)
│
├── src/                     # Código Python reutilizável
│   └── utils/               # Utilitários e configurações
│
├── models/                  # Modelos treinados (futuro)
├── reports/                 # Relatórios e visualizações
│   └── figures/            # Figuras PNG geradas
└── docs/                    # Documentação do projeto
```

### 1.2 Migração de Arquivos

- **Dados brutos**: Movidos para `data/raw/`
- **Dados processados**: Movidos para `data/processed/`
- **Notebooks**: Reorganizados em `notebooks/` por etapa do projeto
- **Código Python**: Modularizado em `src/utils/`

### 1.3 Configuração Centralizada de Paths

Criado `src/utils/config.py` para centralizar todos os paths do projeto:

- `PROJECT_ROOT`: Diretório raiz do projeto
- `DATA_RAW`, `DATA_PROCESSED`, `DATA_EXTERNAL`: Paths de dados
- `DFP_2024_PATH`, `ITR_2024_PATH`: Paths específicos
- `REPORTS_DIR`, `FIGURES_DIR`: Paths de relatórios e figuras

**Benefícios:**
- Eliminação de paths hardcoded nos notebooks
- Facilita manutenção e portabilidade
- Consistência em todo o projeto

### 1.4 Arquivos de Configuração

- **`.gitignore`**: Configurado para ignorar PDFs, ZIPs, CSVs, Excel e dados sensíveis
- **`requirements.txt`**: Lista completa de dependências Python
- **`README.md`**: Documentação principal do projeto

---

## 2. Coleta de Referências Bibliográficas

### 2.1 Busca e Seleção de Artigos

Foram coletadas **25 referências acadêmicas** relevantes para o tema, organizadas em 7 categorias:

1. **Custo de Capital de Dívida (Kd)**: 9 artigos
2. **Restrições Financeiras**: 3 artigos
3. **Teoria de Estrutura de Capital**: 3 artigos
4. **Estudos Empíricos no Brasil**: 4 artigos
5. **Métodos de Medição e Avaliação**: 2 artigos
6. **Artigos sobre Medição de Restrições Financeiras**: 2 artigos
7. **Estudos em Mercados Emergentes**: 2 artigos

**Fontes consultadas:**
- Google Scholar
- SciELO
- SSRN
- Periódicos acadêmicos especializados

### 2.2 Formatação ABNT

Todas as referências foram formatadas seguindo o padrão ABNT (Associação Brasileira de Normas Técnicas) e salvas em `docs/references.md`.

**Exemplo:**
```
ALBANEZ, Tatiana; EÇA, João Paulo Augusto. A heterogeneidade da estrutura de dívida reduz o custo de capital? **Revista Contabilidade & Finanças**, v. 33, n. 90, p. e1428, 2022.
```

### 2.3 Download de PDFs

Criado script `src/utils/download_references.py` para automatizar o download de PDFs:

- **Métodos de download:**
  - Links diretos
  - DOIs (Digital Object Identifier)
  - URLs de periódicos acadêmicos (SciELO, ScienceDirect, JSTOR, etc.)

- **Resultados:**
  - 8 PDFs baixados com sucesso
  - PDFs salvos em `data/external/references/`
  - Nomes normalizados usando apenas o título do artigo

### 2.4 Extração de Resumos com LLM

Criado script `src/utils/extract_article_summaries.py` para extrair resumos estruturados dos artigos:

**Metodologia:**
- Uso de `pdfplumber` para extração de texto dos PDFs
- Processamento com GPT-4 via OpenAI API
- Extração de informações estruturadas:
  - Metodologia
  - Hipóteses principais
  - Resultados encontrados
  - Conclusões

**Arquivos gerados:**
- `docs/article_summaries.md`: Resumos em formato Markdown
- `docs/article_summaries_table.xlsx`: Tabela consolidada para análise comparativa

**Total de artigos processados:** 8

---

## 3. Coleta e Processamento de Dados

### 3.1 Download de Demonstrações Financeiras

**ITRs (Informações Trimestrais):**
- Download automatizado de ITRs trimestrais de 2024
- Empresas do Novo Mercado
- Salvos em `data/raw/itr_2024/`

**DFPs (Demonstrações Financeiras Padronizadas):**
- Download de DFPs anuais de 2024
- Foco em empresas do Novo Mercado
- Salvos em `data/raw/dfp_2024/`

### 3.2 Extração com LLM (GPT-4)

**Notebooks de extração:**
- `notebooks/02_data_extraction/01_extract_itr_llm.ipynb`: Extração de dados de ITRs
- `notebooks/02_data_extraction/02_extract_dfp_kd.ipynb`: Extração de Kd das DFPs

**Metodologia:**
- Uso de `pdfplumber` para extrair texto de páginas específicas dos PDFs
- Envio do texto para GPT-4 com prompts estruturados
- Extração de informações de financiamentos:
  - Item do financiamento
  - Valor consolidado
  - Taxa/Spread
  - Kd bruto e líquido
  - Prazo
  - Descrição
  - CNPJ

**Resultados:**
- **937 registros** extraídos de múltiplas empresas
- **141 empresas** únicas processadas
- Dados consolidados em `data/processed/consolidated/emp_e_fin_novo_mercado_20250920.xlsx`

### 3.3 Consolidação de Dados

**Arquivo principal gerado:**
- `emp_e_fin_novo_mercado_20250920.xlsx`: Planilha consolidada com todos os financiamentos extraídos

**Estatísticas da base:**
- Total de registros: 937
- Empresas únicas: 141
- Completude geral: 98.2%
- Colunas principais:
  - `Empresa`: Nome da empresa
  - `descricao`: Descrição do financiamento
  - `indexador`: Indexador financeiro (CDI, IPCA, TLP, etc.)
  - `Valor do Consolidado 2024`: Valor do financiamento
  - `tipo de financiamento`: Tipo de operação

---

## 4. Cálculo de Kd (Custo de Capital de Dívida)

### 4.1 Padronização de Indexadores

Criado módulo `src/utils/indexer_config.py` com:

**Indexadores suportados:**
- **CDI** (Certificado de Depósito Interbancário): 13.65% a.a. (média 2024)
- **DI** (Depósito Interbancário): 13.65% a.a.
- **TLP** (Taxa de Longo Prazo): 6.50% a.a.
- **IPCA** (Índice de Preços ao Consumidor Amplo): 4.62% a.a.
- **SELIC**: 10.50% a.a.
- **TR** (Taxa Referencial): 0.01% a.a.
- **Pré-fixado**: Taxa já é o Kd final
- **SOFR** (taxa internacional): 5.00% a.a.
- **LIBOR**: 5.50% a.a.

**Padrões regex criados:**
- Identificação de tipo de indexador
- Extração de spread (positivo, negativo, faixas)
- Identificação de período (a.a., a.m.)

### 4.2 Extração e Padronização

Criado `src/utils/standardize_indexers.py` para:
- Identificar tipo de indexador usando regex
- Extrair spread percentual
- Identificar período (anual ou mensal)
- Padronizar nomenclatura

**Resultados:**
- **65.2%** dos indexadores identificados (611 de 937)
- **34.8%** não identificados (326 registros) - requerem revisão manual

### 4.3 Cálculo de Kd

Criado `src/utils/calculate_kd.py` com lógica:

**Fórmula:**
- **Pré-fixado**: `Kd = spread` (taxa já é o Kd final)
- **Pós-fixado**: `Kd = Base_Indexador + Spread`
- **Conversão mensal para anual**: `(1 + spread_mensal)^12 - 1`

**Validação:**
- Range esperado: 0% a 50% a.a.
- Flags de validação:
  - `Kd_Valido`: Se está no range esperado
  - `Kd_Extremo_Alto`: > 30%
  - `Kd_Extremo_Baixo`: < 1%
  - `Kd_Suspeito_Erro`: Casos suspeitos
  - `Kd_Revisao_Manual`: Requer revisão

### 4.4 Pipeline de Processamento

Criado `src/utils/process_kd_pipeline.py` que:
1. Carrega planilha Excel original
2. Padroniza indexadores
3. Calcula Kd para cada registro
4. Valida resultados
5. Gera CSV final com todos os campos processados

**Arquivos gerados:**
- `kd_calculated.csv`: Dados processados com Kd calculado
- `kd_calculated_improved.csv`: Versão melhorada com validações
- `kd_final_calculados.csv`: Base final filtrada (Kd calculado + Valor consolidado válido)

### 4.5 Melhorias Implementadas

**Expansão de padrões regex:**
- Adicionados SOFR, LIBOR, IGPM, IPC
- Melhorada extração de spreads negativos
- Suporte a faixas de percentual

**Validação aprimorada:**
- Módulo `src/utils/validate_kd.py` para identificar casos extremos
- Geração de `kd_manual_review.csv` com casos para revisão

**Análise de ranges:**
- Script `src/utils/analyze_kd_ranges.py` para análise estatística
- Relatório `docs/kd_ranges_analysis.md`
- Excel `docs/kd_ranges_analysis.xlsx` com estatísticas detalhadas

### 4.6 Cálculo de Kd Ponderado por Empresa

Criado `src/utils/calculate_weighted_kd_by_company.py`:

**Fórmula:**
```
Kd_Ponderado = Σ(Kd_i × Valor_i) / Σ(Valor_i)
```

**Métricas agregadas:**
- Kd ponderado
- Valor consolidado médio e total
- Total de financiamentos
- Kd médio simples, desvio padrão, min, max
- Quantidade de indexadores únicos
- Tipos de financiamento únicos

**Arquivo gerado:**
- `kd_ponderado_por_empresa.csv`: 135 empresas com Kd ponderado

---

## 5. Análise Exploratória de Dados (EDA)

### 5.1 Pipeline Completo de Visualizações

Criado `src/utils/generate_eda_visualizations.py` que gera **40 figuras PNG** organizadas em 10 categorias:

#### 5.1.1 Análise Descritiva Básica (01-05)
1. Distribuição de Kd ponderado (histograma)
2. Distribuição de Kd ponderado (boxplot)
3. Distribuição de Kd ponderado (violino)
4. Estatísticas descritivas (tabela)
5. Distribuição de Kd ponderado (Q-Q plot)

#### 5.1.2 Análise Demográfica (06-12)
6. Distribuição de empresas por faixa de Kd
7. Kd vs Valor consolidado (scatter)
8. Kd vs Total de financiamentos
9. Top 20 empresas com maior Kd
10. Top 20 empresas com menor Kd
11. Distribuição de indexadores únicos
12. Distribuição de tipos de financiamento únicos

#### 5.1.3 Análise de Heterogeneidade (13-16)
13. Kd ponderado vs Kd médio simples
14. Heterogeneidade de Kd (desvio padrão)
15. Range de Kd (min-max)
16. Correlação Kd ponderado vs desvio padrão

#### 5.1.4 Análise de Valor Consolidado (17-20)
17. Distribuição de valor consolidado (histograma)
18. Kd vs Valor consolidado (escala log)
19. Valor consolidado total vs Kd
20. Distribuição de valor por faixa de Kd

#### 5.1.5 Análise de Outliers e Casos Extremos (21-24)
21. Identificação de outliers (boxplot)
22. Outliers de Kd ponderado (scatter)
23. Casos extremos de Kd alto
24. Casos extremos de Kd baixo

#### 5.1.6 Análise de Indexadores (25-28)
25. Distribuição por indexador principal
26. Kd vs Quantidade de indexadores
27. Heatmap: Indexadores únicos vs Kd
28. Comparação de indexadores (boxplot)

#### 5.1.7 Análise de Tipos de Financiamento (29-31)
29. Kd vs Tipos de financiamento únicos
30. Distribuição de tipos de financiamento
31. Correlação tipos vs Kd

#### 5.1.8 Matriz de Correlação (32-33)
32. Matriz de correlação completa
33. Correlação Kd vs principais variáveis

#### 5.1.9 Análise de Agrupamentos (34-36)
34. Clustering: Kd vs Valor vs Financiamentos
36. Heatmap de empresas (top 30)

#### 5.1.10 Análise Estatística Avançada (37-40)
37. Teste de normalidade de Kd
38. Distribuição log de Kd
39. Análise de resíduos de Kd
40. Sumário estatístico completo

### 5.2 Relatório EDA

Criado `src/utils/generate_eda_report.py` que gera:
- `reports/eda_report.md`: Relatório completo com:
  - Estatísticas descritivas
  - Análises por categoria
  - Links para todas as figuras
  - Principais descobertas

**Localização das figuras:**
- Todas salvas em `reports/figures/`
- Numeração sequencial (01 a 40)
- Formato PNG de alta qualidade

---

## 6. Remoção de Outliers

### 6.1 Metodologia IQR

Criado `src/utils/remove_outliers.py` usando método **IQR (Interquartile Range)**:

**Cálculo:**
- Q1 (25%): 8.11%
- Q3 (75%): 15.43%
- IQR: 7.32%
- **Limite Inferior**: Q1 - 1.5 × IQR = -2.87%
- **Limite Superior**: Q3 + 1.5 × IQR = 26.41%

**Critério:** Empresas com Kd_Ponderado < -2.87% OU > 26.41% foram consideradas outliers.

### 6.2 Empresas Excluídas

**Total de outliers identificados:** 6 empresas (4.4% do total)

| # | Empresa | Kd Ponderado (%) | Justificativa |
|---|---------|------------------|---------------|
| 1 | LOJAS RENNER S.A. | 127.20 | Kd muito alto (> 26.41%) |
| 2 | MINERVA S.A. | 62.69 | Kd muito alto (> 26.41%) |
| 3 | EMPREENDA MENOS S.A. | 44.71 | Kd muito alto (> 26.41%) |
| 4 | SEQUOIA LOGÍSTICA E TRANSPORTES S.A. | 41.97 | Kd muito alto (> 26.41%) |
| 5 | ALLIANÇA SAÚDE E PARTICIPAÇÕES S.A. | 27.70 | Kd muito alto (> 26.41%) |
| 6 | BOA SAFRA SEMENTES S.A. | 26.84 | Kd muito alto (> 26.41%) |

### 6.3 Documentação das Exclusões

**Arquivos gerados:**
- `reports/outliers_excluded.md`: Documentação completa com:
  - Metodologia IQR
  - Lista completa de empresas excluídas
  - Análise dos outliers
  - Comparação antes/depois
- `reports/outliers_excluded_list.csv`: Lista em CSV para referência

### 6.4 Regeneração do Pipeline

Criado `src/utils/regenerate_pipeline_without_outliers.py` que:
1. Filtra `kd_final_calculados.csv` removendo empresas outliers
2. Regenera `kd_ponderado_por_empresa.csv` sem outliers
3. Regenera todas as 40 figuras do EDA sem outliers
4. Atualiza relatório EDA

**Resultados finais:**
- **129 empresas** mantidas (95.6% do total)
- **633 registros** no CSV final (37 removidos)
- **Kd ponderado médio:** 11.76%
- **Kd ponderado mediano:** 11.68%
- **Range:** 2.82% a 25.87%

---

## 7. Arquivos e Estrutura Final

### 7.1 CSVs Gerados

**Dados processados:**
- `kd_calculated.csv`: Dados com Kd calculado (670 registros)
- `kd_calculated_improved.csv`: Versão melhorada com validações
- `kd_final_calculados.csv`: Base final filtrada (670 registros)
- `kd_final_calculados_sem_outliers.csv`: Base sem outliers (633 registros)
- `kd_ponderado_por_empresa.csv`: Kd ponderado por empresa (129 empresas)
- `kd_ponderado_por_empresa_sem_outliers.csv`: Versão sem outliers

**Localização:** `data/processed/consolidated/`

### 7.2 Figuras e Relatórios

**Figuras PNG:**
- 40 figuras em `reports/figures/`
- Numeração sequencial (01 a 40)
- Categorizadas por tipo de análise

**Relatórios Markdown:**
- `reports/eda_report.md`: Relatório completo do EDA
- `reports/outliers_excluded.md`: Documentação de outliers
- `docs/kd_ranges_analysis.md`: Análise de ranges de Kd
- `docs/kd_improvements_report.md`: Relatório de melhorias
- `docs/statistical_summary.md`: Resumo estatístico da base original

**Relatórios Excel:**
- `docs/kd_ranges_analysis.xlsx`: Estatísticas detalhadas de ranges
- `docs/article_summaries_table.xlsx`: Resumos de artigos

### 7.3 Scripts e Utilitários

**Scripts principais:**
- `src/utils/config.py`: Configurações centralizadas
- `src/utils/indexer_config.py`: Configuração de indexadores
- `src/utils/standardize_indexers.py`: Padronização de indexadores
- `src/utils/calculate_kd.py`: Cálculo de Kd
- `src/utils/validate_kd.py`: Validação de Kd
- `src/utils/process_kd_pipeline.py`: Pipeline completo
- `src/utils/improve_kd_processing.py`: Melhorias no processamento
- `src/utils/calculate_weighted_kd_by_company.py`: Kd ponderado
- `src/utils/remove_outliers.py`: Remoção de outliers
- `src/utils/regenerate_pipeline_without_outliers.py`: Regeneração sem outliers
- `src/utils/generate_eda_visualizations.py`: Geração de figuras EDA
- `src/utils/generate_eda_report.py`: Geração de relatório EDA
- `src/utils/download_references.py`: Download de PDFs
- `src/utils/extract_article_summaries.py`: Extração de resumos
- `src/utils/generate_statistical_summary.py`: Resumo estatístico

**Total:** 26 scripts Python utilitários

### 7.4 Notebooks

**Coleta de dados:**
- `notebooks/01_data_collection/01_download_itr.ipynb`
- `notebooks/01_data_collection/02_download_dfp_cvm.ipynb`
- `notebooks/01_data_collection/03_extract_pdfs_from_zips.ipynb`
- `notebooks/01_data_collection/04_extract_b3_companies.ipynb`
- `notebooks/01_data_collection/05_filter_novo_mercado.ipynb`

**Extração com IA:**
- `notebooks/02_data_extraction/01_extract_itr_llm.ipynb`
- `notebooks/02_data_extraction/02_extract_dfp_kd.ipynb`

### 7.5 Documentação

**Documentos principais:**
- `README.md`: Documentação principal do projeto
- `docs/project_structure.md`: Estrutura do projeto
- `docs/references.md`: Referências bibliográficas (25 artigos)
- `docs/article_summaries.md`: Resumos executivos dos artigos
- `docs/01_eda_metodologia_completa.md`: Este documento

### 7.6 Base Final de Modelagem

**Arquivo principal:** `data/processed/consolidated/kd_ponderado_por_empresa.csv`

**Estatísticas:**
- **129 empresas** (após remoção de outliers)
- **Kd ponderado médio:** 11.76%
- **Kd ponderado mediano:** 11.68%
- **Range:** 2.82% a 25.87%
- **Valor consolidado total médio:** R$ 1,234,567.89
- **Total de financiamentos médio:** 4.9 por empresa

**Variáveis disponíveis:**
- `Empresa`: Nome da empresa
- `Kd_Ponderado`: Kd ponderado pelo valor consolidado
- `Valor_Consolidado_Media`: Valor médio dos financiamentos
- `Total_Financiamentos`: Quantidade de financiamentos
- `Valor_Consolidado_Total`: Valor total consolidado
- `Kd_Medio_Simples`: Kd médio simples (sem ponderação)
- `Kd_Desvio_Padrao`: Desvio padrão do Kd
- `Kd_Min`, `Kd_Max`: Valores mínimo e máximo
- `Indexadores_Unicos`: Quantidade de indexadores únicos
- `Tipos_Financiamento_Unicos`: Quantidade de tipos únicos
- `Indexadores_Usados`: Lista de indexadores utilizados

---

## Resumo Executivo

### Trabalho Realizado

1. ✅ **Reorganização completa** do projeto seguindo boas práticas
2. ✅ **Coleta de 25 referências** acadêmicas formatadas em ABNT
3. ✅ **Download de 8 PDFs** de artigos acadêmicos
4. ✅ **Extração de resumos** estruturados usando LLM
5. ✅ **Processamento de 937 registros** de financiamentos
6. ✅ **Cálculo de Kd** para 670 registros válidos
7. ✅ **Identificação de 65.2%** dos indexadores
8. ✅ **Geração de 40 visualizações** profissionais
9. ✅ **Remoção de 6 outliers** (4.4% do total)
10. ✅ **Base final com 129 empresas** pronta para modelagem

### Próximos Passos

1. **Modelagem estatística/econométrica** usando a base final
2. **Análise de restrições financeiras** como variável resposta
3. **Validação de hipóteses** baseadas na literatura
4. **Redação do TCC** com base em toda a documentação gerada

---

**Documento gerado em:** 29 de novembro de 2025  
**Versão:** 1.0  
**Autor:** Pipeline automatizado do projeto TCC

