# Análise de Validação e Fragilidades dos Dados Financeiros

**Data:** 29/11/2025

## Resumo Executivo

A validação dos dados financeiros extraídos identificou **233 problemas** em **99 empresas** (de 100 total). A maioria dos problemas são de **severidade média ou baixa**, indicando que os dados são utilizáveis, mas requerem atenção em alguns aspectos.

### Principais Achados

- ✅ **Completude excelente:** 100% dos campos críticos preenchidos
- ⚠️ **Inconsistências estruturais:** 99 casos de Passivo Total ≠ PC + PNC
- ⚠️ **Inconsistências de dívida:** 48 casos de Dívida Total ≠ CP + LP
- ℹ️ **Outliers:** 74 casos (esperado em dados financeiros reais)
- ❌ **Casos críticos:** 5 casos de alta severidade

---

## 1. Inconsistências de Passivo (99 casos - Severidade: Média)

### Problema

**Passivo Total ≠ Passivo Circulante + Passivo Não Circulante**

- **Total de casos:** 99 empresas (99%)
- **Diferença média:** ~40%
- **Diferença máxima:** 623% (PDG REALTY)

### Possíveis Causas

1. **Classificação Contábil Diferente:**
   - O "Passivo Total" extraído pode incluir o Patrimônio Líquido
   - Em alguns PDFs, o balanço pode apresentar "Passivo Total" como sinônimo de "Total do Passivo + PL"
   - O LLM pode ter extraído o valor errado da linha

2. **Estrutura do PDF:**
   - Diferentes formatos de apresentação dos balanços
   - Alguns PDFs podem ter o PL incluído no Passivo Total
   - Outros podem ter rubricas adicionais não capturadas

3. **Erro na Extração:**
   - O LLM pode ter confundido linhas do balanço
   - Valores podem ter sido extraídos de seções diferentes

### Impacto

- **Baixo para modelagem:** A inconsistência não afeta diretamente os indicadores calculados (alavancagem, liquidez, etc.)
- **Médio para validação:** Dificulta verificar a consistência dos dados extraídos
- **Recomendação:** Usar `Ativo_Total` como referência principal (mais confiável)

---

## 2. Inconsistências de Dívida (48 casos - Severidade: Baixa)

### Problema

**Dívida Total ≠ Dívida Curto Prazo + Dívida Longo Prazo**

- **Total de casos:** 48 empresas (48%)
- **Diferença média:** ~60%
- **Diferença máxima:** 236% (Melnick)

### Possíveis Causas

1. **Classificações Adicionais:**
   - Dívida Total pode incluir outras rubricas (ex: Dívida com Acionistas, Dívida em Moeda Estrangeira)
   - Alguns PDFs podem apresentar dívidas em rubricas não capturadas
   - Dívidas podem estar classificadas de forma diferente

2. **Forma de Apresentação:**
   - Alguns PDFs podem apresentar apenas "Empréstimos e Financiamentos Total"
   - Outros podem ter subdivisões adicionais
   - Dívidas podem estar em notas explicativas

3. **Extração Parcial:**
   - O LLM pode ter extraído apenas parte das dívidas
   - Valores podem estar em seções diferentes do PDF

### Impacto

- **Médio para modelagem:** Pode afetar cálculos de alavancagem se usar Dívida Total
- **Recomendação:** Usar `Divida_Curto_Prazo + Divida_Longo_Prazo` como proxy mais confiável

---

## 3. Outliers (74 casos - Severidade: Média)

### Problema

Valores fora do range IQR (Interquartile Range) usando método 1.5 × IQR.

### Campos Afetados

