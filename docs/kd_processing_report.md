# Relatório de Processamento de Kd

**Data:** 29 de novembro de 2025
**Arquivo processado:** `emp_e_fin_novo_mercado_20250920.xlsx`

---

## 1. Resumo Executivo

- **Total de registros processados:** 937
- **Kd calculado:** 611 (65.2%)
- **Kd válido:** 599 (63.9%)
- **Kd não calculado:** 326 (34.8%)

## 2. Metodologia de Cálculo

### 2.1 Fórmula de Kd

O Kd (custo de capital de dívida) foi calculado conforme a literatura:

```
Kd = Indexador_Base + Spread
```

Onde:
- **Indexador_Base**: Valor de referência do indexador em 2024
- **Spread**: Margem adicional extraída do texto do indexador

### 2.2 Valores de Referência dos Indexadores (2024)

| Indexador | Valor Base (% a.a.) | Fonte/Nota |
|-----------|---------------------|------------|
| CDI | 13,65% | Média 2024 |
| DI | 13,65% | Similar ao CDI |
| TLP | 6,50% | Taxa de Longo Prazo (BNDES) |
| TJLP | 6,50% | Taxa antiga, substituída por TLP |
| IPCA | 4,62% | Inflação projetada 2024 |
| TR | 0,01% | Taxa Referencial (quase em desuso) |
| SELIC | 10,50% | Taxa básica de juros |
| Pré-fixado | - | Taxa já é o Kd final |

### 2.3 Processamento de Indexadores

1. **Extração de tipo**: Identificação do indexador usando padrões regex
2. **Extração de spread**: Identificação do spread (margem) no texto
3. **Identificação de período**: Verificação se taxa é anual (a.a.) ou mensal (a.m.)
4. **Conversão**: Taxas mensais convertidas para anuais usando `(1 + taxa_mensal)^12 - 1`
5. **Cálculo de Kd**: Aplicação da fórmula Kd = Base + Spread
6. **Validação**: Verificação se Kd está em range razoável (0% a 50% a.a.)

## 3. Estatísticas de Padronização

### 3.1 Distribuição de Indexadores

| Indexador | Quantidade | % do Total |
|-----------|-----------|------------|
| CDI | 343 | 36.6% |
| NÃO_IDENTIFICADO | 326 | 34.8% |
| IPCA | 94 | 10.0% |
| TLP | 72 | 7.7% |
| TR | 46 | 4.9% |
| DI | 45 | 4.8% |
| SELIC | 11 | 1.2% |

## 4. Distribuição de Kd Calculado

### 4.1 Estatísticas Descritivas

| Estatística | Valor (% a.a.) |
|------------|----------------|
| Média | 13.60 |
| Mediana | 14.95 |
| Desvio Padrão | 4.81 |
| Mínimo | 0.01 |
| Máximo | 41.97 |
| Q1 (25%) | 9.98 |
| Q3 (75%) | 16.08 |

### 4.2 Distribuição por Indexador

| Indexador | Kd Médio | Kd Mediano | Qtd. Calculados |
|----------|----------|------------|-----------------|
| CDI | 19.38% | 15.85% | 343 |
| IPCA | 9.16% | 9.15% | 94 |
| TLP | 9.05% | 8.75% | 72 |
| TR | 6.61% | 8.06% | 46 |
| DI | 20.52% | 15.55% | 45 |
| SELIC | 13.77% | 12.30% | 11 |

## 5. Casos Especiais e Tratamentos

### 5.1 Indexadores Não Identificados

Total: 326 registros (34.8%)

Principais razões:
- Formatos não padronizados
- Indexadores raros ou específicos
- Textos incompletos ou mal formatados
- Múltiplos indexadores no mesmo texto

### 5.2 Kd Fora do Range Válido

Total: 12 registros

Kd inválidos geralmente ocorrem por:
- Spreads extremos (muito altos ou negativos)
- Erros na extração de valores
- Indexadores com valores base incorretos

## 6. Qualidade dos Dados

- **Valores consolidados preenchidos:** 905 (96.6%)
- **Valores consolidados = 0:** 57 (6.1%)

## 7. Recomendações

### 7.1 Melhorias na Padronização

1. **Revisão manual** dos 326 indexadores não identificados
2. **Expansão de padrões regex** para capturar mais variações
3. **Tratamento de casos especiais**: faixas de taxa, múltiplos indexadores
4. **Validação cruzada** com dados de mercado quando disponível

### 7.2 Uso dos Dados

1. **Filtrar por Kd válido** para análises principais
2. **Revisar casos extremos** (Kd muito alto ou muito baixo)
3. **Considerar valores consolidados = 0** como financiamentos quitados ou não aplicáveis
4. **Agrupar por tipo de indexador** para análises comparativas

## 8. Referências Metodológicas

- ASSAF NETO, Alexandre. **Finanças Corporativas e Valor**. 6. ed. São Paulo: Atlas, 2014.
- DAMODARAN, Aswath. **Investment Valuation: Tools and Techniques for Determining the Value of Any Asset**. 3. ed. Hoboken: Wiley, 2012.

---

*Relatório gerado automaticamente pelo script `src/utils/generate_kd_report.py`*