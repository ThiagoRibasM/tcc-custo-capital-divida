# Resumo Estatístico e Demográfico da Planilha de Modelagem

**Arquivo:** `emp_e_fin_novo_mercado_20250920.xlsx`  
**Data de análise:** 29 de novembro de 2025

---

## 📊 Visão Geral

- **Total de registros:** 937 linhas
- **Total de colunas:** 7
- **Completude geral:** 98.2%
- **Células preenchidas:** 6,441 / 6,559
- **Células vazias:** 118 (1.8%)

---

## 📐 Estrutura dos Dados

### Colunas Disponíveis

1. **Unnamed: 0** (int64) - Índice numérico
   - Preenchido: 100.0%
   - Valores únicos: 937

2. **Empresa** (object) - Nome da empresa
   - Preenchido: 100.0%
   - Valores únicos: 141 empresas

3. **descricao** (object) - Descrição do financiamento
   - Preenchido: 100.0%
   - Valores únicos: 455 descrições diferentes

4. **indexador** (object) - Indexador da taxa de juros
   - Preenchido: 99.6% (4 valores nulos)
   - Valores únicos: 777 indexadores diferentes

5. **vencimento** (object) - Data de vencimento
   - Preenchido: 91.1% (83 valores nulos)
   - Valores únicos: 541 vencimentos diferentes

6. **consolidado_2024** (object) - Valor consolidado em 2024
   - Preenchido: 96.7% (31 valores nulos)
   - Valores únicos: 798 valores diferentes

7. **arquivo_pdf** (object) - Nome do arquivo PDF de origem
   - Preenchido: 100.0%
   - Valores únicos: 120 arquivos diferentes

---

## 👥 Análise Demográfica

### Top 10 Empresas por Número de Financiamentos

| Empresa | Quantidade | % do Total |
|---------|-----------|------------|
| Rede D'Or São Luiz S.A. | 33 | 3.5% |
| Cosan S.A. | 33 | 3.5% |
| Vibra Energia S.A. | 26 | 2.8% |
| MOURA DUBEUX ENGENHARIA S/A | 23 | 2.5% |
| PBG S/A | 23 | 2.5% |
| CIA SANEAMENTO BASICO EST SAO PAULO | 23 | 2.5% |
| ENGIE BRASIL ENERGIA S.A. | 20 | 2.1% |
| Equatorial S.A. | 19 | 2.0% |
| Iochpe-Maxion S.A. | 19 | 2.0% |
| LOG-IN LOGISTICA INTERMODAL S.A. | 17 | 1.8% |

**Total de empresas únicas:** 141

### Top 10 Tipos de Financiamento (Descrição)

| Descrição | Quantidade | % do Total |
|-----------|-----------|------------|
| Capital de giro | 71 | 7.6% |
| BNDES | 27 | 2.9% |
| Financiamentos – SFH, debêntures e notas | 23 | 2.5% |
| Capital de Giro | 21 | 2.2% |
| NCE | 19 | 2.0% |
| FINEP | 17 | 1.8% |
| Finame | 15 | 1.6% |
| ACF | 11 | 1.2% |
| Loan 4131 | 10 | 1.1% |
| Finem | 10 | 1.1% |

**Total de descrições únicas:** 455

### Top 10 Indexadores Mais Frequentes

| Indexador | Quantidade | % do Total |
|-----------|-----------|------------|
| TJLP + 2% a.a. | 6 | 0.6% |
| CDI | 5 | 0.5% |
| 100% do DI 1,70% | 4 | 0.4% |
| CDI + 1,30% a.a. | 4 | 0.4% |
| Pré-fixado | 4 | 0.4% |
| CDI 1,65% | 4 | 0.4% |
| Não especificado | 4 | 0.4% |
| CDI 1,98% a.a. | 4 | 0.4% |
| IPCA TLP + 3,40% a.a. | 3 | 0.3% |
| CDI+1,80% a.a. | 3 | 0.3% |

**Total de indexadores únicos:** 777  
**Observação:** Alta diversidade de indexadores, indicando heterogeneidade nas condições de financiamento.

### Vencimentos

- **Valores únicos:** 541
- **Valores nulos:** 83 (8.9%)
- **Mais frequente:** "não especificado" (72 ocorrências - 7.7%)
- **Segundo mais frequente:** "vencimento até novembro de 2030" (59 ocorrências - 6.3%)

---

## 📊 Estatísticas Descritivas

### Índice Numérico (Unnamed: 0)

- **Média:** 468.00
- **Mediana:** 468.00
- **Desvio Padrão:** 270.63
- **Mínimo:** 0.00
- **Máximo:** 936.00
- **Q1 (25%):** 234.00
- **Q3 (75%):** 702.00
- **IQR:** 468.00

---

## ⚠️ Qualidade dos Dados

### Completude por Coluna

| Coluna | Preenchido | Nulos | % Preenchido |
|--------|-----------|-------|--------------|
| Unnamed: 0 | 937 | 0 | 100.0% |
| Empresa | 937 | 0 | 100.0% |
| descricao | 937 | 0 | 100.0% |
| indexador | 933 | 4 | 99.6% |
| vencimento | 854 | 83 | 91.1% |
| consolidado_2024 | 906 | 31 | 96.7% |
| arquivo_pdf | 937 | 0 | 100.0% |

### Observações sobre Qualidade

1. **Alta completude geral:** 98.2% das células estão preenchidas
2. **Vencimento:** Maior taxa de valores nulos (8.9%), com muitos registros marcados como "não especificado"
3. **Indexador:** Alta diversidade (777 valores únicos), indicando necessidade de padronização para análise
4. **Consolidado 2024:** 3.3% de valores nulos, mas muitos valores são "0" (57 ocorrências)

---

## 🔍 Insights Principais

1. **Diversidade de empresas:** 141 empresas diferentes, com distribuição relativamente equilibrada (top empresa tem apenas 3.5% dos registros)

2. **Concentração de tipos de financiamento:** "Capital de giro" é o tipo mais comum (7.6%), seguido por financiamentos do BNDES (2.9%)

3. **Heterogeneidade de indexadores:** 777 indexadores únicos sugerem grande variedade nas condições de financiamento, o que pode ser um desafio para análise

4. **Dados de vencimento:** 8.9% de valores nulos e muitos "não especificado" indicam necessidade de tratamento especial para esta variável

5. **Valores consolidados:** Presença significativa de valores zero (6.1%) pode indicar financiamentos já quitados ou valores não aplicáveis

---

## 📝 Recomendações para Modelagem

1. **Padronização de indexadores:** Criar categorias para os 777 indexadores únicos (ex: CDI-based, IPCA-based, Pré-fixado, etc.)

2. **Tratamento de vencimentos:** 
   - Criar variável binária para "vencimento especificado vs não especificado"
   - Extrair ano de vencimento quando disponível
   - Criar categorias de prazo (curto, médio, longo prazo)

3. **Valores consolidados:**
   - Converter para numérico
   - Tratar valores zero (verificar se são realmente zero ou missing)
   - Criar variáveis derivadas (log, categorias de valor)

4. **Variáveis categóricas:**
   - Considerar agrupamento de empresas por setor
   - Padronizar descrições de financiamento
   - Criar features derivadas (ex: tipo de financiador)

---

*Gerado automaticamente pelo script `src/utils/generate_statistical_summary.py`*