- `Ativo_Total`: Empresas muito grandes (ex: Rede D'Or, Cosan, Equatorial)
- `Receita_Liquida`: Empresas com receitas muito altas
- `Divida_Total`: Empresas com dívidas muito altas
- `Lucro_Liquido`: Empresas com lucros/prejuízos extremos

### Análise

**Isso é esperado e normal em dados financeiros reais:**
- Empresas de diferentes tamanhos (pequenas, médias, grandes)
- Setores diferentes (varejo, energia, construção)
- Ciclos econômicos diferentes

### Impacto

- **Baixo para modelagem:** Outliers podem ser tratados estatisticamente (log transform, winsorization)
- **Recomendação:** Manter outliers, mas documentar e considerar transformações para modelagem

---

## 4. Valores Fora do Range Esperado (5 casos - Severidade: Alta)

### Problema

Valores que estão fora dos ranges esperados para indicadores financeiros.

### Casos Identificados

1. **Rede D'Or São Luiz S.A.:**
   - `Divida_Total`: R$ 649.958.696 mil (muito alto)
   - **Análise:** Pode ser erro de extração ou empresa com dívida realmente muito alta

2. **Outros casos:** Valores extremos que podem indicar erro de extração

### Impacto

- **Alto para modelagem:** Valores extremos podem distorcer análises
- **Recomendação:** Revisar manualmente esses casos e validar com os PDFs originais

---

## 5. Dados Ausentes (2 casos - Severidade: Média)

### Problema

Campos importantes não foram extraídos para algumas empresas.

### Impacto

- **Médio para modelagem:** Pode limitar análises para essas empresas específicas
- **Recomendação:** Revisar manualmente os PDFs dessas empresas

---

## 6. Casos Críticos (5 casos - Severidade: Alta)

### Problema

Valores que claramente indicam erro de extração ou dados inconsistentes.

### Exemplos

1. **Valores negativos em campos que não deveriam ser negativos**
2. **Valores fora de ranges físicos possíveis**
3. **Inconsistências matemáticas graves**

### Impacto

- **Alto para modelagem:** Esses casos devem ser revisados antes de usar em modelagem
- **Recomendação:** Revisar manualmente e corrigir ou excluir esses casos

---

## Fragilidades Identificadas

### 1. Fragilidade na Extração de Passivo Total

**Problema:** O LLM pode estar extraindo valores incorretos ou de linhas diferentes.

**Solução:**
- Usar `Ativo_Total` como referência principal (mais confiável)
- Validar que `Ativo_Total = Passivo_Total + Patrimonio_Liquido` (ou similar)
- Se não bater, usar `Ativo_Total - Patrimonio_Liquido` como proxy de Passivo

### 2. Fragilidade na Extração de Dívida Total

**Problema:** Dívida Total pode incluir classificações não capturadas.

**Solução:**
- Usar `Divida_Curto_Prazo + Divida_Longo_Prazo` como proxy mais confiável
- Documentar que há diferenças e que isso é esperado

### 3. Fragilidade na Consistência dos Dados

**Problema:** Muitas inconsistências estruturais podem indicar problemas sistemáticos.

**Solução:**
- Revisar manualmente uma amostra de casos
- Ajustar o prompt do LLM para ser mais específico
- Considerar validação cruzada com dados de outras fontes

### 4. Fragilidade com Outliers

**Problema:** Muitos outliers podem distorcer análises estatísticas.

**Solução:**
- Documentar outliers
- Usar transformações (log, winsorization) na modelagem
- Considerar análises separadas por tamanho de empresa

### 5. Fragilidade com Valores Extremos

**Problema:** Alguns valores extremos podem ser erros de extração.

**Solução:**
- Revisar manualmente casos com valores fora do range esperado
- Validar com PDFs originais
- Considerar exclusão se confirmado erro

---

## Recomendações

### Imediatas

1. ✅ **Revisar manualmente os 5 casos críticos** (alta severidade)
2. ✅ **Validar valores extremos** (ex: Rede D'Or com dívida de R$ 649 bilhões)
3. ✅ **Documentar inconsistências** para referência futura

### Curto Prazo

1. **Ajustar cálculos de indicadores:**
   - Usar `Ativo_Total` como referência principal
   - Usar `Divida_CP + Divida_LP` como proxy de Dívida Total
   - Validar consistência antes de calcular indicadores

2. **Tratar outliers:**
   - Documentar outliers
   - Usar transformações na modelagem
   - Considerar análises por segmento

3. **Melhorar extração (se necessário):**
   - Revisar prompt do LLM
   - Adicionar validações mais específicas
   - Considerar extração em duas etapas (validação + correção)

### Longo Prazo

1. **Validação cruzada:**
   - Comparar com dados de outras fontes (ex: CVM, Economatica)
   - Validar amostra representativa manualmente

2. **Melhorias no pipeline:**
   - Adicionar mais validações automáticas
   - Implementar correções automáticas quando possível
   - Criar dashboard de qualidade dos dados

---

## Conclusão

Os dados extraídos são **utilizáveis para modelagem**, mas requerem atenção em alguns aspectos:

- ✅ **Completude excelente:** Todos os campos críticos preenchidos
- ⚠️ **Inconsistências estruturais:** Comuns, mas não críticas para modelagem
- ⚠️ **Outliers:** Esperados e tratáveis estatisticamente
- ❌ **Casos críticos:** Requerem revisão manual

**Recomendação final:** Proceder com a modelagem, mas:
1. Revisar manualmente os 5 casos críticos
2. Usar proxies mais confiáveis (ex: `Divida_CP + Divida_LP` ao invés de `Divida_Total`)
3. Documentar todas as inconsistências
4. Aplicar transformações estatísticas apropriadas para outliers

---

## Arquivos Gerados

- `validation_issues.csv`: Lista completa de 233 problemas
- `validation_summary.json`: Resumo estatístico
- `validation_report.md`: Relatório em Markdown
- `financial_data_validation_analysis.md`: Este documento (análise detalhada)

